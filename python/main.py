import irsdk
import sched
from utils import State, Car, MyQueue, time_it
import time
import numpy as np
from fastapi import FastAPI, WebSocket
import asyncio
import threading
import uvicorn

app = FastAPI()

ir = irsdk.IRSDK()
state = State()
FUEL_STRATEGY_LAPS = 5
fuel_consumption = MyQueue(FUEL_STRATEGY_LAPS)

# Shared car data
shared_data_json = {
    "player_car_number": None,
    "cars": [],
    "fuel_analysis": {}
}
data_lock = threading.Lock()

# @time_it
def relative():
    ir.freeze_var_buffer_latest()
    all_cars = []
    for car in ir['DriverInfo']['Drivers']:
        all_cars.append(Car(car['CarIdx'], car['CarNumber'], car['UserName'], car['CarID'],
                             car['CarClassID'], car['CarScreenNameShort'], car['TeamName'],
                               car['IRating'], car['LicString']))
    all_cars.sort(key=lambda x: x.car_id)

    my_class = ir['PlayerCarClass']
    my_position = ir['PlayerCarClassPosition']

    their_class = ir['CarIdxClass']
    their_position = ir['CarIdxClassPosition']
    their_distance_pct = ir['CarIdxLapDistPct']
    them_pit_road = ir['CarIdxOnPitRoad']

    them = list(zip(their_class, their_position, their_distance_pct, them_pit_road))

    car_data = []
    me = None
    for car, elem in zip(all_cars, them):
        if my_position != 0 and elem[0] == my_class and elem[1] == my_position:
            me = car.car_number
        car_data.append({
            "user_name": car.user_name,
            "team_name": car.team_name,
            "class_id": car.class_id,
            "car_model_id": car.car_model_id,
            "car_number": car.car_number,
            "distance_pct": elem[2],
            "in_pit": elem[3],
        })

    with data_lock:
        shared_data_json["player_car_number"] = me
        shared_data_json["cars"] = car_data

    ir.unfreeze_var_buffer_latest()

# @time_it
def check_if_in_pit():
    in_pit = ir['OnPitRoad']
    if in_pit:
        state.last_fuel_level = ir['FuelLevel']
        state.last_lap = ir['Lap']

# @time_it
def update_fuel_data():
    fuel_left = ir['FuelLevel']
    if state.last_fuel_level == -1.0:
        state.last_fuel_level = fuel_left
        return
    else:
        fuel_delta = state.last_fuel_level - fuel_left
        state.last_fuel_level = fuel_left
        fuel_consumption.put(fuel_delta)

    fuel_delta_avg = np.mean(fuel_consumption.queue)
    last_fuel_delta = fuel_consumption.last()

    full_laps_on_tank_from_avg = int(fuel_left / fuel_delta_avg)
    omlavg = full_laps_on_tank_from_avg + 1
    ollavg = full_laps_on_tank_from_avg - 1
    one_more_from_avg = fuel_left / omlavg
    one_less_from_avg = fuel_left / ollavg

    # print("=" * 50)
    # print("Fuel left: {:.2f}L".format(fuel_left))
    # print(f"Average consumption ({fuel_delta_avg:.2f}L) prediction")
    # print(f"To do {ollavg} laps, you need {one_less_from_avg:.2f}L of fuel per lap")
    # print(f"To do {full_laps_on_tank_from_avg} laps, you need {(fuel_left / full_laps_on_tank_from_avg):.2f}L of fuel per lap")
    # print(f"To do {omlavg} laps, you need {one_more_from_avg:.2f}L of fuel per lap")
    
    full_laps_on_tank_from_last = int(fuel_left / last_fuel_delta)
    # omllast = full_laps_on_tank_from_last + 1
    # olllast = full_laps_on_tank_from_last - 1
    # one_more_from_last = fuel_left / omllast
    # one_less_from_last = fuel_left / olllast

    # print(f"\nLast lap's consumption ({last_fuel_delta:.2f}L) prediction")
    # print(f"To do {olllast} laps, you need {one_less_from_last:.2f}L of fuel per lap")
    # print(f"To do {full_laps_on_tank_from_last} laps, you need {(fuel_left / full_laps_on_tank_from_last):.2f}L of fuel per lap")
    # print(f"To do {omllast} laps, you need {one_more_from_last:.2f}L of fuel per lap")
    # print("=" * 50)

    fuel_analysis_dict = {
        "fuel_left": fuel_left,
        "average_consumption": fuel_delta_avg,
        "target_laps_avg": full_laps_on_tank_from_avg,
        "target_laps_avg_consumption": (fuel_left / full_laps_on_tank_from_avg),
        "ollavg": ollavg,
        "ollavg_consumption_target": one_less_from_avg,
        "omlavg": omlavg,
        "omlavg_consumption_target": one_more_from_avg,

        "last_lap_consumption": last_fuel_delta,
        "target_laps_last": full_laps_on_tank_from_last,
        "target_laps_last_consumption": (fuel_left / full_laps_on_tank_from_last),
        # "olllast": olllast,
        # "olllast_consumption_target": one_less_from_last,
        # "omllast": omllast,
        # "omllast_consumption_target": one_more_from_last,
    }

    with data_lock:
        shared_data_json["fuel_analysis"] = fuel_analysis_dict

def lap_finished():
    new_lap = ir['Lap']
    if new_lap is None or new_lap == 0:
        return False
    if new_lap == state.last_lap + 1:
        state.last_lap = new_lap
        print("Lap finished")
        return True
    state.last_lap = new_lap
    return False

def check_iracing(test_file=None):
    if state.ir_connected and not (ir.is_initialized and ir.is_connected):
        state.ir_connected = False
        state.last_car_setup_tick = -1
        ir.shutdown()
        return False
    elif not state.ir_connected and ir.startup(test_file=test_file) and ir.is_initialized and ir.is_connected:
    # elif not state.ir_connected and ir.startup() and ir.is_initialized and ir.is_connected:
        state.ir_connected = True
    return True

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await asyncio.sleep(1)
            with data_lock:
                await websocket.send_json(shared_data_json)
    except Exception as e:
        print(f"WebSocket disconnected: {e}")
    finally:
        await websocket.close()


def start_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == '__main__':
    threading.Thread(target=start_api, daemon=True).start()

    try:
        counter = 8 #remove counter
        while not check_iracing():
            pass
        print("iRacing connected")
        state.last_lap = ir['Lap']
        while True:
            # to remove later #######
            # if not check_iracing(f'./python/testset/data{counter}.bin') or not ir.is_initialized or not ir.is_connected:
                # counter += 1
                # if counter > 14:
                #     counter = 8
                # print("iRacing disconnected")
            #########################
            if not check_iracing() or not ir.is_initialized or not ir.is_connected:
                print("iRacing disconnected")
            if state.ir_connected:
                check_if_in_pit()
                if lap_finished():
                    update_fuel_data()
                relative()
            # ir.shutdown() # remove
            time.sleep(1)
    except KeyboardInterrupt:
        # press ctrl+c to exit
        pass