
def disabled_in_this_state(func):
    """Simple decorator that disables function and prints an error message."""
    def print_disabled_message(*args):
        func_name = func.__name__
        class_name = func.__qualname__.split('.')[-2]
        print("Error: function {} is disabled during {}".format(func_name, class_name))
    return print_disabled_message

