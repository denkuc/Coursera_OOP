import random
from abc import ABC, abstractmethod
from copy import copy

import yaml
from objects import PrototypeList


class AbstractMap(ABC):
    __MAP_SIZE = 41

    def __init__(self):
        self.service = None
        self.map_values = [[0 for _ in range(self.__MAP_SIZE)]
                           for _ in range(self.__MAP_SIZE)]

    def add_service(self, service):
        self.service = service

    def get_map(self):
        for i, row in enumerate(self.map_values):
            for j, value in enumerate(row):
                self._set_cell_surface(i, j, value)

        return self.map_values

    @abstractmethod
    def _set_cell_surface(self, i, j, value):
        if self._is_border(i, j):
            self.map_values[j][i] = self.service.wall
        elif (i, j) == (1, 1):
            self.map_values[j][i] = self.service.get_random_floor()
        else:
            self.map_values[j][i] = self._get_random_surface(value)

    def _is_border(self, i, j):
        borders = [0, self.__MAP_SIZE-1]
        return i in borders or j in borders

    def _get_random_surface(self, sparseness):
        if random.uniform(0, 1.0) < sparseness:
            return self.service.wall
        else:
            return self.service.get_random_floor()


class AbstractObjects(ABC):
    def __init__(self):
        self.service = None
        self.objects = []
        self.config = {}

    def add_service(self, service):
        self.service = service

    @abstractmethod
    def get_objects(self, game_map):
        pass

    def _set_stairs(self, game_map):
        stairs = copy(self.service.prototypes.get_object_by_name('stairs'))
        stairs.position = self._get_random_empty_cell(game_map)
        self.objects.append(stairs)

    def _set_objects_and_allies(self, game_map):
        for object_prototype in self.service.prototypes.objects:
            for i in range(random.randint(object_prototype.min_count,
                                          object_prototype.max_count)):
                ally_clone = copy(object_prototype)
                ally_clone.position = self._get_random_empty_cell(game_map)
                self.objects.append(ally_clone)

        for ally_prototype in self.service.prototypes.allies:
            for i in range(random.randint(ally_prototype.min_count,
                                          ally_prototype.max_count)):
                ally_clone = copy(ally_prototype)
                ally_clone.position = self._get_random_empty_cell(game_map)
                self.objects.append(ally_clone)

    def _get_random_empty_cell(self, _map):
        coord = self.__get_random_cell()
        intersect = True
        while intersect:
            intersect = False
            if _map[coord[1]][coord[0]] == self.service.wall:
                intersect = True
                coord = self.__get_random_cell()

                continue
            for obj in self.objects:
                if coord == obj.position or coord == (1, 1):
                    intersect = True
                    coord = self.__get_random_cell()

        return coord

    @staticmethod
    def __get_random_cell():
        return random.randint(1, 39), random.randint(1, 39)


class MapFactory(yaml.YAMLObject):
    def __init__(self):
        super().__init__()

    class Map(AbstractMap):
        def _set_cell_surface(self, i, j, value):
            pass

    class Objects(AbstractObjects):
        def get_objects(self, game_map):
            pass

    @classmethod
    def from_yaml(cls, loader, node):
        _map = cls.Map()
        _obj = cls.Objects()
        config = loader.construct_mapping(node)
        _obj.config.update(config)
        return {'map': _map, 'obj': _obj}


class EndMap(MapFactory):
    yaml_tag = "!end_map"

    class Map(AbstractMap):
        def __init__(self):
            super().__init__()
            string_map_values = ['0000000000000000000000000000000000000000',
                                 '0                                      0',
                                 '0                                      0',
                                 '0  0   0   000   0   0  00000  0   0   0',
                                 '0  0  0   0   0  0   0  0      0   0   0',
                                 '0  000    0   0  00000  0000   0   0   0',
                                 '0  0  0   0   0  0   0  0      0   0   0',
                                 '0  0   0   000   0   0  00000  00000   0',
                                 '0                                   0  0',
                                 '0                                      0',
                                 '0  000   00000 0   0 0  0 0   0  0000  0',
                                 '0  0  0  0     00  0 0 0  0   0 0      0',
                                 '0  0   0 0000  0 0 0 00   0   0 0      0',
                                 '0  0  0  0     0  00 0 0  0   0 0      0',
                                 '0  000   00000 0   0 0  0  000   0000  0',
                                 '0                                      0',
                                 '0                                      0',
                                 '0000000000000000000000000000000000000000']
            self.map_values = list(map(list, string_map_values))

        def _set_cell_surface(self, i, j, value):
            if value == '0':
                self.map_values[i][j] = self.service.wall
            else:
                self.map_values[i][j] = self.service.get_random_floor()

    class Objects(AbstractObjects):
        def get_objects(self, game_map):
            return self.objects


