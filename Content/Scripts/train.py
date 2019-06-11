# coding: utf-8

import random
import math
from scene import Scene
from unreal_engine import FVector, FRotator, FLinearColor
from actors.parameters import LightParams, CameraParams, ObjectParams, OccluderParams
from tools.materials import get_random_material
from actors.object import Object


class Train(Scene):
    @property
    def name(self):
        return 'train'

    @property
    def description(self):
        return 'physically plausible train scene'

    def __init__(self, world, saver):
        super().__init__(world, saver)

    def generate_parameters(self):
        super().generate_parameters()

        self.params['Camera'] = CameraParams(
            location=FVector(0, 0, random.uniform(175, 225)),
            rotation=FRotator(0, random.uniform(-10, 10), 0))

        self.params['Light'] = LightParams(
            type='SkyLight',
            color=FLinearColor(random.uniform(0.6, 1.0), random.uniform(0.6, 1.0), random.uniform(0.6, 1.0), 1.0))

        nobjects = random.randint(1, 3)
        unsafe_zones = []
        noccluders = random.randint(0, 2)
        self.is_occluded = True if noccluders != 0 else False
        location = FVector()
        rotation = FVector()
        scale = 0

        for n in range(nobjects):
            vforce = []
            for i in range(3):
                vforce.append(random.choice([-4, -3, -2, 2, 3, 4]))
                vforce.append(random.uniform(3, 4))
            # the vertical force is necessarly positive
            vforce[4] = abs(vforce[4])
            force = FVector(vforce[0] * math.pow(10, vforce[1]),
                            vforce[2] * math.pow(10, vforce[3]),
                            vforce[4] * math.pow(10, vforce[5]))
            previous_size = len(unsafe_zones)
            for try_index in range(100):
                # scale in [1, 2]
                scale = random.uniform(1, 2)
                location = FVector(
                    random.uniform(200, 700),
                    random.uniform(-500, 500),
                    0)
                rotation = FRotator(
                    0, 0, 360 * random.random())
                # TODO apply angle
                new_zone = [FVector(location.x - 50 * scale, location.y + 50 * scale, location.z),
                            FVector(location.x + 50 * scale, location.y - 50 * scale, location.z)]
                if self.check_spawning_location(new_zone, unsafe_zones):
                    unsafe_zones.append(new_zone)
                    break
            if len(unsafe_zones) == previous_size:
                continue
            # mesh = random.choice([m for m in Object.shape.keys()] + ['Sphere'])
            mesh = 'Cube'
            self.params['object_{}'.format(n + 1)] = ObjectParams(
                mesh=mesh,
                material=get_random_material('Object'),
                location=location,
                rotation=rotation,
                scale=FVector(scale, scale, scale),
                mass=1,
                initial_force=force,
                warning=True,
                overlap=False)

        for n in range(noccluders):
            previous_size = len(unsafe_zones)
            for try_index in range(100):
                location = FVector(
                    random.uniform(200, 700),
                    random.uniform(-500, 500),
                    0)
                rotation = FRotator(
                    0, 0, random.uniform(-180, 180))
                scale = FVector(random.uniform(0.5, 1.5), 1, random.uniform(0.5, 1.5))
                #  TODO apply rotation
                new_zone = [FVector(location.x - 50 * scale.x, location.y + 50 * scale.y, location.z),
                            FVector(location.x + 50 * scale.x, location.y - 50 * scale.y, location.z)]
                if self.check_spawning_location(new_zone, unsafe_zones):
                    unsafe_zones.append(new_zone)
                    break
            if len(unsafe_zones) == previous_size:
                continue
            nmoves = random.randint(0, 3)
            moves = []
            for m in range(nmoves):
                if len(moves) == 0:
                    moves.append(random.randint(0, 200))
                else:
                    moves.append(random.randint(moves[-1], 200))
            self.params['occluder_{}'.format(n + 1)] = OccluderParams(
                material=get_random_material('Wall'),
                location=location,
                rotation=rotation,
                scale=scale,
                moves=moves,
                speed=random.uniform(1, 5),
                warning=True,
                overlap=True,
                start_up=random.choice([True, False]))

    def check_spawning_location(self, new_object_location, all_locations):
        #  new_object_location is an array of 2 3D points representing locations of unsafe square (top left corner
        #  and bottom right one)
        #  all_locations is an array of array same shape of new_object_location
        #  https://stackoverflow.com/questions/306316/determine-if-two-rectangles-overlap-each-other
        for location in all_locations:
            if (location[0].x < new_object_location[1].x and location[1].x > new_object_location[0].x and
                    location[0].y > new_object_location[1].y and location[1].y < new_object_location[0].y):
                return False  # it intersect
        return True  # it doesn't intersect

    def stop_run(self, scene_index, total):
        super().stop_run()
        if not self.saver.is_dry_mode:
            self.saver.save(self.get_scene_subdir(scene_index, total))
            # reset actors if it is the last run
            self.saver.reset(True)
        self.del_actors()
        self.run += 1

    def play_run(self):
        if self.run == 1:
            return
        # ue.log("Run 1/1: Possible run")
        super().play_run()
        for name, actor in self.actors.items():
            if 'object' in name.lower() and random.choice([0, 1, 2]) != 0:
                actor.set_force(actor.initial_force)

    def is_possible(self):
        return True

    def is_test_scene(self):
        return False

    def capture(self):
        ignored_actors = []
        self.saver.capture(ignored_actors, self.get_status())

    def is_over(self):
        return True if self.run == 1 else False
