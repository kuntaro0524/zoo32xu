from abc import ABC, abstractmethod

class GonioBase(ABC):
    common_variable = 32.3543
    cmount_position=[0.0,1.0,1.5]
    gonio_direction="FROM_RIGHT"

    @abstractmethod
    def process(self):
        pass