import functools
import math

def smooth_tuple(alpha=0.2):
    def decorator(func):
        # Using a list to hold state allows 'nonlocal' access in python
        state = {"last_value": None}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_value = func(*args, **kwargs)
            
            if current_value is None:
                return state["last_value"]
                
            if state["last_value"] is None:
                state["last_value"] = current_value
                return current_value
            
            smoothed = tuple(
                alpha * curr + (1 - alpha) * last 
                for curr, last in zip(current_value, state["last_value"])
            )
            state["last_value"] = smoothed
            return smoothed
        return wrapper
    return decorator

def stable_bool(threshold=5):
    # Layer 1: Receives the decorator arguments (threshold)
    def decorator(func):
        # State stored here persists for the life of the decorated function
        state = {"counter": 0, "current_state": False}

        # Layer 2: Receives the function being decorated
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Layer 3: Receives the actual call arguments (self, current_xy, etc.)
            reading = func(*args, **kwargs)

            if reading != state["current_state"]:
                state["counter"] += 1
                if state["counter"] >= threshold:
                    state["current_state"] = reading
                    state["counter"] = 0
            else:
                state["counter"] = 0 
                
            return state["current_state"]
        
        return wrapper # Must return the wrapper
    return decorator # Must return the decorator


def rotate_point(x, y, degrees):
    # Convert degrees to radians
    radians = math.radians(degrees)
    
    # Calculate new coordinates
    new_x = x * math.cos(radians) - y * math.sin(radians)
    new_y = x * math.sin(radians) + y * math.cos(radians)
    
    return new_x, new_y
