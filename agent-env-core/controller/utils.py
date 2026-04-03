
def disabled_in_this_state(func):
    """Simple decorator that disables function and prints an error message."""
    def print_disabled_message(*args):
        func_name = func.__name__
        class_name = func.__qualname__.split('.')[-2]
        print("Error: function {} is disabled during {}".format(func_name, class_name))
    return print_disabled_message

import numpy as np

def format_rl_value(val):
    """Helper function to cleanly format numpy arrays and scalars."""
    if isinstance(val, np.ndarray):
        if val.ndim == 0:
            return str(val.item())
        if val.ndim == 1:
            return np.array2string(val, precision=2, separator=', ', suppress_small=True)
        return f"<array shape={val.shape} dtype={val.dtype}>"
    elif isinstance(val, np.generic):
        return str(val.item())
    return str(val)

def print_action(action):
    """Prints the action dictionary cleanly on a single line."""
    if not action:
        print("Action: <empty>")
        return
        
    # Build a list of formatted strings, then join them with a comma and space
    formatted_items = [f"{key}: {format_rl_value(value)}" for key, value in action.items()]
    print(f"Action:  {', '.join(formatted_items)}")

def print_observation(obs):
    """Prints the observation dictionary on a single line, ignoring cameras."""
    if not obs:
        print("Obs: <empty>")
        return
        
    # Build a list of formatted strings, filtering out camera/image keys
    formatted_items = [
        f"{key}: {format_rl_value(value)}" 
        for key, value in obs.items() 
        if 'cam' not in key.lower() and 'image' not in key.lower()
    ]
    print(f"Obs:     {', '.join(formatted_items)}")
    
