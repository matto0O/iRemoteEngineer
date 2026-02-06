from time import sleep
import threading
import requests
import logging
import os

from race_computations import (
    schedule_data_ingestion,
    run_jobs,
    ir,
    state,
    clear_jobs,
    execute_commands,
)
from lobby_connection import (
    create_lobby as _create_lobby,
    join_lobby as _join_lobby,
    disconnect_all_iot,
)
from gui.data_settings_tab import load_intervals

logger = logging.getLogger(__name__)


class StreamingThreadController:
    ir_heartbeat_thread: threading.Thread = None
    job_thread: threading.Thread = None
    stop_threads: bool = False
    token: str = None

    @staticmethod
    def stop_all_threads():
        """Stop all streaming threads with timeout"""
        logger.info("Stopping streaming...")
        StreamingThreadController.stop_threads = True

        # Clear any scheduled jobs
        clear_jobs()

        # Wait for threads with timeout
        if (
            StreamingThreadController.job_thread is not None
            and StreamingThreadController.job_thread.is_alive()
        ):
            StreamingThreadController.job_thread.join(timeout=2.0)
            if StreamingThreadController.job_thread.is_alive():
                logger.warning("Job thread did not terminate within timeout")

        if (
            StreamingThreadController.ir_heartbeat_thread is not None
            and StreamingThreadController.ir_heartbeat_thread.is_alive()
        ):
            StreamingThreadController.ir_heartbeat_thread.join(timeout=2.0)
            if StreamingThreadController.ir_heartbeat_thread.is_alive():
                logger.warning("Heartbeat thread did not terminate within timeout")

        # Reset threads
        StreamingThreadController.job_thread = None
        StreamingThreadController.ir_heartbeat_thread = None
        StreamingThreadController.stop_threads = False

        # Shutdown iRacing connection
        if ir.is_connected:
            ir.shutdown()
            state.ir_connected = False

        _stop_streaming_reset_uuid(StreamingThreadController.token)

        # Reset tokens to ensure clean state
        StreamingThreadController.token = None
        state.current_token = None

        logger.info("Streaming stopped")

    def are_threads_running():
        """Check if streaming threads are running"""
        return (
            StreamingThreadController.job_thread is not None
            and StreamingThreadController.job_thread.is_alive()
        )


def _check_iracing(test_file=None):
    if state.ir_connected and not (ir.is_initialized and ir.is_connected):
        state.ir_connected = False
        state.last_car_setup_tick = -1
        ir.shutdown()
        return False
    elif state.ir_connected and (ir.is_initialized and ir.is_connected):
        return True
    elif (
        not state.ir_connected
        and ir.startup(test_file=test_file)
        and ir.is_initialized
        and ir.is_connected
    ):
        state.ir_connected = True
    return False


def _check_heartbeat(test_file=None):
    while not StreamingThreadController.stop_threads and _check_iracing(
        test_file=test_file
    ):
        sleep(1)
    # Don't call stop_all_threads here to avoid recursion
    logger.info("iRacing connection lost")


def _check_if_can_stream_to(token):
    start_stop_url = os.getenv("UUID_EDIT_URL")

    body = {"token": token}

    response = requests.patch(start_stop_url, body)
    result = response.status_code in [200, 201]
    if not result:
        logger.warning(f"Token validation failed - {response.text}")
    return result, response


def _stop_streaming_reset_uuid(token):
    start_stop_url = os.getenv("UUID_EDIT_URL")

    body = {"token": token}

    disconnect_all_iot()
    requests.delete(start_stop_url, data=body)
    state.reset_token()
    state.reset_state()


def _start_threads(token, test_file=None):
    def job_thread_func(stop_event):
        intervals = load_intervals()
        schedule_data_ingestion(token, intervals=intervals)
        logger.info("Data streaming started")
        while not stop_event():
            run_jobs(interval=0.5)

    logger.info("Waiting for iRacing connection...")
    while not _check_iracing(test_file):
        sleep(0.5)

    logger.info("iRacing connected")


    can_stream_to, status_code = _check_if_can_stream_to(token)
    if can_stream_to:
        StreamingThreadController.job_thread = threading.Thread(
            target=job_thread_func,
            args=(lambda: StreamingThreadController.stop_threads,),
            daemon=True,
        )

        StreamingThreadController.ir_heartbeat_thread = threading.Thread(
            target=_check_heartbeat, args=(test_file,), daemon=True
        )

        StreamingThreadController.job_thread.start()
        StreamingThreadController.ir_heartbeat_thread.start()

    elif status_code.status_code == 409:
        raise Exception("Lobby is currently being streamed to")
    else:
        raise Exception("Failed to validate streaming token")


def create_lobby_and_stream(
    lobby_name: str, passcode: str, pit_stop_settings: dict, test_file=None
):
    logger.info(f"Creating lobby: {lobby_name}")
    response = _create_lobby(
        lobby_name=lobby_name,
        passcode=passcode,
        pit_stop_settings=pit_stop_settings,
        callback=execute_commands,
    )
    token = response.get("token", None)

    if token is None:
        logger.error("Failed to create lobby - no token received")
        raise ValueError("Failed to create lobby and obtain token")

    _start_threads(token, test_file=test_file)
    StreamingThreadController.token = token
    logger.info(f"Lobby '{lobby_name}' created successfully")


def join_lobby_and_stream(
    lobby_name: str, passcode: str, pit_stop_settings: dict, test_file=None
):
    logger.info(f"Joining lobby: {lobby_name}")
    response = _join_lobby(
        lobby_name=lobby_name,
        passcode=passcode,
        pit_stop_settings=pit_stop_settings,
        callback=execute_commands,
    )
    token = response.get("token", None)

    if token is None:
        logger.error("Failed to join lobby - no token received")
        raise ValueError("Failed to join lobby and obtain token")

    _start_threads(token, test_file=test_file)
    StreamingThreadController.token = token
    logger.info(f"Joined lobby '{lobby_name}' successfully")
