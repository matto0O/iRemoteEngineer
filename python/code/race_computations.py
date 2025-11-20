from threading import Lock
from irsdk import PitCommandMode, IRSDK
from datetime import datetime, timezone
import numpy as np
from time import sleep

from utils import Car, State
from kinesis_producer import KinesisProducer

import schedule

kinesis_producer = KinesisProducer()

ir = IRSDK()
state = State()

kinesis_json = {}

data_lock = Lock()

def get_json_template():
    return kinesis_json.copy()

def send_data(lobby_name, key, value):
    to_send = get_json_template()
    to_send["type"] = key
    to_send["data"] = value
    to_send["timestamp"] = get_timestamp()

    kinesis_producer.send_record(to_send, lobby_name)

def run_jobs(interval=0.5):
    schedule.run_pending()
    sleep(interval)

def schedule_job(func, interval, lobby_name):
    schedule.every(interval).seconds.do(func, lobby_name=lobby_name)

def schedule_data_ingestion(lobby_name, team_name):
    set_constants(lobby_name, team_name)

    schedule_job(post_lap_invocations, 1, lobby_name)
    schedule_job(relative, 5, lobby_name)
    schedule_job(weather_info, 30, lobby_name)

    schedule_job(check_if_in_pit, 1, lobby_name)
    schedule_job(new_incidents, 5, lobby_name)

def set_constants(lobby_name, team_name):
    kinesis_json["lobby_name"] = lobby_name
    kinesis_json["team_name"] = team_name
    
def get_timestamp():
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')

def get_direction(angle=None):
    rad_to_deg = 57.296
    if angle is not None:
        angle_deg = angle
    else:
        angle_deg = ir["WindDir"] * rad_to_deg
    angle_middle = angle_deg + 22.5

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

def split_time_info():
    sectors = ir['SplitTimeInfo']['Sectors']
    return {(sector['SectorNum'] + 1): round(sector["SectorStartPct"] * 100, 2) for sector in sectors}

def used_fast_repair(lobby_name):
    current_fast_repairs = ir["PlayerFastRepairsUsed"]
    if state.computation_helpers['fast_repairs_used'] != current_fast_repairs:
        state.computation_helpers['fast_repairs_used'] = current_fast_repairs
        send_data(lobby_name, "fast_repair", current_fast_repairs)

def new_incidents(lobby_name):
    current_incidents = ir["PlayerCarMyIncidentCount"]
    inc_diff = current_incidents - state.computation_helpers['incidents']
    if inc_diff > 0:
        state.computation_helpers['incidents'] = current_incidents
        send_data(lobby_name, "incidents", current_incidents)
        tyre_data(lobby_name)

def get_speed():
    return ir['WindVel'] * 3.6

def weather_info(lobby_name):
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

    send_data(lobby_name, "weather_data", weather_data)

def tyre_data(lobby_name):
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

    send_data(lobby_name, "tyres", tyres)

