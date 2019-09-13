import unreal_engine as ue
from unreal_engine.classes import Material
from actors.base_mesh import BaseMesh
from actors.parameters import OccluderParams

"""A vertical plane that falls and gets up by itself.

The occluder spawns verticaly.

About the moves variable: it is an array which shall contain the frames when
you want the occluder to initiate a movement (it moves at 1 degree per frame).
ergo, if you want the occluder to move at the first frame, put 0 in the array.
The occluder will come down. If you put 50, it won't have time to fully go
down: it will rise again at the 50th frame

"""


class Occluder(BaseMesh):
    class_name = '/Game/Occluder.Occluder_C'

    def __init__(self, world, params=OccluderParams()):
        super().__init__(world.actor_spawn(ue.load_class(self.class_name)))
        self.get_parameters(params)
        self.set_parameters()

    def get_parameters(self, params):
        super().get_parameters(
            params.location,
            params.rotation,
            params.scale,
            params.friction,
            params.restitution,
            params.overlap,
            params.warning,
            '/Game/Meshes/OccluderWall')

        self.material = ue.load_object(Material, params.material)
        self.speed = params.speed

        # array of numbers from 1 to 200
        self.moves = params.moves
        self.moving = False
        self.up = params.start_up
        if self.up is False:
            self.rotation.roll = 90
        self.count = -1

    def set_parameters(self):
        super().set_parameters()
        # self.get_mesh().set_simulate_physics(True)

    def move(self):
        """Make the Occluder fall and get up when called"""
        self.count += 1
        rotation = self.rotation
        if self.count in self.moves:
            if self.moving is False:
                if self.up is True:
                    rotation.roll += self.speed
                else:
                    rotation.roll -= self.speed
                self.moving = True
            else:
                if self.up is True:
                    rotation.roll += self.speed
                    self.up = False
                else:
                    rotation.roll -= self.speed
                    self.up = True
        elif self.moving is True:
            if self.warning and self.overlap:
                self.actor.bind_event(
                    'OnActorHit', self.moving_down_on_actor_hit)
            if self.up is True:
                rotation.roll += self.speed
            else:
                rotation.roll -= self.speed
        else:
            return

        # switch rotation direction downward if roll is 90 or upward if 0
        if rotation.roll >= 90:
            rotation.roll = 90
            self.up = False
            self.moving = False
        elif rotation.roll <= 0:
            rotation.roll = 0
            self.up = True
            self.moving = False

        self.set_rotation(rotation)
        self.location = self.actor.get_actor_location()

    def get_status(self):
        status = super().get_status()
        status['material'] = self.material.get_name()
        status['speed'] = self.speed
        status['moves'] = []
        for i in self.moves:
            status['moves'].append(i)
        return status

    def on_actor_overlap(self, me, other):
        super().on_actor_overlap(me, other)

    def on_actor_hit(self, me, other, *args):
        super().on_actor_hit(me, other)
        if 'occluder' in other.get_name().lower():
            self.is_valid = False

    def moving_down_on_actor_hit(self, me, other, *args):
        super().on_actor_hit(me, other)
        if self.up is True and self.moving is True:
            self.up = False

    def reset(self, params):
        super().reset(params)
        self.set_location(self.location)
        self.moving = False
        self.count = -1
        self.up = params.start_up
        if (self.up is False):
            self.rotation.roll = 90
