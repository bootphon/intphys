import importlib
import json
import os
import random
import shutil

import unreal_engine as ue
from unreal_engine.classes import GameplayStatics
from tools.utils import exit_ue
from tools.saver import Saver


class PauseManager:
    """Manages game pauses at the beginning of each scene

    Auxiliary class to Director. At each new scene, the game is paused during
    `duration` ticks. This is required to let the time for the textures to be
    fully loaded and rendered for the first capture of the scene.

    """
    def __init__(self, world, duration):
        self._world = world
        self._duration = duration
        self._is_paused = False
        self.remaining = 0

    def is_paused(self):
        return self._is_paused

    def pause(self):
        self.remaining = self._duration
        self._is_paused = True
        GameplayStatics.SetGamePaused(self._world, True)

    def unpause(self):
        self._is_paused = False
        GameplayStatics.SetGamePaused(self._world, False)


class ScenesJsonParser:
    """Yields instances of of the class Scene as defined in a JSON file

    Auxiliary class to Director. This class parses the scenes JSON file and
    instanciates the scenes definied in it. If an error occurs during the
    parse, the program exits with an error message.

    """
    def __init__(self, world, saver):
        self.world = world
        self.saver = saver
        self.classes = {}

    def import_class(self, module_name, class_name):
        class_key = '.'.join((module_name, class_name))
        if class_key not in self.classes:
            try:
                self.classes[class_key] = getattr(
                    importlib.import_module(module_name), class_name)
            except (ImportError, AttributeError):
                exit_ue(
                    f'error: cannot import class {class_key}')

        return self.classes[class_key]

    @staticmethod
    def is_occluded(scene):
        if 'occluded' in scene:
            return True
        elif 'visible' in scene:
            return False
        else:
            exit_ue('error: no "occluded" or "visible" in one JSON scene')

    @staticmethod
    def check_movement(movement):
        if movement not in ('static', 'dynamic_1', 'dynamic_2'):
            exit_ue('error: no "static", "dynamic_1" or "dynamic_2"'
                    'in one JSON scene')

    def parse(self, scenes_json):
        if not os.path.isfile(scenes_json):
            exit_ue(f'error: file does not exist: {scenes_json}')
            return

        try:
            data = json.load(open(scenes_json, 'r'))
        except ValueError as err:
            exit_ue(f'error: cannot parse {scenes_json}: {str(err)}')
            return

        for category, sub_data in data.items():
            for scene in self.parse_category(category, sub_data):
                yield scene

    def parse_category(self, category, data):
        if category not in ('train', 'test', 'dev'):
            exit_ue(
                f'error: category must be train, test or dev '
                'but is {category}')
            return

        if 'train' in category:
            scenes = self.parse_train(data)
        else:
            # category is either 'test' or 'dev'
            scenes = self.parse_test(data, category)

        for scene in scenes:
            yield scene

    def parse_train(self, num_scenes):
        train_class = self.import_class('train', 'Train')
        for _ in range(num_scenes):
            yield train_class(self.world, self.saver, 'train')

    def parse_test(self, data, category):
        for scenario, scenes in data.items():
            for visibility, sub_scenes in scenes.items():
                # occluded or visible case
                is_occluded = self.is_occluded(visibility)
                for movement, num_scenes in sub_scenes.items():
                    # must be static, dynamic_1 or dynamic_2
                    self.check_movement(movement)
                    for _ in range(num_scenes):
                        yield self.get_test(
                            category, scenario, is_occluded, movement)

    def get_test(self, category, scenario, is_occluded, movement):
        if scenario == 'O0' and movement == 'dynamic_1':
            scenario = random.choices(['O0a', 'O0b'])
            cls = self.import_class(f'test.{scenario}', f'{scenario}Test')
        elif scenario == 'O0':
            cls = self.import_class('test.O0a', 'O0aTest')
        else:
            cls = self.import_class(f'test.{scenario}', f'{scenario}Test')

        return cls(self.world, self.saver, category, is_occluded, movement)