def relative(lobby_name):
    ir.freeze_var_buffer_latest()
    
    # Get all driver data once
    drivers = ir['DriverInfo']['Drivers']
    my_car_idx = ir['PlayerCarIdx']
    
    # Use list comprehension for better performance
    all_cars = [
        Car(car['CarIdx'], car['CarNumber'], car['UserName'], car['CarID'],
            car['CarClassID'], car['CarScreenNameShort'], car['TeamName'],
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

        # Format last lap time efficiently
        if last_lap > 0:
            minutes = int(last_lap / 60)
            seconds = int(last_lap % 60)
            milliseconds = int((last_lap % 1) * 1000)
            formatted_last_lap = f"{minutes}:{seconds:02d}.{milliseconds:03d}"
        else:
            formatted_last_lap = "--:--:---"
            
        car_data.append({
            "user_name": car.user_name,
            "team_name": car.team_name,
            "class_id": car.class_id,
            "car_model_id": car.car_model_id,
            "car_number": car.car_number,
            "car_class_position": class_pos,
            "gap_leader": round(gap_leader, 3),
            "car_position": position,
            "car_est_time": round(est_time, 3),
            "distance_pct": round(dist_pct, 3),
            "in_pit": in_pit,
            "lap": lap,
            "last_lap": formatted_last_lap,
        })

    send_data(lobby_name, "cars", car_data)
    state.session_info["team_name"] = all_cars[my_car_idx].team_name
    state.session_info["player_car_number"] = all_cars[my_car_idx].car_number
    state.session_info["car_name"] = all_cars[my_car_idx].car_model_id

    return car_data

def check_if_in_pit(lobby_name):
    in_pit = ir['OnPitRoad']
    if state.computation_helpers['in_pit'] != in_pit:
        state.computation_helpers['in_pit'] = in_pit

        if in_pit:
            event = {
                        "type": "pit_stop",
                        "description": "Entered the pit lane"
                    }
            send_data(lobby_name, "event", event)
        else:
            state.computation_helpers['last_fuel_level'] = ir['FuelLevel']
            state.computation_helpers['last_lap'] = ir['Lap']
            used_fast_repair(lobby_name)

            event = {
                        "type": "pit_stop",
                        "description": "Left the pit lane"
                    }
            send_data(lobby_name, "event", event)

def fuel_data(lobby_name):
    send_data(lobby_name, "fuel", {"fuel_level": round(ir['FuelLevel'], 2)})

def lap_finished():
    new_lap = ir['Lap']
    if new_lap is None or new_lap == 0:
        return False
    if new_lap == state.computation_helpers['last_lap'] + 1:
        state.computation_helpers['last_lap'] = new_lap
        return True
    state.computation_helpers['last_lap'] = new_lap
    return False

def post_lap_invocations(lobby_name):
    if lap_finished():
        get_session_info(lobby_name)
        fuel_data(lobby_name)
        tyre_data(lobby_name)

def get_session_info(lobby_name):
    weekend_info = ir['WeekendInfo']
    session_info = {
        "session_id": weekend_info['SessionID'],
        "subsession_id": weekend_info['SubSessionID'],
        "track_name": weekend_info['TrackDisplayName'],
        "track_config": weekend_info['TrackConfigName'],
        "split_time_info": split_time_info()
    }
    if session_info != state.session_info:
        for key, value in session_info.items():
            state.session_info[key] = value
        print("New session detected:", session_info)
        send_data(lobby_name, "session_info", session_info)

# def execute_commands(text):
#     commands = text.split(" ")
#     executed = ["clear"]
#     ir.pit_command(PitCommandMode.clear)
    
#     # Command mapping for better performance
#     command_map = {
#         "lf": PitCommandMode.lf,
#         "rf": PitCommandMode.rf,
#         "lr": PitCommandMode.lr,
#         "rr": PitCommandMode.rr,
#         "fr": PitCommandMode.fr,
#         "ws": PitCommandMode.ws,
#         "clear_ws": PitCommandMode.clear_ws,
#         "clear_fr": PitCommandMode.clear_fr,
#         "clear_fuel": PitCommandMode.clear_fuel,
#     }
    
#     for command in commands:
#         if command in command_map:
#             ir.pit_command(command_map[command])
#             executed.append(command)
#         elif "fuel" in command:
#             try:
#                 fuel = int(command.split(".")[1])
#                 ir.pit_command(PitCommandMode.fuel, fuel)
#                 executed.append(f"fuel.{fuel}")
#             except (ValueError, IndexError):
#                 print(f"Invalid fuel command: {command}")
#         elif "tc" in command:
#             try:
#                 tc = int(command.split(".")[1])
#                 # ir.pit_command(PitCommandMode., tc) # TODO cannot solve, need to use macros for tc
#             except (ValueError, IndexError):
#                 print(f"Invalid tyre change command: {command}")
#         else:
#             print(f"Unknown command: {command}")

#     current_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
#     with data_lock:
#         shared_data_json["event"].append({
#             "type": "command",
#             "description": f"Executed commands: {', '.join(executed)}",
#             "time": current_time,
#         })
