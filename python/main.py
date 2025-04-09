import irsdk
import sched
from utils import State, Car, MyQueue, time_it
import time
import numpy as np

@time_it
def relative():
    ir.freeze_var_buffer_latest()
    all_cars = []
    for car in ir['DriverInfo']['Drivers']:
        all_cars.append(Car(car['CarIdx'], car['CarNumber'], car['UserName'], car['CarID'],
                             car['CarClassID'], car['CarClassShortName'], car['TeamName'],
                               car['IRating'], car['LicString']))
    all_cars.sort(key=lambda x: x.car_id)

    my_class = ir['PlayerCarClass']
    my_position = ir['PlayerCarClassPosition']

    # their_distance = ir['CarIdxEstTime']
    their_class = ir['CarIdxClass']
    their_position = ir['CarIdxClassPosition']
    their_distance_pct = ir['CarIdxLapDistPct']

    them = list(zip(their_class, their_position, their_distance_pct))

    me = None
    for idx, elem in enumerate(them):
        if elem[1] == my_class and elem[2] == my_position:
            me = idx
            break
    if me is None:
        print("No user car found")
        ir.unfreeze_var_buffer_latest()
        return
    
    for car, elem in zip(all_cars, them):
        print(f"{car.car_number} {elem[-1]:.3f}")
    print("=" * 50 + "\n")
    ir.unfreeze_var_buffer_latest()

@time_it
def update_fuel_data():
    fuel_left = ir['FuelLevel']
    lap_progress = ir['LapDistPct']
    last_lap = ir['LapLastLapTime']

    def compute_deltas():
        for i, elem in enumerate(fuel_consumption):
            if i+1 < len(fuel_consumption):
                other = fuel_consumption[i+1]
                fuel_delta = elem[0] - other[0]
                lap_delta = 1.0 + elem[1] - other[1]
                fuel_delta_per_lap = fuel_delta / lap_delta
                fuel_deltas.append(fuel_delta_per_lap)

    fuel_deltas = []

    if last_lap is not None and last_lap > 0:
        fuel_consumption.put((fuel_left, lap_progress, last_lap))
        if len(fuel_consumption) == 1:
            return
        else:
            compute_deltas()
    elif len(fuel_consumption) > 1:
            compute_deltas()
    else:
        return

    fuel_delta_avg = np.mean(fuel_deltas)
    last_fuel_delta = fuel_deltas[-1]

    full_laps_on_tank_from_avg = int(fuel_left / fuel_delta_avg)
    omlavg = full_laps_on_tank_from_avg + 1
    ollavg = full_laps_on_tank_from_avg - 1
    one_more_from_avg = fuel_left / omlavg
    one_less_from_avg = fuel_left / ollavg

    print("=" * 50)
    print("Fuel left: {:.2f}L".format(fuel_left))
    print(f"Average consumption ({fuel_delta_avg:.2f}L) prediction")
    print(f"To do {ollavg} laps, you need {one_less_from_avg:.2f}L of fuel per lap")
    print(f"To do {full_laps_on_tank_from_avg} laps, you need {(fuel_left / full_laps_on_tank_from_avg):.2f}L of fuel per lap")
    print(f"To do {omlavg} laps, you need {one_more_from_avg:.2f}L of fuel per lap")
    
    full_laps_on_tank_from_last = int(fuel_left / last_fuel_delta)
    omllast = full_laps_on_tank_from_last + 1
    olllast = full_laps_on_tank_from_last - 1
    one_more_from_last = fuel_left / omllast
    one_less_from_last = fuel_left / olllast

    print(f"\nLast lap's consumption ({last_fuel_delta:.2f}L) prediction")
    print(f"To do {olllast} laps, you need {one_less_from_last:.2f}L of fuel per lap")
    print(f"To do {full_laps_on_tank_from_last} laps, you need {(fuel_left / full_laps_on_tank_from_last):.2f}L of fuel per lap")
    print(f"To do {omllast} laps, you need {one_more_from_last:.2f}L of fuel per lap")
    print("=" * 50)

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

def check_iracing():
    if state.ir_connected and not (ir.is_initialized and ir.is_connected):
        state.ir_connected = False
        state.last_car_setup_tick = -1
        ir.shutdown()
        return False
    elif not state.ir_connected and ir.startup(test_file='data.bin') and ir.is_initialized and ir.is_connected:
    # elif not state.ir_connected and ir.startup() and ir.is_initialized and ir.is_connected:
        state.ir_connected = True
    return True

if __name__ == '__main__':
    ir = irsdk.IRSDK()
    state = State()

    FUEL_STRATEGY_LAPS = 5
    fuel_consumption = MyQueue(FUEL_STRATEGY_LAPS)

    try:
        while not check_iracing():
            pass
        print("iRacing connected")
        state.last_lap = ir['Lap']
        while True:
            if not check_iracing() or not ir.is_initialized or not ir.is_connected:
                print("iRacing disconnected")
            if state.ir_connected:
                # if lap_finished():
                #     update_fuel_data()
                relative()
            time.sleep(5)
    except KeyboardInterrupt:
        # press ctrl+c to exit
        pass