class Director(object):
    """Renders the scenes definded in `scenes_json`

    The director manages the scene creation, rendering and saving. The method
    Director.tick is called at each UE game tick and start a new scene when the
    former one is done, or restart it if failed, until all the scenes are
    rendered and saved.

    The scenes can be 'train', 'test' or 'dev' scenes. Each scene is rendered
    during `2 * size[2]` ticks and captured on even ticks.

    Parameters
    ----------
    world : ue.UWorld
        The world in which the scenes are rendered
    scenes_json : str
        The JSON file defining the scenes to render.
    size : tuple
        The dimension of a scene as (image_width, image_heigth, num_images)
    output_dir : str
        The directory where to save the rendered scenes captures. If None, run
        in "dry mode" and do not save anything.
    seed : int
        The seed for random number generation
    pause_duration : int, optional
        Duration of the pause at the beginning of each scene (in number of
        ticks).

    """
    def __init__(self, world, scenes_json, size, output_dir,
                 seed, pause_duration=30):
        # the world in which the scenes are rendered
        self.world = world

        # count the number of scenes rendered for each category 'train', 'test'
        # and 'dev', this is usefull to name the subdirectory where the scenes
        # are saved.
        self.counter = {
            'total': 0,
            'train': 0,
            'test': 0,
            'dev': 0}

        # count the number of restarted scenes (i.e. the number of times a
        # scene rendering failed)
        self.num_restarted_scenes = 0

        # ticker is set at 0 when a scene starts and is incremented until it
        # reachs max_tick (meaning the scene is rendered)
        self.max_tick = 2 * size[2]
        self.ticker = 0

        # manage the pauses at the beginning of each scene
        self.pauser = PauseManager(self.world, pause_duration)

        # manage the scenes capture and saving to disk
        self.saver = Saver(size, seed, output_dir=output_dir)

        # the list of the scenes being rendered by the director, as instances
        # of the class Scene.
        self.scenes = list(
            ScenesJsonParser(self.world, self.saver).parse(scenes_json))

    @property
    def current_scene_index(self):
        """The index of the scene being rendered"""
        return self.counter['total']

    @property
    def current_scene(self):
        """The scene being rendered"""
        return self.scenes[self.current_scene_index]

    @property
    def total_scenes(self):
        """The total number of scene to render"""
        return len(self.scenes)

    def start_scene(self):
        if self.current_scene_index >= self.total_scenes:
            # no more scene to start
            return

        if self.current_scene.run == 0:
            if hasattr(self.current_scene, 'movement'):
                ue.log('Scene {}/{}: Test / scenario {} / {} / {}'.format(
                    self.current_scene_index + 1, self.total_scenes,
                    self.current_scene.name,
                    self.current_scene.movement,
                    'occluded' if self.current_scene.is_occluded is True
                    else 'visible'))
            else:
                ue.log('Scene {}/{}: Train / scenario {}'.format(
                    self.current_scene_index + 1, self.total_scenes,
                    self.current_scene.name))

        self.current_scene.play_run()

        # for train only, 'warmup' the scene to settle the physics simulation
        if 'train' in self.current_scene.name:
            for _ in range(1, 10):
                self.current_scene.tick()

    def stop_scene(self):
        if self.current_scene_index >= self.total_scenes:
            return

        run_stopped = self.current_scene.stop_run(
            self.counter[self.current_scene.set], self.total_scenes)
        if run_stopped is False:
            self.restart_scene()

        elif (self.current_scene.is_over()
              and self.current_scene_index < self.total_scenes):
            if (self.current_scene.name !=
                self.scenes[
                    (self.current_scene_index + 1) % self.total_scenes].name):
                self.counter[self.current_scene.set] = 0
            else:
                self.counter[self.current_scene.set] += 1
            self.counter['total'] += 1

        self.ticker = 0

    def restart_scene(self):
        ue.log('Restarting scene')
        self.num_restarted_scenes += 1

        # clear the saver from any saved content and delete the output
        # directory of the failed scene (if any)
        self.saver.reset(True)
        if not self.saver.is_dry_mode:
            output_dir = self.current_scene.get_scene_subdir(
                self.counter[self.current_scene.set],
                self.total_scenes)
            if self.current_scene.is_test_scene():
                output_dir = '/'.join(output_dir.split('/')[:-1])
            shutil.rmtree(output_dir)

        # we are restarting a test scene
        if 'test' in type(self.current_scene).__name__.lower():
            module = importlib.import_module(
                "test.{}".format(self.current_scene.name))
            test_class = getattr(
                module, "{}Test".format(self.current_scene.name))
            self.scenes.insert(
                self.current_scene_index + 1,
                test_class(
                    self.world, self.saver, self.current_scene.set,
                    self.current_scene.is_occluded,
                    self.current_scene.movement))

        # we are restarting a train scene
        else:
            module = importlib.import_module('train')
            train_class = getattr(module, "Train")
            self.scenes.insert(
                self.current_scene_index + 1,
                train_class(self.world, self.saver, 'train'))

        self.scenes.pop(0)

    def capture(self):
        self.current_scene.capture()

    def tick(self, dt):
        """this method is called at each game tick by UE"""
        if self.pauser.remaining != 0:
            self.pauser.remaining -= 1
            return

        # launch new scene every 2 * num_frames tick except if a pause just
        # finished
        if not self.pauser.is_paused() and self.ticker % self.max_tick == 0:
            if self.ticker != 0:
                # if this is not the first tick, stop the previous scene
                self.stop_scene()
            self.start_scene()
            self.pauser.pause()
            return

        # if one of the actors is not valid, restart the scene with
        # new parameters, in a try/catch to deals with the very last
        # scene once it have been stopped
        try:
            if not self.current_scene.is_valid():
                self.current_scene.stop_run(
                    self.counter[self.current_scene.set], self.total_scenes)
                self.restart_scene()
                self.ticker = 0
                self.start_scene()
                self.pauser.pause()
                return
        except IndexError:
            pass

        self.pauser.unpause()

        if self.current_scene_index < self.total_scenes:
            self.current_scene.tick()
            if self.ticker % 2 == 1:
                self.capture()
        else:
            # we generated all the requested scenes, gently exit the program
            if self.num_restarted_scenes:
                # informs on the amount of restarted scenes
                percent_restarted = (
                    self.num_restarted_scenes / self.total_scenes)
                ue.log("Generated {}% more scenes due to restarted scenes".
                       format(int(percent_restarted * 100)))

            # shuffle possible/impossible runs in test scenes
            self.saver.shuffle_test_scenes()

            # exit the program
            exit_ue()

        self.ticker += 1
