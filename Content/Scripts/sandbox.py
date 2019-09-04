import colorsys
import random

import unreal_engine as ue
from unreal_engine import FLinearColor, FRotator, FVector

from train import Train
from actors.parameters import CameraParams
from actors.parameters import FloorParams
from actors.parameters import LightParams
from actors.parameters import ObjectParams
from actors.parameters import OccluderParams
from actors.parameters import WallsParams
from actors.parameters import camera_location
from tools.materials import get_random_material


class Sandbox(Train):
    @property
    def name(self):
        return 'train sandbox'

    @property
    def description(self):
        return 'for debugging only'

    def generate_parameters(self):
        self.params['Camera'] = CameraParams(
            location=camera_location(type='train'),
            rotation=FRotator(
                0,
                random.uniform(-10, 10),
                random.uniform(-10, 10)))

        self.params['Floor'] = FloorParams(
            material=get_random_material('Floor'))

        self.params['Light'] = LightParams(type='SkyLight')

        self.params['Light_1'] = LightParams(
            type='SkyLight',
            location=FVector(0, 0, 30),
            color=self.make_color(0.9, 1.0),
            varIntensity=random.uniform(-0.2, 0.9))

        self.case_two_occluders_colliding()
        # self.case_ball_on_camera()
        # self.case_one_occluder()
        # self.case_one_object()

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
            mesh='Sphere',
            material=get_random_material('Object'),
            location=FVector(300, 0, 0),
            rotation=FRotator(0, 0, 0),
            scale=FVector(2, 2, 2),
            mass=1,
            initial_force=FVector(0, 0, 0),
            warning=True,
            overlap=False)
