from time import sleep

from race_computations import schedule_data_ingestion, run_jobs, ir, state

def check_iracing(test_file=None):
    if state.ir_connected and not (ir.is_initialized and ir.is_connected):
        state.ir_connected = False
        state.last_car_setup_tick = -1
        ir.shutdown()
        return False
    elif state.ir_connected and (ir.is_initialized and ir.is_connected):
        return True
    elif not state.ir_connected and ir.startup(test_file=test_file) and ir.is_initialized and ir.is_connected:
        state.ir_connected = True
    return False

if __name__ == "__main__":
    while not check_iracing():
        print("Waiting for iRacing...")
        sleep(1)
    state.session_info["lobby_name"] = "asa"
    partition_key = state.session_info["lobby_name"]

    schedule_data_ingestion(lobby_name=partition_key, team_name="name")

    while True:
        run_jobs(interval=0.5)