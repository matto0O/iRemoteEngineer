from dataclasses import dataclass
import time

class MyQueue:
    def __init__(self, max_size=5):
        self.queue = []
        self.max_size = max_size

    def put(self, item):
        self.queue.append(item)
        if len(self.queue) >= self.max_size:
            self.queue = self.queue[1:]
    
    def peek(self):
        if self.queue:
            return self.queue[0]
        return None
    
    def last(self):
        if self.queue:
            return self.queue[-1]
        return None
    
    def empty(self):
        return len(self.queue) == 0
    
    def __len__(self):
        return len(self.queue)
    
    def __getitem__(self, index):
        return self.queue[index]
    
    def __str__(self):
        return str(self.queue)
    
    def __repr__(self):
        return repr(self.queue)
    
    def __iter__(self):
        return iter(self.queue)
    
    def __contains__(self, item):
        return item in self.queue
    
    def __delitem__(self, index):
        del self.queue[index]

    def __setitem__(self, index, item):
        self.queue[index] = item


class State:
    ir_connected = False
    last_car_setup_tick = -1
    last_lap = 0

@dataclass
class Car:
    car_id:int
    car_number:str
    user_name:str
    car_model_id:str
    class_id:int
    class_name:str
    team_name:str
    irating:int
    licence:str

    def __eq__(self, other):
        if isinstance(other, int):
            return self.car_id == other
        if not isinstance(other, Car):
            return NotImplemented
        return self.car_id == other.car_id
    
    def __str__(self):
        return f'{self.user_name} - {self.class_name} - {self.irating} - {self.licence}'
    
def time_it(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function {func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper