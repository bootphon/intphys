import random

from unreal_engine import FRotator, FVector
from actors.parameters import CameraParams
from actors.parameters import FloorParams
from actors.parameters import LightParams
from actors.parameters import ObjectParams
from actors.parameters import OccluderParams
from actors.parameters import WallsParams
from tools.materials import get_random_material
from train import Train


class Sandbox(Train):
    """Implements constrained scenarios for development/debugging

    The methods case_* are all invalid videos, they must fail for the program
    to be correct.

    TODO implement a method to automatically pass all the tests and make sure
    they all fail.

    """
    @property
    def name(self):
        return 'train sandbox'

    @property
    def description(self):
        return 'for debugging only'

    def play_run(self):
        if self.is_over():
            return

        self.generate_moving_actors_parameters()
        super().spawn_actors()

        # apply force on moving objects
        for name, actor in self.actors.items():
            if 'object' in name.lower():
                actor.set_force(actor.initial_force)

    def generate_parameters(self):
        self.params['Camera'] = CameraParams(
            location=FVector(0, 0, 180),
            rotation=FRotator(0, 0, 0))

        self.params['Floor'] = FloorParams(
            material=get_random_material('Floor'))

        self.params['Light'] = LightParams(type='SkyLight')

        self.params['Light_1'] = LightParams(
            type='SkyLight',
            location=FVector(0, 0, 30),
            color=self.make_color(0.9, 1.0),
            varIntensity=random.uniform(-0.2, 0.9))

    def generate_moving_actors_parameters(self):
        self.case_two_occluders_colliding()
        # self.case_ball_on_camera()
        # self.case_one_occluder()
        # self.case_one_object()
        # self.case_walls_overlap()

    def case_two_occluders_colliding(self):
        """A static occluder and a second one hitting/overlapping the first"""
        self.params['occluder_1'] = OccluderParams(
            material=get_random_material(
                'Wall', self.params['Floor'].material),
            location=FVector(600, 0, 0),
            rotation=FRotator(0, 0, 90),
            scale=FVector(1, 1, 1),
            moves=[],
            speed=random.uniform(1, 5),
            warning=True,
            overlap=False,
            start_up=True)

        self.params['occluder_2'] = OccluderParams(
            material=get_random_material(
                'Wall', self.params['Floor'].material),
            location=FVector(500, -300, 0),
            rotation=FRotator(0, 0, 0),
            scale=FVector(1, 1, 1),
            moves=[10, 100],
            speed=random.uniform(1, 5),
            warning=True,
            overlap=False,
            start_up=True)

        self.params['object_1'] = ObjectParams(
            mesh='Sphere',
            material=get_random_material('Object'),
            location=FVector(300, 0, 0),
            rotation=FRotator(0, 0, 0),
            scale=FVector(1, 1, 1),
            mass=1,
            initial_force=FVector(30**3, 0, 0),
            warning=True,
            overlap=False)

    def case_ball_on_camera(self):
        self.params['object_1'] = ObjectParams(
            mesh='Sphere',
            material=get_random_material('Object'),
            location=FVector(500, 0, 0),
            rotation=FRotator(0, 0, 0),
            scale=FVector(2, 2, 2),
            mass=1,
            initial_force=FVector(-30**3, 0, 0),
            warning=True,
            overlap=False)

    def case_one_occluder(self):
        """A static occluder"""
        self.params['occluder_1'] = OccluderParams(
            material=get_random_material(
                'Wall', self.params['Floor'].material),
            location=FVector(600, 0, 0),
            rotation=FRotator(0, 0, 90),
            scale=FVector(1, 1, 1),
            moves=[],
            # speed=random.uniform(1, 5),
            warning=True,
            overlap=False,
            start_up=False)

    def case_one_object(self):
        """A static object"""
        self.params['object_1'] = ObjectParams(
            mesh='Cube',
            material=get_random_material('Object'),
            location=FVector(100, 200, 0),
            rotation=FRotator(0, 0, 0),
            scale=FVector(1, 1, 1),
            mass=1,
            initial_force=FVector(0, 0, 0),
            warning=True,
            overlap=False)

    def case_walls_overlap(self):
        self.params['walls'] = WallsParams(
            material=get_random_material('Wall'),
            height=20,
            length=1000,
            depth=800)

        self.params['object_1'] = ObjectParams(
            mesh='Sphere',
            material=get_random_material('Object'),
            location=FVector(800, 0, 0),
            rotation=FRotator(0, 0, 0),
            scale=FVector(2, 2, 2),
            mass=1,
            initial_force=FVector(0, 0, 0),
            warning=True,
            overlap=False)
