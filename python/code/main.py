import json
import threading
from time import sleep

from utils import Config, TaskScheduler, AutomationState, MyQueue
from race_computations import new_session_state, get_session_info, get_data, ir, state
from kinesis_producer import KinesisProducer

config = Config()
scheduler = TaskScheduler()

kinesis_producer = KinesisProducer()

gui = None
server = None
exit_event = threading.Event()

def check_iracing(test_file=None):
    if state.ir_connected and not (ir.is_initialized and ir.is_connected):
        state.ir_connected = False
        state.last_car_setup_tick = -1
        ir.shutdown()
        return False
    elif not state.ir_connected and ir.startup(test_file=test_file) and ir.is_initialized and ir.is_connected:
        state.ir_connected = True
    return True

if __name__ == "__main__":
    test_file = "python/newdataset/data24.bin"
    state.computation_helpers["fuel_consumption_queue"] = MyQueue(10)
    state.session_info["lobby_name"] = "eeaaaa"
    ir.startup(test_file=test_file)
    automation_state = AutomationState.AWAITING_SIM
    print("Waiting for iRacing to start...")
    i=24
    while i < 367:
        test_file = f"python/newdataset/data{i}.bin"
        print(f"Checking file: {test_file}")

        if automation_state == AutomationState.AWAITING_SIM:
            while not check_iracing(test_file=test_file):
                sleep(5)
            print("iRacing detected. Initializing...")
            automation_state = AutomationState.OUT_OF_THE_CAR
        elif automation_state == AutomationState.OUT_OF_THE_CAR:
            if not check_iracing(test_file=test_file):
                automation_state = AutomationState.AWAITING_SIM
                print("Waiting for iRacing to start...")
                continue
            new_session_state()
            if ir['LRtempCL'] != -1:
                print(ir["LRtempCL"])
                print("In car detected. Setting up session...")
                automation_state = AutomationState.IN_THE_CAR
            else:
                sleep(5)
        elif automation_state == AutomationState.IN_THE_CAR:
            if not check_iracing(test_file=test_file):
                automation_state = AutomationState.AWAITING_SIM
                print("Waiting for iRacing to start...")
                continue
            if ir['PlayerCarIdx'] == -1:
                print("Out of car detected. Waiting to re-enter...")
                automation_state = AutomationState.OUT_OF_THE_CAR
                continue
            
            get_session_info()
            partition_key = f"{state.session_info["lobby_name"]}"
            
            data = get_data()
            # with open(f"output_data_{i}.json", "w") as json_file:
            #     json.dump(data, json_file, indent=4)
            # exit(1)
            print(data)
            kinesis_producer.send_record(data, partition_key=partition_key)
            sleep(1)
            i += 1
        

    # while check_iracing():
    #     sleep(5)

    # while ir.is_connected:
    #     weekend_info = ir['WeekendInfo']
    #     sessionId = weekend_info['SessionID']
    #     subSessionId = weekend_info['SubSessionID']
    #     date = weekend_info['Date']

    #     # print("sessionid = ", ir['SessionUniqueID'])
    #     # print("sessionnum = ", ir['SessionNum'])
    #     # print("carid = ", ir['PlayerCarID'])
    #     print(ir["WeekendInfo"])
    #     break