from typing import Tuple, Any

class Block:
    def __init__(self, color: Any, classification_threshold: float) -> None:
        self._color = color
        self._classification_threshold = classification_threshold
        

    @property
    def color(self) -> Any:
        return self._color

    @property
    def classification_threshold(self) -> float:
        return self._classification_threshold

    

        
        
        