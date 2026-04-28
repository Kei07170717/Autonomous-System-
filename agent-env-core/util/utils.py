import time
import os
from functools import wraps

# --- GLOBAL TOGGLE ---
# Set this to False to instantly disable all timing prints across your codebase.
ENABLE_PROFILING = False

# Alternatively, you can control it via environment variables without changing code:
# ENABLE_PROFILING = os.getenv("PROFILE_CODE") == "1"

def time_it(func):
    """A decorator that prints execution time, with a global toggle."""
    
    # If turned off, return the original function with no wrapper.
    # This prevents any extra function calls or logic from slowing down your code.
    if not ENABLE_PROFILING:
        return func

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        
        result = func(*args, **kwargs)
        
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000
        
        if args and hasattr(args[0], '__class__'):
            class_name = args[0].__class__.__name__
            print(f"#[{class_name}.{func.__name__}] executed in {execution_time:.4f} ms")
        else:
            print(f"#[{func.__name__}] executed in {execution_time:.4f} ms")
            
        return result
        
    return wrapper
