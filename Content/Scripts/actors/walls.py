from actors.wall import Wall
from actors.parameters import WallsParams

"""
Walls is a wrapper class that make 3 walls spawn.
"""


class Walls():
    def __init__(self, world, params=WallsParams):
        self.get_parameters(params)
        self.front = Wall(
            world, "Front",
            self.length, self.depth,
            self.height, self.material, self.overlap, self.warning, self.z)

        self.right = Wall(
            world, "Right",
            self.length, self.depth,
            self.height, self.material, self.overlap, self.warning, self.z)

        self.left = Wall(
            world, "Left",
            self.length, self.depth,
            self.height, self.material, self.overlap, self.warning, self.z)

        self.is_valid = True

    def actor_destroy(self):
        self.front.actor_destroy()
        self.right.actor_destroy()
        self.left.actor_destroy()

    def get_parameters(self, params):
        self.depth = params.depth
        self.length = params.length
        self.height = params.height
        self.z = params.z
        self.material = params.material
        self.overlap = False
        self.warning = False

    def get_status(self):
        return {
            'depth': self.depth,
            'length': self.length,
            'height': self.height}
