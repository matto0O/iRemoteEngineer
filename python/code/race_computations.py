from irsdk import PitCommandMode, IRSDK
from datetime import datetime, timezone
from time import sleep
import schedule
import logging

from utils import Car, State
from kinesis_producer import KinesisProducer

logger = logging.getLogger(__name__)

kinesis_producer = KinesisProducer(debug_mode=True)

ir = IRSDK()
state = State()

# CORE

def send_data(key, value, **kwargs):
    to_send = {
        "type": key,
        "data": value,
        # "sender": state.uuid,
        "token": state.current_token
    }
    if kwargs:
        for k, v in kwargs.items():
            to_send[k] = v
    to_send["timestamp"] = get_timestamp()
    
    kinesis_producer.send_record(to_send, state.current_token)
    logger.info(f"Sent {key} ({len(str(to_send))}B).")

def run_jobs(interval=0.5):
    schedule.run_pending()
    sleep(interval)

def schedule_job(func, interval, **kwargs):
    schedule.every(interval).seconds.do(func, **kwargs)

def clear_jobs():
    schedule.clear()


# DATA INGESTION FUNCTIONS

def schedule_data_ingestion(token, intervals={}):
    state.computation_helpers["last_fuel_level"] = ir['FuelLevel']
    state.current_token = token
    get_session_info()

    function_mapping = {
        "lap_finish": post_lap_invocations,
        "relative": relative,
        "weather": weather_info,
        "incidents": new_incidents,
        "tow": is_towed,
        "tyres": tyre_data,
        "pit": check_if_in_pit
    }

    lap_based_functions = []

    for key, data in intervals.items():
        if data["enabled"] == False:
            continue
        if data["mode"] == "lap":
            lap_based_functions.append(function_mapping[key])
        elif key != "lap_finish":
            schedule_job(function_mapping[key], data["interval"])

    schedule_job(post_lap_invocations, intervals["lap_finish"]["interval"], funcs=lap_based_functions)
    get_session_info() # get session info again to get car and team data
    
def get_timestamp():
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')

def get_direction(angle=None):
    rad_to_deg = 57.296
    if angle is not None:
        angle_deg = angle
    else:
        angle_deg = ir["WindDir"] * rad_to_deg
    angle_middle = (angle_deg + 22.5) % 360

    if 0 < angle_middle < 45:
        wind_direction = "North"
    elif 45 <= angle_middle < 90:
        wind_direction = "North-East"
    elif 90 <= angle_middle < 135:
        wind_direction = "East"
    elif 135 <= angle_middle < 180:
        wind_direction = "South-East"
    elif 180 <= angle_middle < 225:
        wind_direction = "South"
    elif 225 <= angle_middle < 270:
        wind_direction = "South-West"
    elif 270 <= angle_middle < 315:
        wind_direction = "West"
    elif 315 <= angle_middle < 360:
        wind_direction = "North-West"
    else:
        wind_direction = "Unknown direction"

    return wind_direction, angle_deg

def format_lap_time(time_seconds):
    """
    Format lap time in seconds to racing format: M:SS.mmm or MM:SS.mmm

    Args:
        time_seconds: Lap time in seconds (float or int)

    Returns:
        str: Formatted lap time (e.g., "1:23.456" or "12:34.567")
             Returns "--:--.---" for invalid times (0 or -1)
    """
    if time_seconds == 0 or time_seconds == -1 or time_seconds is None:
        return "--:--.---"

    # Convert to total milliseconds for precise calculation
    total_ms = int(time_seconds * 1000)

    # Extract minutes, seconds, milliseconds
    minutes = total_ms // 60000
    remaining_ms = total_ms % 60000
    seconds = remaining_ms // 1000
    milliseconds = remaining_ms % 1000

    # Format: 1 or 2 digit minutes, always 2 digit seconds, always 3 digit milliseconds
    return f"{minutes}:{seconds:02d}.{milliseconds:03d}"

def split_time_info():
    sectors = ir['SplitTimeInfo']['Sectors']
    return {(sector['SectorNum'] + 1): round(sector["SectorStartPct"] * 100, 2) for sector in sectors}

