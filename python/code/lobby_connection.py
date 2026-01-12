import requests
import json
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder
import os
import sys
from pathlib import Path
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def print_callback(topic, payload, **kwargs):
    print(f"Received message on topic {topic}: {payload}")

def create_lobby(lobby_name, passcode, pit_stop_settings, callback=print_callback, **additional_fields):
    """
    Create a new lobby in DynamoDB with a hashed passcode.

    Args:
        lobby_name (str): Name of the lobby
        passcode (str): Plain text passcode (will be hashed)
        pit_stop_settings (dict): Settings related to pit stops
        **additional_fields: Any additional lobby-specific fields

    Returns:
        dict: Created lobby item with lobbyId

    Raises:
        ValueError: If lobby already exists
    """
    # Create lobby item
    lobby = {
        'lobby_name': lobby_name,
        'passcode': passcode,
        'pit_stop_settings': pit_stop_settings,
    }

    lobby.update(additional_fields)

    create_lobby_url = os.getenv('CREATE_LOBBY_URL')
    response = requests.post(create_lobby_url, data=json.dumps(lobby))

    # Check if lobby creation failed
    response_data = response.json()
    if response.status_code != 201 or response_data.get('error'):
        error_msg = response_data.get('error', 'Unknown error occurred')
        raise ValueError(f"Failed to create lobby: {error_msg}")

    try:
        del pit_stop_settings['remote_pit_control_enabled']
    except KeyError:
        pass

    def callback_wrapper(topic, payload, **kwargs):
        try:
            callback(topic, payload, **kwargs)
        except Exception as e:
            logger.error(f"Command callback failed: {e}", exc_info=True)

    iot_topic_url = os.getenv('IOT_TOPIC_URL')
    if True in pit_stop_settings.values():
        subscribe_to_iot_topic(
            topic=f"{lobby_name}/commands",
            message_callback=callback_wrapper,
            endpoint=iot_topic_url,
        )

    return response_data

def join_lobby(lobby_name, passcode, pit_stop_settings, callback=print_callback,**additional_fields):
    """
    Join an existing lobby in DynamoDB with a hashed passcode to stream data.

    Args:
        lobby_name (str): Name of the lobby
        passcode (str): Plain text passcode (will be hashed),
        'pit_stop_settings': pit_stop_settings
        **additional_fields: Any additional lobby-specific fields

    Returns:
        dict: Created lobby item with lobbyId

    Raises:
        ValueError: If lobby doesn't exist or credentials are incorrect
    """
    # Create lobby item
    lobby = {
        'lobby_name': lobby_name,
        'passcode': passcode,
        'pit_stop_settings': pit_stop_settings
    }

    lobby.update(additional_fields)

    lobby_auth_url = os.getenv('LOBBY_AUTH_URL')
    response = requests.post(lobby_auth_url, data=json.dumps(lobby))

    # Check if join failed (lobby doesn't exist or wrong credentials)
    response_data = response.json()
    if response.status_code != 200 or response_data.get('error'):
        error_msg = response_data.get('error', 'Unknown error occurred')
        raise ValueError(f"Failed to join lobby: {error_msg}")

    try:
        del pit_stop_settings['remote_pit_control_enabled']
    except KeyError:
        pass

    def callback_wrapper_join(topic, payload, **kwargs):
        try:
            callback(topic, payload, **kwargs)
        except Exception as e:
            logger.error(f"Command callback failed: {e}", exc_info=True)

    iot_topic_url = os.getenv('IOT_TOPIC_URL')
    if True in pit_stop_settings.values():
        subscribe_to_iot_topic(
            topic=f"{lobby_name}/commands",
            message_callback=callback_wrapper_join,
            endpoint=iot_topic_url,
        )

    return response_data

## Websockets

# Certificate files configuration
# Use PyInstaller's temp directory when bundled, otherwise use development path
def get_cert_dir():
    if getattr(sys, 'frozen', False):
        # Running as compiled executable - use bundle directory
        base_path = Path(sys._MEIPASS)
    else:
        # Running in development - use relative path
        base_path = Path(__file__).resolve().parent.parent
    return base_path / "certificates"

CERT_DIR = get_cert_dir()

# Global MQTT connection storage (keeps connections alive)
_active_mqtt_connections = []

