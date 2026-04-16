#from .materialize import get_vla_dataset_and_collator
#Deactivated for mycobot

def get_vla_dataset_and_collator(*args, **kwargs):
    from .materialize import get_vla_dataset_and_collator as _fn
    return _fn(*args, **kwargs)
