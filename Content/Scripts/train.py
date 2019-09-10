"""Generation of train scenes (physically plausible)"""

import colorsys
import importlib
import math
import random

from unreal_engine import FLinearColor, FRotator, FVector
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

    def is_valid(self):
        """Returns True if the scene and all the actors are valid"""
        return self._is_valid and super().is_valid()

    def is_possible(self):
        return True

    def is_test_scene(self):
        return False

    def capture(self):
        self.saver.capture(ignored_actors=[], status=self.get_status())

    def is_over(self):
        """Return True if the scene has been rendered"""
        return self.run == 1

    @staticmethod
    def make_color(min_value=0.5, max_value=1.0):
        h = random.uniform(0.05, 0.18)
        s = 0.3
        v = random.uniform(min_value, max_value)
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return FLinearColor(r, g, b, 1.0)

    def stop_run(self, scene_index, total):
        """Save the scene and delete the actors"""
        super().stop_run()

        if not self.saver.is_dry_mode:
            self.saver.save(self.get_scene_subdir(scene_index, total))
            self.saver.reset(True)

        self.del_actors()
        self.run += 1

    def play_run(self):
        """Spawn the actors and starts the movie

        This method generates parameters for the dynamic actors (objects and
        occluders), making sure there is no overlap between actors. It spawns
        each actor and apply a physical force to objects.

        """
        # a safe guard to avoid regenerating a scene is already spawned
        if self.is_over():
            return

        # spawn the static actors (lights, floor)
        super().spawn_actors()

        self.generate_spawn_moving_actors()

        # apply force on moving objects
        for name, actor in self.actors.items():
            if 'object' in name.lower():
                actor.set_force(actor.initial_force)

    def is_overlapping(self, actor):
        """Returns True if `actor` overlaps another actor in the scene"""
        actors_to_check = [
            actor.actor for name, actor in self.actors.items()
            if 'object' in name.lower() or 'occluder' in name.lower()]

        if 'walls' in self.actors:
            actors_to_check += [
                self.actors['walls'].front.actor,
                self.actors['walls'].left.actor,
                self.actors['walls'].right.actor]

        for other in actors_to_check:
            if SpawnManager.IsOverlapping(actor.actor, other):
                return True
        return False

    def spawn(self, name, params, check_overlap=True):
        """Spawns a new actor in the world

        This method dynamically import the actor's class based on its name,
        instanciate it (ie spawn the actor), make sure the spawned actor does
        not overlap another actor (if so the freshly spawned actor is
        destryed). It finally updated the internal dictionnaries registering
        the living actors and their parameters (needed to retrieve the status
        and scene's validity).

        Parameters
        ----------
        name : str
            The name of the actor being spawned. The actor's class is guessed
            from its name.
        params : dict
            The parameters of the actor (mesh, position, force, etc...)
        check_overlap : bool, optional
            When True, make sure the spawned actor does not overlap an existing
            actor. Default to True.

        Returns
        -------
        False if `check_overlap` is True and the spawned actor is overlappîng
        another actor, True otherwise.

        """
        # dynamically import the actor's class
        module_path = "actors.{}".format(name.lower().split('_')[0])
        module = importlib.import_module(module_path)
        actor_class = getattr(module, name.split('_')[0].title())

        # instanciate the actor (spawn it in the world)
        actor = actor_class(world=self.world, params=params)

        # make sure the new actor does not overlap any existing actor
        if check_overlap is True and self.is_overlapping(actor):
            actor.actor_destroy()
            return False

        # update the actros and parameters dictionnaries
        self.params[name] = params
        self.actors[name] = actor
        return True

    def generate_parameters(self):
        """Generates only non-mobile actors

        To deal with potential ovelaping of actors during spawn, the parameters
        for mobile actors (objects and occluders) are generated during the call
        to play_run().

        This method generates random parameters for camera, lights and floor of
        a train scene.

        """
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

    def generate_spawn_moving_actors(self):
        """Manages moving actors in the scene (actors and occluders)

        The objects are generated according to 3 scenarios: random, collision
        and walls. Random generates completely random parameters. Collision
        maximize the probabilty for a collision to appens between the actors
        (by generating a collision point and related actors forces). Walls
        scenario maximize the probability that actors jump above the background
        wall.

        """
        # choose the train scenario to render
        scenario = random.choice(2 * ['random', 'collision'] + ['walls'])

        # generate the walls
        if scenario == 'walls' or random.uniform(0, 1) <= 0.3:
            params = self.generate_walls(scenario)
            self.spawn('walls', params, check_overlap=False)

        # generate the occluders
        noccluders = random.randint(0, 2)
        for n in range(noccluders):
            is_ok = False
            while is_ok is False:
                params = self.generate_occluder()
                is_ok = self.spawn(f'occluder_{n+1}', params)

        # generate the objects
        collision = self.generate_collision_point(scenario)
        nobjects = self.generate_nobjects()
        for n in range(nobjects):
            is_ok = False
            while is_ok is False:
                if scenario == 'random':
                    params = self.generate_object_random()
                elif scenario == 'collision':
                    params = self.generate_object_collision(collision)
                else:
                    params = self.generate_object_wall(collision)
                is_ok = self.spawn(f'object_{n+1}', params)

    @staticmethod
    def generate_nobjects():
        """Returns 1 at 15%, 2 at 25%, 3 at 60%"""
        rand = random.uniform(0, 1)
        if rand < 0.15:
            return 1
        if rand < 0.35:
            return 2
        return 3

    @staticmethod
    def generate_collision_point(scenario):
        """Returns a random point for actors collision"""
        point = FVector(random.uniform(200, 700), random.uniform(-300, 300), 0)
        if scenario == 'walls':
            point.x = random.uniform(800, 1000)
        return point

    def generate_position(self, is_occluder=False):
        """Returns a random position for a new object or occluder

        Position is a location, a rotation and a scale.

        """
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

    def generate_walls(self, scenario):
        """Return random parameters for background walls"""
        max_height = 4
        max_depth = 2000
        if scenario == 'walls':
            max_height = 0.7
            max_depth = 900

        return WallsParams(
            material=get_random_material('Wall'),
            height=random.uniform(0.3, max_height),
            length=random.uniform(1500, 5000),
            depth=random.uniform(800, max_depth))

    def generate_occluder(self):
        """Return random parameters for an occluder"""
        nmoves = random.randint(0, 3)
        moves = []
        for m in range(nmoves):
            if len(moves) == 0:
                moves.append(random.randint(0, 200))
            elif moves[-1] + 30 < 200:
                moves.append(random.randint(moves[-1] + 30, 200))

        position = self.generate_position(is_occluder=True)

        return OccluderParams(
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

    def generate_object_random(self):
        """Returns random parameters for an object in 'random' scenario"""
        """Generate a random object at random position"""
        mesh = random.choice([m for m in Object.shape.keys()] + ['Sphere'])
        position = self.generate_position(Object.shape[mesh])

        random_force = random.randint(0, 4)
        # the force is totally random
        if random_force >= 2:
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
                random.uniform(1.6, 1.8),
                random.uniform(1.6, 1.8),
                random.uniform(3, 4)]
            force = FVector(
                dir_force[0] * math.pow(10, intensity[0]),
                dir_force[1] * math.pow(10, intensity[1]),
                dir_force[2] * math.pow(10, intensity[2]))

        # if random_force == 0, the force is null
        else:
            force = FVector(0, 0, 0)

        return ObjectParams(
            mesh=mesh,
            material=get_random_material('Object'),
            location=position[0],
            rotation=position[1],
            scale=position[2],
            mass=1,
            initial_force=force,
            warning=True,
            overlap=False)

    def generate_object_collision(self, collision):
        """Returns random parameters for an object in 'collision' scenario"""
        mesh = random.choice([m for m in Object.shape.keys()] + ['Sphere'])
        position = self.generate_position(Object.shape[mesh])
        dir_force = [
            collision.x - position[0].x,
            collision.y - position[0].y,
            random.randint(2, 4)]
        intensity = [
            random.uniform(1.6, 1.8),
            random.uniform(1.6, 1.8),
            random.uniform(3, 4)]
        force = FVector(
            dir_force[0] * math.pow(10, intensity[0]),
            dir_force[1] * math.pow(10, intensity[1]),
            dir_force[2] * math.pow(10, intensity[2]))

        return ObjectParams(
            mesh=mesh,
            material=get_random_material('Object'),
            location=position[0],
            rotation=position[1],
            scale=position[2],
            mass=1,
            initial_force=force,
            warning=True,
            overlap=False)

    def generate_object_wall(self, collision):
        """Returns random parameters for an object in 'walls' scenario"""
        mesh = random.choice([m for m in Object.shape.keys()] + ['Sphere'])
        position = self.generate_position(Object.shape[mesh])
        dir_force = [
            collision.x - position[0].x,
            collision.y - position[0].y,
            random.randint(3, 4)]
        intensity = [
            random.uniform(1.6, 1.8),
            random.uniform(1.6, 1.8),
            random.uniform(3.7, 4)]
        force = FVector(
            dir_force[0] * math.pow(10, intensity[0]),
            dir_force[1] * math.pow(10, intensity[1]),
            dir_force[2] * math.pow(10, intensity[2]))

        return ObjectParams(
            mesh=mesh,
            material=get_random_material('Object'),
            location=position[0],
            rotation=position[1],
            scale=position[2],
            mass=1,
            initial_force=force,
            warning=True,
            overlap=False)
