"""Generation of train scenes (physically plausible)"""

import colorsys
import math
import random

import unreal_engine as ue
from unreal_engine import FLinearColor, FRotator, FVector, FTransform
from unreal_engine.classes import SpawnManager

from scene import Scene
from actors.object import Object
from actors.parameters import CameraParams
from actors.parameters import FloorParams
from actors.parameters import LightParams
from actors.parameters import ObjectParams
from actors.parameters import OccluderParams
from actors.parameters import WallsParams
from actors.parameters import camera_location
from tools.materials import get_random_material


class BoundingBox:
    def __init__(self, params):
        if isinstance(params, OccluderParams):
            if params.start_up:
                self._min = FVector(-200, 0, 0)
                self._max = FVector(200, 10, 0)
            else:
                self._min = FVector(-200, 0, 0)
                self._max = FVector(200, 200, 0)
        elif isinstance(params, ObjectParams):
            self._min = FVector(-50, -50, 0)
            self._max = FVector(50, 50, 0)
        else:
            raise ValueError('unsuported params for bounding box')

        self._transform = FTransform()
        self._transform.translation = params.location
        self._transform.rotation = params.rotation
        self._transform.scale = params.scale

    def intersect(self, other):
        return SpawnManager.Intersect(
            self._min, self._max, self._transform,
            other._min, other._max, other._transform)


