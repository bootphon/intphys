import importlib
import json
import shutil

import unreal_engine as ue
import tools.materials
from tools.utils import exit_ue, set_game_paused
from tools.saver import Saver


class Director(object):
    def __init__(self, world, params_file, size, output_dir,
                 seed, pause_duration=30):
        self.world = world
        self.scenes = []
        self.scene = {
            'total': 0,
            'train': 0,
            'test': 0,
            'dev': 0}

        self.saver = Saver(size, seed, output_dir=output_dir)

        try:
            self.generate_scenes(json.load(open(params_file, 'r')))
        except ValueError as err:
            exit_ue(
                'fatal error: failed to parse {}: {}'
                .format(params_file, str(err)))

        # preload the actors materials
        tools.materials.load()

        self.ticker = 0
        self.pause_duration = pause_duration
        self.pause_remaining = 0
        self.is_paused = False
        self.restarted = 0

    def generate_scenes(self, json_data):
        for Set, d in json_data.items():
            if 'train' in Set:
                train_class = getattr(
                    importlib.import_module("train"), "Train")
                for _ in range(d):
                    self.scenes.append(
                        train_class(self.world, self.saver, Set))
            else:
                for scenario, scenes in d.items():
                    module = importlib.import_module(
                        "test.{}".format(scenario))
                    test_class = getattr(module, "{}Test".format(scenario))
                    for scene, b in scenes.items():
                        if ('occluded' in scene):
                            is_occluded = True
                        elif ('visible' in scene):
                            is_occluded = False
                        else:
                            raise ValueError(
                                "Didn't find 'occluded' nor 'visible' " +
                                "in one scene of the json file")

                        for movement, nb in b.items():
                            if (
                                    'static' not in movement and
                                    'dynamic_1' not in movement and
                                    'dynamic_2' not in movement):
                                raise ValueError(
                                    "Didn't find 'static', " +
                                    "'dynamic_1' nor 'dynamic_2' " +
                                    "in one scene of the json file")
                            else:
                                for i in range(nb):
                                    try:
                                        self.scenes.append(test_class(
                                            self.world, self.saver, Set,
                                            is_occluded, movement))
                                    except NotImplementedError:
                                        continue

        self.total_scenes = len(self.scenes)

    def play_scene(self):
        total = self.scene['total']

        if total >= len(self.scenes):
            return
        if self.scenes[total].run == 0:
            if hasattr(self.scenes[total], 'movement'):
                ue.log("Scene {}/{}: Test / scenario {} / {} / {}".format(
                    total + 1, len(self.scenes),
                    self.scenes[total].name,
                    self.scenes[total].movement,
                    "occluded" if self.scenes[total].is_occluded
                    is True else "visible"))
            else:
                ue.log("Scene {}/{}: Train / scenario {}".format(
                    total + 1, len(self.scenes),
                    self.scenes[total].name))
        self.scenes[total].play_run()

        # for train only, "warmup" the scene to settle the physics simulation
        if "train" in self.scenes[total].name:
            for i in range(1, 10):
                self.scenes[total].tick()

    def stop_scene(self):
        total = self.scene['total']

        if total >= len(self.scenes):
            return

        if self.scenes[total].stop_run(
                self.scene[self.scenes[total].set], len(self.scenes)) is False:
            self.restart_scene()

        elif (self.scenes[total].is_over() and total < len(self.scenes)):
            if (
                    self.scenes[total].name !=
                    self.scenes[(total + 1) % len(self.scenes)].name):
                self.scene[self.scenes[total].set] = 0
            else:
                self.scene[self.scenes[total].set] += 1
            self.scene['total'] += 1

        self.ticker = 0

    def restart_scene(self):
        ue.log('Restarting scene')
        self.restarted += 1
        total = self.scene['total']

        # clear the saver from any saved content and delete the output
        # directory of the failed scene
        self.saver.reset(True)
        if not self.saver.is_dry_mode:
            output_dir = self.scenes[total].get_scene_subdir(
                self.scene[self.scenes[total].set], len(self.scenes))
            if self.scenes[total].is_test_scene():
                output_dir = '/'.join(output_dir.split('/')[:-1])
            shutil.rmtree(output_dir)

        is_test = True if 'test' in \
            type(self.scenes[total]).__name__.lower() else False
        if is_test is True:
            module = importlib.import_module(
                "test.{}".format(self.scenes[total].name))
            test_class = getattr(
                module,
                "{}Test".format(self.scenes[total].name))
            is_occluded = self.scenes[total].is_occluded
            movement = self.scenes[total].movement
            self.scenes.insert(total + 1, test_class(
                self.world, self.saver, self.scenes[total].set,
                is_occluded, movement))
            self.scenes.pop(0)
        else:
            module = importlib.import_module('train')
            train_class = getattr(module, "Train")
            self.scenes.insert(
                total + 1,
                train_class(self.world, self.saver, self.scenes[total].set))
            self.scenes.pop(0)

    def capture(self):
        self.scenes[self.scene['total']].capture()

    def tick(self, dt):
        """this method is called at each game tick by UE"""
        if self.pause_remaining != 0:
            self.pause_remaining -= 1
            return

        # launch new scene every 200 tick except if a pause just finished
        if self.is_paused is False and self.ticker % 200 == 0:
            if self.ticker != 0:
                self.stop_scene()
            self.play_scene()

            # pause to let textures load
            self.pause_remaining = self.pause_duration
            self.is_paused = True
            set_game_paused(self.world, True)
            return

        # if one of the actors is not valid, restart the scene with
        # new parameters, in a try/catch to deals with the very last
        # scene once it have been stopped
        total = self.scene['total']
        try:
            if not self.scenes[total].is_valid():
                self.scenes[total].stop_run(
                    self.scene[self.scenes[total].set], len(self.scenes))
                self.restart_scene()
                self.ticker = 0
                self.play_scene()
                # pause to let textures load
                self.pause_remaining = self.pause_duration
                self.is_paused = True
                set_game_paused(self.world, True)
                return
        except IndexError:
            pass

        self.is_paused = False
        set_game_paused(self.world, False)
        if total < len(self.scenes):
            self.scenes[total].tick()
            if self.ticker % 2 == 1:
                self.capture()
        else:
            # we generated all the requested scenes, gently exit the program
            if self.restarted:
                # informs on the amount of restarted scenes
                ue.log("Generated {}% more scenes due to restarted scenes".
                       format(int((self.restarted / self.total_scenes) * 100)))

            # shuffle possible/impossible runs in test scenes
            self.saver.shuffle_test_scenes()

            # exit the program
            exit_ue()

        self.ticker += 1
