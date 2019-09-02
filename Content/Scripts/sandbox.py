import colorsys
import random

import unreal_engine as ue
from unreal_engine import FLinearColor, FRotator, FVector

from scene import Scene
from actors.parameters import CameraParams
from actors.parameters import FloorParams
from actors.parameters import LightParams
from actors.parameters import ObjectParams
from actors.parameters import WallsParams
from actors.parameters import camera_location
from tools.materials import get_random_material


class Sandbox(Scene):
    @property
    def name(self):
        return 'train sandbox'

    @property
    def description(self):
        return 'for debugging only'

    def __init__(self, world, saver):
        super().__init__(world, saver, 'train')

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

        self.params['walls'] = WallsParams(
            material=get_random_material('Wall'),
            height=random.uniform(0.3, 4),
            length=random.uniform(1500, 5000),
            depth=random.uniform(800, 2000))

        self.params['object_1'] = ObjectParams(
            mesh='Sphere',
            material=get_random_material('Object'),
            location=FVector(300, 0, 0),
            rotation=FRotator(0, 0, 0),
            scale=FVector(2, 2, 2),
            mass=1,
            initial_force=FVector(0, 0, 0),
            # initial_force=FVector(-10**4, 0, 0),
            warning=True,
            overlap=False)

        self.params['object_2'] = ObjectParams(
            mesh='Sphere',
            material=get_random_material('Object'),
            location=FVector(500, 300, 0),
            rotation=FRotator(0, 0, 0),
            scale=FVector(2, 2, 2),
            mass=1,
            initial_force=FVector(-10**4, -10**4, 0),
            # initial_force=FVector(0, 0, 0),
            warning=True,
            overlap=False)

    @staticmethod
    def make_color(min_value=0.5, max_value=1.0):
        h = random.uniform(0.05, 0.18)
        s = 0.3
        v = random.uniform(min_value, max_value)
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return FLinearColor(r, g, b, 1.0)

    def stop_run(self, scene_index, total):
        super().stop_run()

        if not self.saver.is_dry_mode:
            self.saver.save(self.get_scene_subdir(scene_index, total))
            self.saver.reset(True)
        self.del_actors()
        self.run += 1

    def play_run(self):
        if self.is_over():
            return

        super().play_run()
        for name, actor in self.actors.items():
            if 'object' in name.lower():
                actor.set_force(actor.initial_force)

    def is_possible(self):
        return True

    def is_test_scene(self):
        return False

    def capture(self):
        self.saver.capture(ignored_actors=[], status=self.get_status())

    def is_over(self):
        return self.run == 1

    def tick(self):
        # o1 = self.actors['object_1']
        # overlapping = []
        # overlapping = o1.actor.GetOverlappingActors()
        # ue.log(overlapping)

        super().tick()