def used_fast_repair():
    current_fast_repairs = ir["PlayerFastRepairsUsed"]
    if state.computation_helpers['fast_repairs_used'] != current_fast_repairs:
        state.computation_helpers['fast_repairs_used'] = current_fast_repairs
        send_data("fast_repair", 1)

def new_incidents():
    current_incidents = ir["PlayerCarMyIncidentCount"]
    inc_diff = current_incidents - state.computation_helpers['last_incidents']
    if inc_diff > 0:
        state.computation_helpers['last_incidents'] = current_incidents
        send_data("incidents", inc_diff)
        tyre_data()

def last_lap_data():
    """Capture fuel/incidents immediately, schedule lap time fetch for later"""
    driver_name = ir['DriverInfo']['Drivers'][ir['PlayerCarIdx']]['UserName']
    fuel_consumed = state.computation_helpers['last_fuel_level'] - ir['FuelLevel']
    incidents_incurred = ir["PlayerCarMyIncidentCount"] - state.computation_helpers['last_lap_incidents']
    state.computation_helpers['last_fuel_level'] = ir['FuelLevel']
    state.computation_helpers['last_lap_incidents'] = ir["PlayerCarMyIncidentCount"]

    pending_data = {
        "driver_name": driver_name,
        "fuel_consumed": round(fuel_consumed, 2),
        "incidents_incurred": incidents_incurred,
    }

    # Schedule sending with lap time in 5 seconds (runs once then cancels)
    schedule.every(5).seconds.do(send_lap_data_with_time, pending_data=pending_data).tag('lap_data_delayed')

def send_lap_data_with_time(pending_data):
    """Send lap data with the now-updated lap time"""
    lap_data = {
        **pending_data,
        "lap_time": format_lap_time(ir['LapLastLapTime'])
    }
    send_data("lap_history", lap_data)

    return schedule.CancelJob

def get_speed():
    return ir['WindVel'] * 3.6

def weather_info():
    wind_direction, angle = get_direction(ir['WindDir'] * 57.296)
    
    wetness_map = {
        1: "Dry",
        2: "Mostly dry",
        3: "Very lightly wet",
        4: "Lightly wet",
        5: "Moderately wet",
        6: "Very wet",
        7: "Extremely wet"
    }
    track_wetness = wetness_map.get(ir['TrackWetness'], "Unknown wetness")
    
    declared_wet = ir['WeatherDeclaredWet']
    speed = get_speed()
    
    weather_data = {
        "air_temp": round(ir['AirTemp'], 1),
        "track_temp": round(ir['TrackTempCrew'], 1),
        "wind_speed": round(speed, 1),
        "wind_direction": f"{wind_direction} ({angle:.1f}°)",
        "track_wetness": track_wetness,
        "precipitation": round(float(ir['Precipitation']), 1), 
        "declared_wet": declared_wet,
    }
    send_data("weather", weather_data)

def tyre_data():
    def get_tyre_data(prefix):
        return {
            "left_carcass_temp": round(ir[f"{prefix}tempCL"], 1),
            "middle_carcass_temp": round(ir[f"{prefix}tempCM"],1),
            "right_carcass_temp": round(ir[f"{prefix}tempCR"], 1),
            "left_tread_remaning": round(ir[f"{prefix}wearL"] * 100, 1),
            "middle_tread_remaning": round(ir[f"{prefix}wearM"] * 100, 1),
            "right_tread_remaning": round(ir[f"{prefix}wearR"] * 100, 1)
        }

    tyres = {
        "front_left": get_tyre_data("LF"),
        "front_right": get_tyre_data("RF"),
        "rear_left": get_tyre_data("LR"),
        "rear_right": get_tyre_data("RR")
    }

    if tyres != state.computation_helpers['tyres']:
        send_data("tyres", tyres)
        state.computation_helpers['tyres'] = tyres