def subscribe_to_iot_topic(topic, message_callback, endpoint,
                           cert_path=None, key_path=None, ca_path=None):
    """
    Subscribe to an AWS IoT Core topic using MQTT.

    Args:
        topic (str): The IoT topic to subscribe to (e.g., "lobby_name/commands")
        message_callback (callable): Callback function that receives messages
            Signature: callback(topic, payload, **kwargs)
        endpoint (str): Your AWS IoT endpoint (e.g., "xxxxx.iot.eu-north-1.amazonaws.com")
        cert_path (str, optional): Path to certificate file. Defaults to CERT_DIR/cert.pem
        key_path (str, optional): Path to private key file. Defaults to CERT_DIR/private.key
        ca_path (str, optional): Path to root CA file. Defaults to CERT_DIR/AmazonRootCA1.pem

    Returns:
        tuple: (mqtt_connection, event_loop_group) - Keep these alive while subscribed

    Example:
        def on_message(topic, payload, **kwargs):
            print(f"Received on {topic}: {payload}")

        connection, elg = subscribe_to_iot_topic(
            "my_lobby/commands",
            on_message,
            "xxxxx.iot.eu-north-1.amazonaws.com"
        )

        # Keep running to receive messages
        # When done:
        # connection.disconnect()
    """
    # Set default certificate paths
    if cert_path is None:
        cert_path = str(CERT_DIR / "pit_stop_manager.cert.pem")
    if key_path is None:
        key_path = str(CERT_DIR / "pit_stop_manager.private.key")
    if ca_path is None:
        ca_path = str(CERT_DIR / "root-CA.crt")

    # Verify files exist
    for path in [cert_path, key_path, ca_path]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Certificate file not found: {path}")

    # Create event loop group (manages IO threads)
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    # Generate unique client ID
    client_id = f"iremoteengineer_{os.urandom(4).hex()}"

    # Connection callbacks for debugging
    def on_connection_interrupted(connection, error, **kwargs):
        logger.warning(f"MQTT connection interrupted: {error}")

    def on_connection_resumed(connection, return_code, session_present, **kwargs):
        logger.info(f"MQTT connection resumed")

    # Build MQTT connection
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=endpoint,
        cert_filepath=cert_path,
        pri_key_filepath=key_path,
        client_bootstrap=client_bootstrap,
        ca_filepath=ca_path,
        client_id=client_id,
        clean_session=True,
        keep_alive_secs=30,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed
    )

    logger.info(f"Connecting to AWS IoT...")
    try:
        connect_future = mqtt_connection.connect()
        connect_future.result(timeout=30)
        logger.info("Connected to AWS IoT successfully")
    except Exception as e:
        logger.error(f"MQTT connection failed: {e}")
        raise

    # Subscribe to topic
    logger.info(f"Subscribing to topic: {topic}")
    try:
        subscribe_future, _ = mqtt_connection.subscribe(
            topic=topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=message_callback
        )

        subscribe_future.result(timeout=10)
        logger.info(f"Subscribed to command topic successfully")
    except Exception as e:
        logger.error(f"MQTT subscription failed: {e}")
        mqtt_connection.disconnect()
        raise

    # Store connection to keep it alive
    connection_info = {
        'connection': mqtt_connection,
        'event_loop_group': event_loop_group,
        'topic': topic,
        'endpoint': endpoint
    }
    _active_mqtt_connections.append(connection_info)

    return mqtt_connection, event_loop_group

# def publish_to_iot_topic(mqtt_connection, topic, message):
#     """
#     Publish a message to an AWS IoT Core topic.
    
#     Args:
#         mqtt_connection: Active MQTT connection from subscribe_to_iot_topic
#         topic (str): The IoT topic to publish to
#         message (dict or str): Message to publish (dicts will be JSON encoded)
    
#     Returns:
#         Future: AWS CRT future that can be awaited
#     """
#     if isinstance(message, dict):
#         message = json.dumps(message)
    
#     publish_future, packet_id = mqtt_connection.publish(
#         topic=topic,
#         payload=message,
#         qos=mqtt.QoS.AT_LEAST_ONCE
#     )
    
#     return publish_future

def disconnect_iot(mqtt_connection):
    """
    Disconnect from AWS IoT Core.

    Args:
        mqtt_connection: Active MQTT connection to disconnect
    """
    logger.info("Disconnecting from IoT Core...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    logger.info("Disconnected from IoT Core")

def disconnect_all_iot():
    """
    Disconnect all active MQTT connections.
    Useful for cleanup when stopping the application.
    """
    global _active_mqtt_connections

    if len(_active_mqtt_connections) > 0:
        logger.info(f"Disconnecting {len(_active_mqtt_connections)} MQTT connection(s)...")

    for conn_info in _active_mqtt_connections:
        try:
            disconnect_future = conn_info['connection'].disconnect()
            disconnect_future.result(timeout=5)
        except Exception as e:
            logger.error(f"Error disconnecting MQTT: {e}")

    _active_mqtt_connections.clear()