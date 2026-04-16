#from .datasets import DummyDataset, EpisodicRLDSDataset, RLDSBatchTransform, RLDSDataset
#Deactivated for my cobot

# Lazy imports to avoid pulling in dlimp/tensorflow during inference
def __getattr__(name):
    if name in ("DummyDataset", "EpisodicRLDSDataset", "RLDSBatchTransform", "RLDSDataset"):
        from .datasets import DummyDataset, EpisodicRLDSDataset, RLDSBatchTransform, RLDSDataset
        return {"DummyDataset": DummyDataset, "EpisodicRLDSDataset": EpisodicRLDSDataset, "RLDSBatchTransform": RLDSBatchTransform, "RLDSDataset": RLDSDataset}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")