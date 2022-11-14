from abc import ABC, abstractmethod


class AbstractEffect(Hero, ABC):
    _MAIN_STATS = ["Strength", "Perception", "Endurance",
                   "Charisma", "Intelligence", "Agility", "Luck"]

    def __init__(self, base: Hero):
        super().__init__()
        self.base = base
        self.stats = self.base.get_stats()
        self.__change_stats()

    def get_positive_effects(self):
        return self.base.get_positive_effects().copy()

    def get_negative_effects(self):
        return self.base.get_negative_effects().copy()

    def get_stats(self):
        new_stats = self.base.get_stats()
        stats_change = self._stats_change()
        for key, value in stats_change.items():
            new_stats[key] += value

        return new_stats

    def __change_stats(self):
        for key, value in self._stats_change().items():
            self.stats[key] += value

    @abstractmethod
    def _stats_change(self) -> dict:
        ...


class AbstractPositive(AbstractEffect, ABC):
    def get_positive_effects(self):
        base_positive_effects = super().get_positive_effects()
        base_positive_effects.append(self.__class__.__name__)
        return base_positive_effects


class AbstractNegative(AbstractEffect, ABC):
    def get_negative_effects(self):
        base_negative_effects = super().get_negative_effects()
        base_negative_effects.append(self.__class__.__name__)
        return base_negative_effects


class Berserk(AbstractPositive):
    def __init__(self, base):
        super().__init__(base)

    def _stats_change(self):
        return dict(**{stat: 7 for stat in ['Strength', 'Endurance',
                                            'Agility', 'Luck']},
                    **{stat: -3 for stat in ['Perception', 'Charisma',
                                             'Intelligence']},
                    **{'HP': 50})


class Blessing(AbstractPositive):
    def __init__(self, base):
        super().__init__(base)

    def _stats_change(self):
        return {stat: 2 for stat in self._MAIN_STATS}


class Weakness(AbstractNegative):
    def __init__(self, base):
        super().__init__(base)

    def _stats_change(self):
        return {stat: -4 for stat in ['Strength', 'Endurance', 'Agility']}


class Curse(AbstractNegative):
    def __init__(self, base):
        super().__init__(base)

    def _stats_change(self):
        return {stat: -2 for stat in self._MAIN_STATS}


class EvilEye(AbstractNegative):
    def __init__(self, base):
        super().__init__(base)

    def _stats_change(self):
        return {'Luck': -10}
