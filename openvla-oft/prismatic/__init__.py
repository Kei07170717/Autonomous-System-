#Deactivated for mycobot
# from .models import available_model_names, available_models, get_model_description, load

# Lazy import to avoid eager loading of training-only modules
def __getattr__(name):
    if name in ("available_model_names", "available_models", "get_model_description", "load"):
        from .models import available_model_names, available_models, get_model_description, load
        return {"available_model_names": available_model_names, "available_models": available_models, "get_model_description": get_model_description, "load": load}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


