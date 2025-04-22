from dataclasses import dataclass
import time
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
    __slots__ = ['ir_connected', 'last_car_setup_tick', 'last_lap', 'last_fuel_level', 
                'in_pit', 'incidents', 'track_state', 'wind_direction', 'wind_speed', 
                'fast_repairs_used']
    
    def __init__(self):
        self.ir_connected = False
        self.last_car_setup_tick = -1
        self.last_lap = 0
        self.last_fuel_level = -1.0
        self.in_pit = False
        self.incidents = 0
        self.track_state = False
        self.wind_direction = None
        self.wind_speed = None
        self.fast_repairs_used = 0

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
    __slots__ = ['task_intervals', 'loop_interval']
    
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