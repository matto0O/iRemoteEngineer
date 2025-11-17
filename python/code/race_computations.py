from threading import Lock
from irsdk import PitCommandMode, IRSDK
from datetime import datetime, timezone
import numpy as np

from utils import Car, State


ir = IRSDK()
state = State()

shared_data_json = {
    "session_info": {},
    "cars": [],
    "fuel_analysis": {},
    "sectors": {},
    "weather": {},
    "tyres": {
        "front_left": {},
        "front_right": {},
        "rear_left": {},
        "rear_right": {}
    },
    "events": [],
    "total_incidents": 0,
    "fast_repairs_used": 0,
}

data_lock = Lock()

def get_data():
    split_time_info()
    weather_info()
    tyre_data()
    relative()
    check_if_in_pit()
    new_incidents()
    update_fuel_data(fuel_consumption=state.computation_helpers.get('fuel_consumption_queue', None))
    used_fast_repair()
    set_timestamp()
    return shared_data_json

def set_timestamp():
    with data_lock:
        shared_data_json["session_info"]["timestamp"] = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')

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
    with data_lock:
        sectors = ir['SplitTimeInfo']['Sectors']
        shared_data_json["sectors"] = {(sector['SectorNum'] + 1): sector["SectorStartPct"] * 100 for sector in sectors}

def used_fast_repair():
    current_fast_repairs = ir["PlayerFastRepairsUsed"]
    if state.computation_helpers['fast_repairs_used'] != current_fast_repairs:
        state.computation_helpers['fast_repairs_used'] = current_fast_repairs
        current_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        with data_lock:
            shared_data_json["fast_repairs_used"] = current_fast_repairs
            shared_data_json["events"].append({
                "type": "pit_stop",
                "description": "Used fast repair",
                "time": current_time,
            })

def new_incidents():
    current_incidents = ir["PlayerCarMyIncidentCount"]
    inc_diff = current_incidents - state.computation_helpers['incidents']
    if inc_diff > 0:
        state.computation_helpers['incidents'] = current_incidents
        current_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        with data_lock:
            shared_data_json["total_incidents"] = current_incidents
            shared_data_json["events"].append({
                "type": "incident",
                "description": f"Incurred {inc_diff}x incident",
                "time": current_time,
            })

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
    current_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

    with data_lock:
        # Update weather data
        shared_data_json["weather"] = {
            "air_temp": round(ir['AirTemp'], 1),
            "track_temp": round(ir['TrackTempCrew'], 1),
            "wind_speed": round(speed, 1),
            "wind_direction": f"{wind_direction} ({angle:.1f}°)",
            "track_wetness": track_wetness,
            "precipitation": round(float(ir['Precipitation']), 1), 
            "declared_wet": declared_wet,
        }

        # Check for track state change
        if declared_wet != state.computation_helpers['track_state']:
            event_description = f"Track state changed - {"Wet" if declared_wet else "Dry"}"
            shared_data_json["events"].append({
                "type": "weather",
                "time": current_time,
                "description": event_description,
            })
            state.computation_helpers['track_state'] = declared_wet

        # Check for wind direction change
        if wind_direction != state.computation_helpers['wind_direction']:
            event_description = f"Wind direction changed from {state.computation_helpers['wind_direction']} to {wind_direction}"
            state.computation_helpers['wind_direction'] = wind_direction
            shared_data_json["events"].append({
                "type": "weather",
                "time": current_time,
                "description": event_description,
            })

        # Check for wind speed change
        if state.computation_helpers['wind_speed'] is None or abs(speed - state.computation_helpers['wind_speed']) > 5:
            event_description = f"Wind speed changed significantly to {speed:.2f}"
            state.computation_helpers['wind_speed'] = speed
            shared_data_json["events"].append({
                "type": "weather",
                "time": current_time,
                "description": event_description,
            })

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

    with data_lock:
        shared_data_json["tyres"]["front_left"] = get_tyre_data("LF")
        shared_data_json["tyres"]["front_right"] = get_tyre_data("RF")
        shared_data_json["tyres"]["rear_left"] = get_tyre_data("LR")
        shared_data_json["tyres"]["rear_right"] = get_tyre_data("RR")

def relative():
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

    with data_lock:
        shared_data_json["cars"] = car_data
        state.session_info["team_name"] = all_cars[my_car_idx].team_name
        state.session_info["player_car_number"] = all_cars[my_car_idx].car_number
        state.session_info["car_name"] = all_cars[my_car_idx].car_model_id

def check_if_in_pit():
    in_pit = ir['OnPitRoad']
    if state.computation_helpers['in_pit'] != in_pit:
        state.computation_helpers['in_pit'] = in_pit
        current_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

        if in_pit:
            with data_lock:
                shared_data_json["events"].append({
                    "type": "pit_stop",
                    "description": "Entered the pit lane",
                    "time": current_time,
                })
        else:
            state.computation_helpers['last_fuel_level'] = ir['FuelLevel']
            state.computation_helpers['last_lap'] = ir['Lap']
            used_fast_repair()

            with data_lock:
                shared_data_json["events"].append({
                    "type": "pit_stop",
                    "description": "Left the pit lane",
                    "time": current_time,
                })

def update_fuel_data(fuel_consumption=None):
    fuel_left = ir['FuelLevel']
    if state.computation_helpers['last_fuel_level'] == -1.0:
        state.computation_helpers['last_fuel_level'] = fuel_left
        return
    
    fuel_delta = state.computation_helpers['last_fuel_level'] - fuel_left
    state.computation_helpers['last_fuel_level'] = fuel_left
    fuel_consumption.put(fuel_delta)

    # Use np.mean only on the actual data to avoid zeros
    if fuel_consumption.size > 0:
        fuel_delta_avg = np.mean(fuel_consumption.queue[:fuel_consumption.size])
    else:
        fuel_delta_avg = 0
        
    last_fuel_delta = fuel_consumption.last()

    # Avoid unnecessary calculations if fuel delta is zero
    if fuel_delta_avg > 0:
        full_laps_on_tank_from_avg = int(fuel_left / fuel_delta_avg)
        omlavg = full_laps_on_tank_from_avg + 1
        ollavg = max(1, full_laps_on_tank_from_avg - 1)
        one_more_from_avg = fuel_left / omlavg
        one_less_from_avg = fuel_left / ollavg
    else:
        full_laps_on_tank_from_avg = 0
        omlavg = 0
        ollavg = 0
        one_more_from_avg = 0
        one_less_from_avg = 0
    
    # Avoid division by zero
    if last_fuel_delta > 0:
        full_laps_on_tank_from_last = int(fuel_left / last_fuel_delta)
        target_laps_last_consumption = fuel_left / full_laps_on_tank_from_last
    else:
        full_laps_on_tank_from_last = 0
        target_laps_last_consumption = 0

    fuel_analysis_dict = {
        "fuel_left": round(fuel_left, 2),
        "average_consumption": round(fuel_delta_avg, 2),
        "target_laps_avg": int(full_laps_on_tank_from_avg),
        "target_laps_avg_consumption": round(fuel_left / full_laps_on_tank_from_avg, 2) if full_laps_on_tank_from_avg > 0 else 0,
        "ollavg": int(ollavg),
        "ollavg_consumption_target": round(one_less_from_avg, 2),
        "omlavg": int(omlavg),
        "omlavg_consumption_target": round(one_more_from_avg, 2),
        "last_lap_consumption": round(last_fuel_delta, 2),
        "target_laps_last": int(full_laps_on_tank_from_last),
        "target_laps_last_consumption": round(target_laps_last_consumption, 2),
    }

    with data_lock:
        shared_data_json["fuel_analysis"] = fuel_analysis_dict

def lap_finished():
    new_lap = ir['Lap']
    if new_lap is None or new_lap == 0:
        return False
    if new_lap == state.computation_helpers['last_lap'] + 1:
        state.computation_helpers['last_lap'] = new_lap
        return True
    state.computation_helpers['last_lap'] = new_lap
    return False

def execute_commands(text):
    commands = text.split(" ")
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
                print(f"Invalid fuel command: {command}")
        elif "tc" in command:
            try:
                tc = int(command.split(".")[1])
                # ir.pit_command(PitCommandMode., tc) # TODO cannot solve, need to use macros for tc
            except (ValueError, IndexError):
                print(f"Invalid tyre change command: {command}")
        else:
            print(f"Unknown command: {command}")

    current_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    with data_lock:
        shared_data_json["events"].append({
            "type": "command",
            "description": f"Executed commands: {', '.join(executed)}",
            "time": current_time,
        })

def new_session_state():
    state.computation_helpers['last_lap'] = ir['Lap']
    state.computation_helpers['incidents'] = ir['PlayerCarMyIncidentCount']
    state.computation_helpers['track_state'] = ir['WeatherDeclaredWet']
    state.computation_helpers['wind_direction'], _ = get_direction(ir['WindDir'] * 57.296)
    with data_lock:
        shared_data_json["total_incidents"] = state.computation_helpers['incidents']
    state.computation_helpers['fast_repairs_used'] = ir["PlayerFastRepairsUsed"]
    split_time_info()

def get_session_info():
    weekend_info = ir['WeekendInfo']
    session_info = {
        "session_id": weekend_info['SessionID'],
        "subsession_id": weekend_info['SubSessionID'],
        "track_name": weekend_info['TrackDisplayName'],
        "track_config": weekend_info['TrackConfigName'],
    }
    if session_info != state.session_info:
        for key, value in session_info.items():
            state.session_info[key] = value
        with data_lock:
            shared_data_json["session_info"] = state.session_info
        print("New session detected:", session_info)
    return session_info
