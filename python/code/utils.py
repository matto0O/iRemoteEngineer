from enum import Enum
import time
from numpy import zeros

class AutomationState(Enum):
    AWAITING_SIM = 0
    OUT_OF_THE_CAR = 1
    IN_THE_CAR = 2

class MyQueue:
    __slots__ = ['queue', 'size', 'pointer']
    
    def __init__(self, max_size):
        self.queue = zeros(max_size, dtype=float)
        self.size = 0
        self.pointer = 0
    
    def put(self, item):
        self.queue[self.pointer] = item
        self.pointer = (self.pointer + 1) % len(self.queue)
        self.size = min(self.size + 1, len(self.queue))
    
    def last(self):
        if self.size == 0:
            return 0
        last_pointer = (self.pointer - 1) % len(self.queue)
        return self.queue[last_pointer]

class State:
    __slots__ = ['ir_connected', 'last_car_setup_tick', 'computation_helpers', 'session_info']
    
    def __init__(self):
        self.ir_connected = False
        self.last_car_setup_tick = -1
        self.computation_helpers = {
            "last_lap": 0,
            "last_fuel_level": -1.0,
            "in_pit": False,
            "incidents": 0,
            "track_state": False,
            "wind_direction": None,
            "wind_speed": None,
            "fast_repairs_used": 0
        }
        self.session_info = {
            "session_id": None,
            "subsession_id": None,
            "track_name": None,
            "track_config": None,
            "team_name": None,
            "player_car_number": None,
            "car_name": None,
            "event_type": None,
            "lobby_name": None
        }


class Car:
    __slots__ = ['idx', 'car_number', 'user_name', 'car_model_id', 'class_id', 
                'model_short', 'team_name', 'irating', 'license']
    
    def __init__(self, idx, car_number, user_name, car_model_id, class_id, 
                model_short, team_name, irating, license):
        self.idx = idx
        self.car_number = car_number
        self.user_name = user_name
        self.car_model_id = car_model_id
        self.class_id = class_id
        self.model_short = model_short
        self.team_name = team_name
        self.irating = irating
        self.license = license

    def __eq__(self, other):
        if isinstance(other, int):
            return self.idx == other
        if not isinstance(other, Car):
            return NotImplemented
        return self.idx == other.idx

    def __repr__(self):
        return (f"Car(idx={self.idx}, car_number={self.car_number}, user_name={self.user_name}, "
                f"car_model_id={self.car_model_id}, class_id={self.class_id}, "
                f"model_short={self.model_short}, team_name={self.team_name}, "
                f"irating={self.irating}, license={self.license})")

class TaskScheduler:
    __slots__ = ['tasks', 'current_time']
    
    def __init__(self):
        # Format: {function_name: {'func': function_ref, 'interval': seconds, 'last_run': timestamp}}
        self.tasks = {}
        self.current_time = time.time()
    
    def register(self, name, func, interval):
        """Register a function to be executed at specified intervals"""
        self.tasks[name] = {
            'func': func,
            'interval': interval,
            'last_run': 0  # Start with 0 to run on first cycle
        }
    
    def run_due_tasks(self):
        """Run all tasks that are due based on their intervals"""
        self.current_time = time.time()
        for name, task in self.tasks.items():
            if self.current_time - task['last_run'] >= task['interval']:
                try:
                    task['func']()
                    task['last_run'] = self.current_time
                except Exception as e:
                    print(f"Error running task {name}: {e}")

class Config:
    __slots__ = ['task_intervals', 'loop_interval', 'exposed_port', 'fuel_strategy_laps']
    
    def __init__(self):
        # Default intervals in seconds
        self.task_intervals = {
            'relative': 1.0,
            'check_if_in_pit': 5.0,
            'weather_info': 15.0,
            'new_incidents': 15.0,
            'tyre_data': 60.0,
        }
        self.loop_interval = 1.0         # Main loop sleep time
        self.exposed_port = 8080
        self.fuel_strategy_laps = 5

    def update_interval(self, task_name, interval):
        """Update a specific task's interval"""
        if task_name in self.task_intervals:
            self.task_intervals[task_name] = float(interval)
            return True
        return False
    
    def get_interval(self, task_name):
        """Get the interval for a specific task"""
        return self.task_intervals.get(task_name, 1.0)
    
    def set_loop_interval(self, interval):
        """Set the main loop interval"""
        self.loop_interval = float(interval)