def relative():
    ir.freeze_var_buffer_latest()
    
    # Get all driver data once
    drivers = ir['DriverInfo']['Drivers']
    my_car_idx = ir['PlayerCarIdx']
    
    # Use list comprehension for better performance
    all_cars = [
        Car(car['CarIdx'], car['CarNumber'], car['UserName'], car['CarID'],
            car['CarClassID'], car['TeamName'],
            car['IRating'], car['LicString']) for car in drivers
    ]
    all_cars.sort(key=lambda x: x.idx)

    # Get all arrays at once to minimize data access overhead
    their_position = ir['CarIdxPosition']
    their_lap = ir['CarIdxLap']
    their_distance_pct = ir['CarIdxLapDistPct']
    their_est_time = ir["CarIdxEstTime"]
    their_class_position = ir["CarIdxClassPosition"]
    them_pit_road = ir['CarIdxOnPitRoad']
    their_gap_leader = ir['CarIdxF2Time']
    their_last_lap = ir['CarIdxLastLapTime']

    ir.unfreeze_var_buffer_latest()
    # Format last lap time once for each car
    car_data = []
    for car, position, dist_pct, in_pit, lap, est_time, class_pos, gap_leader, last_lap in zip(
            all_cars, their_position, their_distance_pct, them_pit_road,
            their_lap, their_est_time, their_class_position, their_gap_leader, their_last_lap):

        car_data.append({
            "user_name": car.user_name,
            "team_name": car.team_name,
            "class_id": car.class_id,
            "car_model_id": car.car_model_id,
            "car_number": car.car_number,
            "car_class_position": class_pos,
            "gap_leader": round(gap_leader, 3),
            "car_position": position,
            # "car_est_time": round(est_time, 3),
            "distance_pct": round(dist_pct, 3),
            "in_pit": in_pit,
            "lap": lap,
            "car_lap_last_time": format_lap_time(last_lap)
        })

    changed_data = {}
    # Initial full update
    if state.computation_helpers['cars'] == {}:
        for car in car_data:
            car_number = car['car_number']
            state.computation_helpers['cars'][car_number] = car
        send_data("cars", state.computation_helpers['cars'], full_update=True)

    # Compare with previous state and send only changed fields
    else:
        for car in car_data:
            car_number = car['car_number']
            changed_fields = {}
            if car_number in state.computation_helpers['cars']:
                car_info = state.computation_helpers['cars'][car_number]
                for key, value in car.items():
                    if car_info.get(key, None) != value:
                        changed_fields[key] = value
            else:
                changed_fields = car

            if changed_fields:
                changed_data[car_number] = changed_fields
            state.computation_helpers['cars'][car_number] = car

        if changed_data:
            send_data("cars", changed_data)

    state.session_info["team_name"] = all_cars[my_car_idx].team_name
    state.session_info["player_car_number"] = all_cars[my_car_idx].car_number
    state.session_info["car_model_id"] = all_cars[my_car_idx].car_model_id

    return changed_data

def check_if_in_pit():
    in_pit = ir['OnPitRoad']
    if state.computation_helpers['in_pit'] != in_pit:
        state.computation_helpers['in_pit'] = in_pit

        if in_pit:
            send_data("pit_stop", "Entered the pit lane")
        else:
            state.computation_helpers['last_fuel_level'] = ir['FuelLevel']
            # Don't update last_lap here - let lap_finished() handle it
            used_fast_repair()

            send_data("pit_stop", "Left the pit lane")

def fuel_data():
    send_data("fuel", {"fuel_level": round(ir['FuelLevel'], 2)})

def lap_finished():
    new_lap = ir['Lap']
    if new_lap is None or new_lap == 0:
        return False
    # Handle lap number increases (normal finish or skip due to pit entry)
    if new_lap > state.computation_helpers['last_lap']:
        state.computation_helpers['last_lap'] = new_lap
        return True
    return False

def post_lap_invocations(funcs=[]):
    if lap_finished():
        get_session_info()
        fuel_data()
        last_lap_data()
        for func in funcs:
            func()

