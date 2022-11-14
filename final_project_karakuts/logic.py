from random import choice


class GameEngine:
    objects = []
    map = None
    working = True
    subscribers = set()
    score = 0.
    game_process = True
    show_help = False
    game_over = False
    sprite_size = None

    def __init__(self, hero, service):
        self.hero = hero
        self.service = service
        self.level = -1

    def subscribe(self, obj):
        self.subscribers.add(obj)

    def unsubscribe(self, obj):
        if obj in self.subscribers:
            self.subscribers.remove(obj)

    def notify(self, message):
        for i in self.subscribers:
            i.update(message)

    def interact(self):
        for obj in self.objects:
            if list(obj.position) == self.hero.position:
                self.delete_object(obj)
                obj.interact(self, self.hero)

    def __set_position(self, position_x, position_y):
        self.score -= 0.02
        if self.is_wall(self.map[position_y][position_x]):
            return
        if self.__is_stairs(position_x, position_y):
            if self.hero.exp < self.hero.exp_to_level_up and self.level != 0:
                self.notify('Not enough exp to level up!')
                return
        self.hero.position = [position_x, position_y]
        self.interact()

    def move_up(self):
        position_x = self.hero.position[0]
        position_y = self.hero.position[1] - 1
        self.__set_position(position_x, position_y)

    def move_down(self):
        position_x = self.hero.position[0]
        position_y = self.hero.position[1] + 1
        self.__set_position(position_x, position_y)

    def move_left(self):
        position_x = self.hero.position[0] - 1
        position_y = self.hero.position[1]
        self.__set_position(position_x, position_y)

    def move_right(self):
        position_x = self.hero.position[0] + 1
        position_y = self.hero.position[1]
        self.__set_position(position_x, position_y)

    def get_random_action(self):
        actions = [self.move_right, self.move_left,
                   self.move_up, self.move_down]

        return choice(actions)

    def is_wall(self, cell):
        return cell == self.service.wall

    def __is_stairs(self, position_x, position_y):
        for object_instance in self.objects:
            if object_instance.name == 'stairs' \
                    and object_instance.position == (position_x, position_y):
                return True

    def load_map(self, game_map):
        self.map = game_map

    def add_size(self, sprite_size):
        self.sprite_size = sprite_size

    def redraw_objects(self):
        for object_instance in self.objects:
            object_instance.sprite.redraw(self.sprite_size)

    def redraw_surface(self):
        for row in self.map:
            for cell in row:
                cell.redraw(self.sprite_size)

    def add_object(self, obj):
        self.objects.append(obj)

    def add_objects(self, objects):
        self.objects.extend(objects)

    def delete_object(self, obj):
        self.objects.remove(obj)
