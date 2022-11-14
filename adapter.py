class MappingAdapter:
    def __init__(self, adaptee):
        self.adaptee = adaptee

    def lighten(self, grid):
        y_dim = len(grid)
        x_dim = len(grid[0])
        self.adaptee.set_dim((x_dim, y_dim))
        lights = self.__get_coords_array(grid, 1)
        self.adaptee.set_lights(lights)
        obstacles = self.__get_coords_array(grid, -1)
        self.adaptee.set_obstacles(obstacles)
        return self.adaptee.generate_lights()

    @staticmethod
    def __get_coords_array(grid, value):
        array = []
        for row_index, row in enumerate(grid):
            for column_index, grid_value in enumerate(row):
                if grid_value == value:
                    array.append((column_index, row_index))
        return array