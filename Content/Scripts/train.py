# coding: utf-8

import random
import math
import colorsys
from scene import Scene
from unreal_engine import FVector, FRotator, FLinearColor
from actors.parameters import LightParams, CameraParams, ObjectParams, OccluderParams, WallsParams
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
                rotation=FRotator(0, random.uniform(-10, 10), random.uniform(-10, 10)))

        self.params['Light_1'] = LightParams(
                type='SkyLight',
                location=FVector(0, 0, 30),
                color=self.make_color(0.9, 1.0))

        unsafe_zones = []
        noccluders = random.randint(0, 2)
        self.is_occluded = True if noccluders != 0 else False

        prob_walls = random.uniform(0, 1)
        scenarios = ['random', 'collision']
        scenarios = 2*scenarios+['wall']
        scenario = random.choice(scenarios)
        if scenario == 'random':
            # random scenario
            nobjects = random.randint(1, 3)
            self.generate_random_objects(nobjects, unsafe_zones)
            self.generate_walls(prob_walls, 4, 2000)
        elif scenario == 'collision':
            # scenario that maximizes collision between objects
            self.generate_collision_objects(unsafe_zones)
            self.generate_walls(prob_walls, 4, 2000)
        else:
            # scenario with the objects going above the Walls
            # always 3 objects, nobjects-nobjects_r are going above the Wall
            # nobjects_r are placed randomly
            self.generate_walls(0, 0.7, 900)
            nobjects = 3
            nobjects_r = random.randint(0, 2)
            self.generate_random_objects(nobjects_r, unsafe_zones)
            self.objects_above_walls_scenario(nobjects - nobjects_r, nobjects_r, unsafe_zones)

        for n in range(noccluders):
            previous_size = len(unsafe_zones)
            position = self.find_position("occ", unsafe_zones)
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
                material=get_random_material('Wall', self.params['Floor'].material),
                location=position[0],
                rotation=position[1],
                scale=position[2],
                moves=moves,
                speed=random.uniform(1, 5),
                warning=True,
                overlap=True,
                start_up=random.choice([True, False]))

    def generate_walls(self, prob_walls, max_height, max_depth):
        """Generate walls
        """
        if prob_walls <= 0.3:
            self.params['walls'] = WallsParams(
                material=get_random_material('Wall'),
                height=random.uniform(0.3, max_height),
                length=random.uniform(1500, 5000),
                depth=random.uniform(800, max_depth)
            )

    def generate_random_objects(self, nobjects, unsafe_zones):
        """Generate random objects at random positions

        Parameters
        ----------
        nobjects : int
            nobjects is the number of objects you want to generate
        unsafe_zones : list
            unsafe_zones is a list of existing unsafe zones (zones where an
            actor has already been placed)

        """
        for n in range(nobjects):
            previous_size = len(unsafe_zones)
            # find a position (location, rotation, scale)
            position = self.find_position("obj", unsafe_zones)
            if len(unsafe_zones) == previous_size:
                continue

            random_force = random.randint(0, 2)
            # if random_force == 0, the force is totally random
            if random_force == 0:
                vforce = []
                for i in range(3):
                    vforce.append(random.choice([-4, -3, -2, 2, 3, 4]))
                    vforce.append(random.uniform(3, 4))
                # the vertical force is necessarly positive
                vforce[4] = abs(vforce[4])
                force = FVector(vforce[0] * math.pow(10, vforce[1]),
                                vforce[2] * math.pow(10, vforce[3]),
                                vforce[4] * math.pow(10, vforce[5]))
            # if random_force == 1, the force is directed in the camera range
            elif random_force == 1:
                collision_point = FVector(
                    random.uniform(300, 700),
                    random.uniform(-200, 200),
                    0
                )
                dir_force = [collision_point.x - position[0].x,
                             collision_point.y - position[0].y,
                             random.randint(2, 4)]
                intensity = [random.uniform(1.5, 1.8), random.uniform(1.5, 1.8), random.uniform(3, 4)]
                force = FVector(dir_force[0] * math.pow(10, intensity[0]),
                                dir_force[1] * math.pow(10, intensity[1]),
                                dir_force[2] * math.pow(10, intensity[2]))
            # if random_force == 2, the force is null
            else:
                force = FVector(0, 0, 0)

            mesh = random.choice([m for m in Object.shape.keys()] + ['Sphere'])
            self.params['object_{}'.format(n + 1)] = ObjectParams(
                mesh=mesh,
                material=get_random_material('Object'),
                location=position[0],
                rotation=position[1],
                scale=position[2],
                mass=1,
                initial_force=force,
                warning=True,
                overlap=False)

    def generate_collision_objects(self, unsafe_zones):
        """
        Generate 3 objects in order to maximize collision
        A collision point is randomly chosen, the 3 objects have an initial
        force in the direction of the collision point
        """
        nobjects = 3
        collision_point = FVector(
            random.uniform(200, 700),
            random.uniform(-300, 300),
            0
        )
        for n in range(nobjects):
            previous_size = len(unsafe_zones)
            position = self.find_position("obj", unsafe_zones)
            if len(unsafe_zones) == previous_size:
                continue
            dir_force = [collision_point.x - position[0].x,
                         collision_point.y - position[0].y,
                         random.randint(2, 4)]
            intensity = [random.uniform(1.5, 1.8), random.uniform(1.5, 1.8), random.uniform(3, 4)]
            force = FVector(dir_force[0] * math.pow(10, intensity[0]),
                            dir_force[1] * math.pow(10, intensity[1]),
                            dir_force[2] * math.pow(10, intensity[2]))

            mesh = random.choice([m for m in Object.shape.keys()] + ['Sphere'])
            self.params['object_{}'.format(n + 1)] = ObjectParams(
                mesh=mesh,
                material=get_random_material('Object'),
                location=position[0],
                rotation=position[1],
                scale=position[2],
                mass=1,
                initial_force=force,
                warning=True,
                overlap=False)

    def objects_above_walls_scenario(self, nobjects, nprevious, unsafe_zones):
        """
        Generate objects, maximize objects being thrown above
        walls.
        """
        # nobjects = random.randint(1,3)

        collision_point = FVector(
            random.uniform(800, 1000),
            random.uniform(-300, 300),
            0
        )
        for n in range(nobjects):
            previous_size = len(unsafe_zones)
            position = self.find_position("obj", unsafe_zones)
            if len(unsafe_zones) == previous_size:
                continue
            dir_force = [collision_point.x - position[0].x,
                         collision_point.y - position[0].y,
                         random.randint(3, 4)]
            intensity = [random.uniform(1.5, 1.8), random.uniform(1.5, 1.8), random.uniform(3.7, 4)]
            force = FVector(dir_force[0] * math.pow(10, intensity[0]),
                            dir_force[1] * math.pow(10, intensity[1]),
                            dir_force[2] * math.pow(10, intensity[2]))

            mesh = random.choice([m for m in Object.shape.keys()] + ['Sphere'])
            self.params['object_{}'.format(nprevious + 1)] = ObjectParams(
                mesh=mesh,
                material=get_random_material('Object'),
                location=position[0],
                rotation=position[1],
                scale=position[2],
                mass=1,
                initial_force=force,
                warning=True,
                overlap=False)


    def create_new_zone(self, location, scale, rotation, type_actor):
        """
        Create a new zone
        """
        #  creation of a new zone
        #  new_zone is an array of 4 3D points, the vertices
        #  of unsafe square
        zone = [FVector(location.x - 50 * scale.x, location.y - 50 * scale.y, location.z),
                FVector(location.x + 50 * scale.x, location.y - 50 * scale.y, location.z),
                FVector(location.x + 50 * scale.x, location.y + 50 * scale.y, location.z),
                FVector(location.x - 50 * scale.x, location.y + 50 * scale.y, location.z)]
        if type_actor == 'occ':
            zone[2] = FVector(location.x + 50 * scale.x + 10, location.y + 50 * scale.y + 100 * scale.z + 10, location.z)
            zone[3] = FVector(location.x - 50 * scale.x + 10, location.y + 50 * scale.y + 100 * scale.z + 10, location.z)

        for point in zone:
            x, y = point.x-location.x, point.y-location.y
            point.x = x*math.cos(rotation.yaw*math.pi/180) - y*math.sin(rotation.yaw*math.pi/180)
            point.y = x*math.sin(rotation.yaw*math.pi/180) + y*math.cos(rotation.yaw*math.pi/180)
            point.x += location.x
            point.y += location.y
        return zone

    def find_position(self, type_actor, unsafe_zones):
        """
        Find a safe position and return it as a tuple (location, rotation, scale)
        type is "occ" if the actor is an occluder and "obj" if it's an object
        """
        location = FVector()
        rotation = FVector()
        scale = FVector()
        for try_index in range(100):
            if type_actor == "occ":
                scale = FVector(random.uniform(0.5, 1.5), 1, random.uniform(0.5, 1.5))
            else:
                # scale of an object in [1, 2]
                s = random.uniform(1, 2)
                scale = FVector(s, s, s)
            location = FVector(
                        random.uniform(200, 700),
                        random.uniform(-500, 500),
                        0)
            rotation = FRotator(0, 0, random.uniform(-180, 180))
            new_zone = self.create_new_zone(location, scale, rotation, type_actor)
            if self.check_spawning_location(new_zone, unsafe_zones):
                unsafe_zones.append(new_zone)
                break
        return location, rotation, scale

    def check_spawning_location(self, new_object_location, all_locations):
        #  new_object_location is an array of 4 3D points, the vertices
        #  of unsafe square
        #
        #  all_locations is an array of array same shape of new_object_location
        #
        #  https://stackoverflow.com/questions/306316/determine-if-two-rectangles-overlap-each-other
        #
        #  new_top, new_bottom, new_right, new_left are the extremum of new_object_location
        #  top and bottom are following the x axis
        #  right and left follow the y axis
        #
        #  top, bottom, right, left are the same for each location of all_locations

        new_top = max([point.x for point in new_object_location])
        new_bottom = min([point.x for point in new_object_location])
        new_right = max([point.y for point in new_object_location])
        new_left = min([point.y for point in new_object_location])
        for location in all_locations:
            top = max([point.x for point in location])
            bottom = min([point.x for point in location])
            right = max([point.y for point in location])
            left = min([point.y for point in location])
            if (left < new_right and right > new_left and
                    top > new_bottom and bottom < new_top):
                return False  # it intersect
        return True  # it doesn't intersect

    def make_color(self, min_value = 0.5, max_value = 1.0):
        h, s, v = random.uniform(0.05, 0.18), 0.3, random.uniform(min_value, max_value)
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return FLinearColor(r, g, b, 1.0)

    def stop_run(self, scene_index, total):
        super().stop_run()
        "print stop run"
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
            if 'object' in name.lower():
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