class Train(Scene):
    @property
    def name(self):
        return 'train'

    @property
    def description(self):
        return 'physically plausible train scene'

    def __init__(self, world, saver):
        super().__init__(world, saver, 'train')
        self._is_valid = True

    def generate_parameters(self):
        """Pick random parameters for all the objects in the scene"""
        # first generate the 'constants' of the scene: camera, floor and lights
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

        # choose the train scenario to render, 'collision' maximizes collision
        # between objects, 'wall' scenario with the objects going above the
        # wall, 'random' is a fully random scenario.
        scenarios = 2 * ['random', 'collision'] + ['wall']
        scenario = random.choice(scenarios)

        # the bounding boxes of each actor
        self._boxes = {}

        # generate the walls
        if scenario == 'wall':
            self.generate_walls(0.7, 900)
        elif random.uniform(0, 1) <= 0.3:
            self.generate_walls(4, 2000)

        # generate the occluders
        noccluders = random.randint(0, 2)
        for n in range(noccluders):
            while self.generate_occluder(n) is False:
                pass

        # generate the objects
        if scenario == 'random':

            self.generate_random_objects(random.randint(1, 3))
        elif scenario == 'collision':
            self.generate_collision_objects()
        else:  # 'wall' scenario
            self.generate_above_wall_objects()

        return True

    def generate_random_position(self, mesh, is_occluder=False):
        if is_occluder is True:
            scale = FVector(
                random.uniform(0.5, 1.5),
                1,
                random.uniform(0.5, 3))
            location = FVector(
                random.uniform(200, 700),
                random.uniform(-500, 500),
                0)
        else:
            s = random.uniform(0.8, 2.5)
            scale = FVector(s, s, s)
            location = FVector(
                random.uniform(200, 800),
                random.uniform(-800, 800),
                0)

        rotation = FRotator(0, 0, random.uniform(-180, 180))

        return location, rotation, scale

    def generate_walls(self, max_height, max_depth):
        self.params['walls'] = WallsParams(
            material=get_random_material('Wall'),
            height=random.uniform(0.3, max_height),
            length=random.uniform(1500, 5000),
            depth=random.uniform(800, max_depth))

    def generate_occluder(self, n):
        nmoves = random.randint(0, 3)
        moves = []
        for m in range(nmoves):
            if len(moves) == 0:
                moves.append(random.randint(0, 200))
            elif moves[-1] + 20 < 200:
                moves.append(random.randint(moves[-1] + 20, 200))

        position = self.generate_random_position(
            '/Game/Meshes/OccluderWall', is_occluder=True)

        self.params[f'occluder_{n+1}'] = OccluderParams(
            material=get_random_material(
                'Wall', self.params['Floor'].material),
            location=position[0],
            rotation=position[1],
            scale=position[2],
            moves=moves,
            speed=random.uniform(1, 5),
            warning=True,
            overlap=True,
            start_up=random.choice([True, False]))

        # compute the bounding box of the occluder and make sure it does not
        # overlap any other object
        box = BoundingBox(self.params[f'occluder_{n+1}'])
        for b in self._boxes.values():
            if box.intersect(b):
                return False
        # no overlap, add the bounding box for further intersection checks
        self._boxes[f'occluder_{n+1}'] = box
        return True

    def generate_random_objects(self, nobjects):
        """Generate random objects at random positions"""
        for n in range(nobjects):
            mesh = random.choice([m for m in Object.shape.keys()] + ['Sphere'])

            position = self.generate_random_position(Object.shape[mesh])

            random_force = random.randint(0, 2)
            # if random_force == 0, the force is totally random
            if random_force == 0:
                vforce = []
                for i in range(3):
                    vforce.append(random.choice([-4, -3, -2, 2, 3, 4]))
                    vforce.append(random.uniform(3, 4))
                # the vertical force is necessarly positive
                vforce[4] = abs(vforce[4])
                force = FVector(
                    vforce[0] * math.pow(10, vforce[1]),
                    vforce[2] * math.pow(10, vforce[3]),
                    vforce[4] * math.pow(10, vforce[5]))

            # if random_force == 1, the force is directed in the camera range
            elif random_force == 1:
                collision_point = FVector(
                    random.uniform(300, 700),
                    random.uniform(-200, 200),
                    0)

                dir_force = [
                    collision_point.x - position[0].x,
                    collision_point.y - position[0].y,
                    random.randint(2, 4)]
                intensity = [
                    random.uniform(1.5, 1.8),
                    random.uniform(1.5, 1.8),
                    random.uniform(3, 4)]
                force = FVector(
                    dir_force[0] * math.pow(10, intensity[0]),
                    dir_force[1] * math.pow(10, intensity[1]),
                    dir_force[2] * math.pow(10, intensity[2]))

            # if random_force == 2, the force is null
            else:
                force = FVector(0, 0, 0)

            self.params[f'object_{n+1}'] = ObjectParams(
                mesh=mesh,
                material=get_random_material('Object'),
                location=position[0],
                rotation=position[1],
                scale=position[2],
                mass=1,
                initial_force=force,
                warning=True,
                overlap=False)
            self._boxes[f'object_{n+1}'] = BoundingBox(
                self.params[f'object_{n+1}'])

    def generate_collision_objects(self):
        """Generate 3 objects in order to maximize collision

        A collision point is randomly chosen, the 3 objects have an initial
        force in the direction of the collision point.

        """
        nobjects = 3
        collision_point = FVector(
            random.uniform(200, 700),
            random.uniform(-300, 300),
            0)

        for n in range(nobjects):
            mesh = random.choice([m for m in Object.shape.keys()] + ['Sphere'])

            position = self.generate_random_position(Object.shape[mesh])

            dir_force = [
                collision_point.x - position[0].x,
                collision_point.y - position[0].y,
                random.randint(2, 4)]
            intensity = [
                random.uniform(1.5, 1.8),
                random.uniform(1.5, 1.8),
                random.uniform(3, 4)]
            force = FVector(
                dir_force[0] * math.pow(10, intensity[0]),
                dir_force[1] * math.pow(10, intensity[1]),
                dir_force[2] * math.pow(10, intensity[2]))

            self.params[f'object_{n+1}'] = ObjectParams(
                mesh=mesh,
                material=get_random_material('Object'),
                location=position[0],
                rotation=position[1],
                scale=position[2],
                mass=1,
                initial_force=force,
                warning=True,
                overlap=False)
            self._boxes[f'object_{n+1}'] = BoundingBox(
                self.params[f'object_{n+1}'])

    def generate_above_wall_objects(self):
        nobjects = 3
        nobjects_r = random.randint(0, 2)
        self.generate_random_objects(nobjects_r)

        collision_point = FVector(
            random.uniform(800, 1000),
            random.uniform(-300, 300),
            0)

        for n in range(nobjects - nobjects_r):
            mesh = random.choice([m for m in Object.shape.keys()] + ['Sphere'])

            position = self.generate_random_position(Object.shape[mesh])

            dir_force = [
                collision_point.x - position[0].x,
                collision_point.y - position[0].y,
                random.randint(3, 4)]
            intensity = [
                random.uniform(1.5, 1.8),
                random.uniform(1.5, 1.8),
                random.uniform(3.7, 4)]
            force = FVector(
                dir_force[0] * math.pow(10, intensity[0]),
                dir_force[1] * math.pow(10, intensity[1]),
                dir_force[2] * math.pow(10, intensity[2]))

            self.params[f'object_{n+nobjects_r+1}'] = ObjectParams(
                mesh=mesh,
                material=get_random_material('Object'),
                location=position[0],
                rotation=position[1],
                scale=position[2],
                mass=1,
                initial_force=force,
                warning=True,
                overlap=False)
            self._boxes[f'object_{n+nobjects_r+1}'] = BoundingBox(
                self.params[f'object_{n+nobjects_r+1}'])

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

        # make sure there is no overlap between objects at spawn time
        actors_to_check = [
            actor.actor for name, actor in self.actors.items()
            if 'object' in name.lower() or 'occluder' in name.lower()]

        actors_overlapped = actors_to_check.copy()
        if 'walls' in self.actors:
            actors_overlapped += [
                self.actors['walls'].front.actor,
                self.actors['walls'].left.actor,
                self.actors['walls'].right.actor]

        for actor in actors_to_check:
            for other in actors_overlapped:
                if SpawnManager.IsOverlapping(actor, other):
                    ue.log(f'ERROR: overlapping actors detected: '
                           f'{actor.get_name()} and {other.get_name()}')
                    self._is_valid = False
                    return

        # apply force on moving objects
        for name, actor in self.actors.items():
            if 'object' in name.lower():
                actor.set_force(actor.initial_force)

    def is_valid(self):
        return self._is_valid and super().is_valid()

    def is_possible(self):
        return True

    def is_test_scene(self):
        return False

    def capture(self):
        self.saver.capture(ignored_actors=[], status=self.get_status())

    def is_over(self):
        return self.run == 1