def time_it(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function {func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper


# def create_config():
#     file_config = ConfigParser()
#     global config
#     if not os.path.exists(f"config.ini"):
#         # Default settings
#         file_config.add_section('intervals')
#         file_config.set('intervals', 'relative', '0.5')
#         file_config.set('intervals', 'check_if_in_pit', '1.0')
#         file_config.set('intervals', 'weather_info', '5.0')
#         file_config.set('intervals', 'new_incidents', '1.0')
#         file_config.set('intervals', 'tyre_data', '5.0')
#         file_config.set('intervals', 'main_loop', '1.0')

#         file_config.add_section('server')
#         file_config.set('server', 'port', '3721')

#         file_config.add_section('misc')
#         file_config.set('misc', 'fuel_strategy_laps', '5')
#     else:
#         # Load existing file_config
#         file_config.read("config.ini")
        
#         # Ensure all sections exist
#         if not file_config.has_section('intervals'):
#             file_config.add_section('intervals')
#         if not file_config.has_section('server'):
#             file_config.add_section('server')
#         if not file_config.has_section('misc'):
#             file_config.add_section('misc')
            
#         # Set default values only if they don't exist
#         if not file_config.has_option('intervals', 'relative'):
#             file_config.set('intervals', 'relative', '0.5')
#         else:
#             config.task_intervals['relative'] = float(file_config.get('intervals', 'relative'))
#         if not file_config.has_option('intervals', 'check_if_in_pit'):
#             file_config.set('intervals', 'check_if_in_pit', '1.0')
#         else:
#             config.task_intervals['check_if_in_pit'] = float(file_config.get('intervals', 'check_if_in_pit'))
#         if not file_config.has_option('intervals', 'weather_info'):
#             file_config.set('intervals', 'weather_info', '5.0')
#         else:
#             config.task_intervals['weather_info'] = float(file_config.get('intervals', 'weather_info'))
#         if not file_config.has_option('intervals', 'new_incidents'):
#             file_config.set('intervals', 'new_incidents', '1.0')
#         else:
#             config.task_intervals['new_incidents'] = float(file_config.get('intervals', 'new_incidents'))
#         if not file_config.has_option('intervals', 'tyre_data'):
#             file_config.set('intervals', 'tyre_data', '5.0')
#         else:
#             config.task_intervals['tyre_data'] = float(file_config.get('intervals', 'tyre_data'))
#         if not file_config.has_option('intervals', 'main_loop'):
#             file_config.set('intervals', 'main_loop', '1.0')
#         else:
#             config.loop_interval = float(file_config.get('intervals', 'main_loop'))
#         if not file_config.has_option('server', 'port'):
#             file_config.set('server', 'port', '3721')
#         else:
#             config.exposed_port = int(file_config.get('server', 'port'))
#         if not file_config.has_option('misc', 'fuel_strategy_laps'):
#             file_config.set('misc', 'fuel_strategy_laps', '5')
#         else:
#             config.fuel_strategy_laps = int(file_config.get('misc', 'fuel_strategy_laps'))

#     file_config.write(open("config.ini", "w"))

# def save_config():
#     file_config = ConfigParser()
#     file_config.read("config.ini")
    
#     # Save all intervals
#     for task_name, interval in config.task_intervals.items():
#         file_config.set('intervals', task_name, str(interval))
    
#     # Save loop interval
#     file_config.set('intervals', 'main_loop', str(config.loop_interval))

#     # Save port
#     file_config.set('server', 'port', str(config.exposed_port))

#     # Save fuel strategy laps
#     file_config.set('misc', 'fuel_strategy_laps', str(config.fuel_strategy_laps))

#     with open("config.ini", "w") as configfile:
#         file_config.write(configfile)
