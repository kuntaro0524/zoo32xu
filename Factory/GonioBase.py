from abc import ABC, abstractmethod

class GonioBase(ABC):
    common_variable = 32.3543
    @abstractmethod
    def process(self):
        pass