def get_session_info():
    weekend_info = ir['WeekendInfo']
    session_info = ir['SessionInfo']
    data = {
        "series_id": weekend_info['SeriesID'],
        "session_id": weekend_info['SessionID'],
        "subsession_id": weekend_info['SubSessionID'],
        "event_type": weekend_info['EventType'], # typ lobby
        "session_type": session_info.get("SessionName", weekend_info['EventType']), # jedna z trzech sesji w lobby
        "track_name": weekend_info['TrackDisplayName'],
        "track_config": weekend_info['TrackConfigName'],
        "split_time_info": split_time_info(),
        "car_model_id": state.session_info.get("car_model_id", None),
        "team_name": state.session_info.get("team_name", None),
        "player_car_number": state.session_info.get("player_car_number", None)
    }
    for key in ["series_id", "session_id", "subsession_id", "track_name", "track_config", "event_type"]:
        if data[key] != state.session_info[key]:
            logger.info(f"New session: {data['track_name']} - {data['event_type']}")
            state.reset_state()
            state.session_info.update(data)
            send_data("session_info", data, reset=True)
            return
    if data["session_type"] != state.session_info["session_type"]:
        logger.info(f"Session changed to: {data['session_type']}")
        send_data("session_info", data)

# TODO incorporate below

def in_the_car():
    if ir["IsOnTrack"] != state.computation_helpers["in_car"]:
        state.computation_helpers["in_car"]
        send_data('in_car', 
            {
                "user_in_car": ir["IsOnTrack"],
                "any_driver_in_car": ir["IsOnTrackCar"]
            }
        )

    return ir["IsOnTrack"]

def is_towed():
    tow_time = ir["PlayerCarTowTime"]
    if tow_time > 0 and not state.computation_helpers["being_towed"]:
        # just started towing
        state.computation_helpers["being_towed"] = True
        send_data("tow", tow_time)
    elif tow_time == 0 and state.computation_helpers["being_towed"]:
        # finished towing
        state.computation_helpers["being_towed"] = False
        send_data("tow", 0)
    return tow_time > 0

def fast_repairs_left():
    pass

def execute_commands(topic, payload, **kwargs):
    # Decode payload if it's bytes
    if isinstance(payload, bytes):
        try:
            payload = payload.decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to decode command payload: {e}")
            return

    # Parse JSON payload
    try:
        import json
        payload_data = json.loads(payload)
        command_string = payload_data.get('command', '')
    except json.JSONDecodeError as e:
        logger.error(f"Invalid command JSON: {e}")
        # Fallback: treat payload as plain text command
        command_string = payload if isinstance(payload, str) else str(payload)

    if kwargs.get("debug", False):
        logger.debug(f"Debug mode - Commands: {command_string}")
        return

    commands = command_string.split(" ")

    executed = ["clear"]
    ir.pit_command(PitCommandMode.clear)

    # Command mapping for better performance
    command_map = {
        "lf": PitCommandMode.lf,
        "rf": PitCommandMode.rf,
        "lr": PitCommandMode.lr,
        "rr": PitCommandMode.rr,
        "fr": PitCommandMode.fr,
        "ws": PitCommandMode.ws,
        "clear_ws": PitCommandMode.clear_ws,
        "clear_fr": PitCommandMode.clear_fr,
        "clear_fuel": PitCommandMode.clear_fuel,
    }

    for command in commands:
        if command in command_map:
            ir.pit_command(command_map[command])
            executed.append(command)
        elif "fuel" in command:
            try:
                fuel = int(command.split(".")[1])
                ir.pit_command(PitCommandMode.fuel, fuel)
                executed.append(f"fuel.{fuel}")
            except (ValueError, IndexError):
                logger.error(f"Invalid fuel command: {command}")
        elif "tc" in command:
            try:
                tc = int(command.split(".")[1])
                logger.warning(f"TC command not yet implemented: {tc}")
                #ir.pit_command(PitCommandMode., tc) # TODO cannot solve, need to use macros for tc
            except (ValueError, IndexError):
                logger.error(f"Invalid tyre change command: {command}")
        else:
            logger.warning(f"Unknown command: {command}")

    logger.info(f"Pit commands executed: {', '.join(executed)}")

    event = {
        "type": "command",
        "description": f"Executed commands: {', '.join(executed)}",
        "time": datetime.now(timezone.utc).strftime('%H:%M:%S')
    }
    send_data("event", event)