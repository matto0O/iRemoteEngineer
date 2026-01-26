from enum import Enum
import time
import logging
from numpy import zeros

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
    __slots__ = ['ir_connected', 'last_car_setup_tick', 'uuid', 'computation_helpers', 'session_info', 'current_token']
    
    def __init__(self):
        self.ir_connected = False
        self.last_car_setup_tick = -1
        self.uuid = None
        self.current_token = None
        self.reset_state()

    def reset_token(self):
        self.current_token = None

    def reset_state(self):
        self.computation_helpers = {
            "last_lap": 0,
            "last_fuel_level": -1.0,
            "in_pit": False,
            "track_state": False,
            "wind_direction": None,
            "wind_speed": None,
            "fast_repairs_used": 0,
            "cars": {},
            "tyres": {},
            "last_fuel_level": -1.0,
            "last_incidents": 0,
            "last_lap_incidents": 0,
            "in_car": False,
            "being_towed": False
        }
        self.session_info = {
            'series_id': None,
            "session_id": None,
            "subsession_id": None,
            "event_type": None,
            "session_type": None,
            "track_name": None,
            "track_config": None,
            "team_name": None,
            "player_car_number": None,
            "car_model_id": None,
            "lobby_name": None
        }


class Car:
    __slots__ = ['idx', 'car_number', 'user_name', 'car_model_id', 'class_id', 
                 'team_name', 'irating', 'license']
    
    def __init__(self, idx, car_number, user_name, car_model_id, class_id, 
                team_name, irating, license):
        self.idx = idx
        self.car_number = car_number
        self.user_name = user_name
        self.car_model_id = car_model_id
        self.class_id = class_id
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
                f"team_name={self.team_name}, "
                f"irating={self.irating}, license={self.license})")

class TaskScheduler:
    __slots__ = ['tasks', 'current_time']
    
    def __init__(self):
        # Format: {function_name: {'func': function_ref, 'interval': seconds, 'last_run': timestamp}}
        self.tasks = {}
        self.current_time = time.time()
    
    def register(self, name, func, interval, **kwargs):
        """Register a function to be executed at specified intervals"""
        self.tasks[name] = {
            'func': func,
            'kwargs': kwargs,
            'interval': interval,
            'last_run': 0  # Start with 0 to run on first cycle
        }
    
    def run_due_tasks(self):
        """Run all tasks that are due based on their intervals"""
        self.current_time = time.time()
        for name, task in self.tasks.items():
            if self.current_time - task['last_run'] >= task['interval']:
                try:
                    if a:= task['kwargs']:
                        task['func'](**a)
                    else:
                        task['func']()
                    task['last_run'] = self.current_time
                except Exception as e:
                    logging.error(f"Error running task {name}: {e}")

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
        logging.debug(f"Function {func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper
