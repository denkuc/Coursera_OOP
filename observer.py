from abc import ABC, abstractmethod


class ObservableEngine(Engine):
    def __init__(self):
        self.__printers = []

    def subscribe(self, printer):
        if printer not in self.__printers:
            self.__printers.append(printer)

    def unsubscribe(self, printer):
        self.__printers.remove(printer)

    def notify(self, achievement):
        for printer in self.__printers:
            printer.update(achievement)


class AbstractObserver(ABC):
    @abstractmethod
    def update(self, achievement):
        ...


class FullNotificationPrinter(AbstractObserver):
    def __init__(self):
        self.achievements = list()

    def update(self, achievement):
        if achievement not in self.achievements:
            self.achievements.append(achievement)


class ShortNotificationPrinter(AbstractObserver):
    def __init__(self):
        self.achievements = set()

    def update(self, achievement):
        self.achievements.add(achievement['title'])