class RandomMap(MapFactory):
    yaml_tag = "!random_map"

    class Map(AbstractMap):
        def _set_cell_surface(self, i, j, value):
            super()._set_cell_surface(i, j, 0.15)

    class Objects(AbstractObjects):
        def get_objects(self, game_map):
            self._set_objects_and_allies(game_map)

            for enemy_prototype in self.service.prototypes.enemies:
                for i in range(random.randint(0, 5)):
                    enemy_clone = copy(enemy_prototype)
                    enemy_clone.position = \
                        self._get_random_empty_cell(game_map)
                    self.objects.append(enemy_clone)

            return self.objects


class EmptyMap(MapFactory):
    yaml_tag = "!empty_map"

    class Map(AbstractMap):
        def _set_cell_surface(self, i, j, value):
            super()._set_cell_surface(i, j, 0.1)

    class Objects(AbstractObjects):
        def get_objects(self, game_map):
            self._set_stairs(game_map)
            return self.objects


class SpecialMap(MapFactory):
    yaml_tag = "!special_map"

    class Map(AbstractMap):
        def _set_cell_surface(self, i, j, value):
            super()._set_cell_surface(i, j, 0.2)

    class Objects(AbstractObjects):
        def get_objects(self, game_map):
            self._set_objects_and_allies(game_map)

            for enemy_name, amount in self.config.items():
                enemy_prototype = \
                    self.service.prototypes.get_enemy_by_name(enemy_name)
                for _ in range(amount):
                    enemy_clone = copy(enemy_prototype)
                    enemy_clone.position = \
                        self._get_random_empty_cell(game_map)
                    self.objects.append(enemy_clone)

            return self.objects


class Service:
    def __init__(self, game):
        self.game = game
        self.sprite_factory = game.sprite_factory
        self.wall = self.sprite_factory.get_sprite_for_wall()
        self.prototypes = None

    def get_random_floor(self):
        return self.sprite_factory.get_sprite_for_floor()

    def service_init(self, full=True):
        file = open("objects.yml", "r")
        if full:
            object_list_dict = yaml.load(file.read())
            self.prototypes = PrototypeList()

            for obj_name, obj_dict in object_list_dict['objects'].items():
                obj = self.prototypes.get_object_by_name(obj_name)
                obj.sprite_icon_path = obj_dict['sprite'][0]
                obj.action = \
                    self.game.actions.get_action_by_name(obj_dict['action'])
                obj.min_count = obj_dict['min-count']
                obj.max_count = obj_dict['max-count']

            for ally_name, ally_dict in object_list_dict['ally'].items():
                ally = self.prototypes.get_ally_by_name(ally_name)
                ally.sprite_icon_path = ally_dict['sprite'][0]
                ally.action = \
                    self.game.actions.get_action_by_name(ally_dict['action'])
                ally.min_count = ally_dict['min-count']
                ally.max_count = ally_dict['max-count']

            for enemy_name, enemy_dict in object_list_dict['enemies'].items():
                sprite = enemy_dict['sprite'][0]
                enemy = self.prototypes.get_enemy_by_name(enemy_name, enemy_dict)
                enemy.sprite_icon_path = sprite

        for obj in self.prototypes.objects:
            obj.sprite = self.game.sprite_factory.get_sprite_for_object(obj)
            obj.sprite.redraw(self.game.size)

        for ally in self.prototypes.allies:
            ally.sprite = self.game.sprite_factory.get_sprite_for_object(ally)
            ally.sprite.redraw(self.game.size)

        for enemy in self.prototypes.enemies:
            enemy.sprite = \
                self.game.sprite_factory.get_sprite_for_object(enemy)
            enemy.sprite.redraw(self.game.size)

        file.close()

        if full:
            file = open("levels.yml", "r")
            self.game.level_list = yaml.load(file.read())['levels']
            self.game.level_list.append({'map': EndMap.Map(),
                                         'obj': EndMap.Objects()})
            file.close()
