from abc import ABC, abstractmethod


class Collector(ABC):

    @abstractmethod
    def collect(self, data, source):
        pass

    @abstractmethod
    def deliver(self):
        pass
