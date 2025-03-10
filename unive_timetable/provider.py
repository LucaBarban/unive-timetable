from abc import ABC, abstractmethod
from typing import List, Any
from unive_timetable.lesson import Lesson
from types import MappingProxyType


class Provider(ABC):
    @abstractmethod
    def __init__(self, config: MappingProxyType[str, Any]):
        pass

    @abstractmethod
    def getEvents(self) -> List[Lesson]:
        pass

    @abstractmethod
    def createEvents(self, events: List[Lesson]):
        pass

    @abstractmethod
    def deleteEvents(self, events: List[Lesson]):
        pass
