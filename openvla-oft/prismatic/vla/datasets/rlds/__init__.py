#from .dataset import make_interleaved_dataset, make_single_dataset
#Deactivated for mycobot

# Lazy imports to avoid pulling in dlimp/tensorflow during inference
def __getattr__(name):
    if name in ("make_interleaved_dataset", "make_single_dataset"):
        from .dataset import make_interleaved_dataset, make_single_dataset
        return {"make_interleaved_dataset": make_interleaved_dataset, "make_single_dataset": make_single_dataset}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
