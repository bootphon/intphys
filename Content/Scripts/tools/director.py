import importlib
import json
import os
import random
import shutil

import unreal_engine as ue
from unreal_engine.classes import GameplayStatics
from actors.camera import Camera
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
        self._remaining = 0

    def tick(self):
        if self._remaining == 0:
            GameplayStatics.SetGamePaused(self._world, False)

        if self.is_paused():
            self._remaining -= 1

    def is_paused(self):
        return self._remaining > 0

    def pause(self):
        self._remaining = self._duration
        GameplayStatics.SetGamePaused(self._world, True)


class SceneFactory:
    """Builds instances of the class Scene

    Auxiliary class to Director. This class parses the scenes JSON file and
    instanciates the scenes definied in it. If an error occurs during the
    parse, the program exits with an error message.

    """
    def __init__(self, world, saver):
        self._world = world
        self._saver = saver
        self._classes = {}

    def get_train(self):
        """Returns an instance of a train scene"""
        train_class = self._import_class('train', 'Train')
        return train_class(self._world, self._saver)

    def get_sandbox(self):
        """Returns an instance of a sandbox scene"""
        train_class = self._import_class('sandbox', 'Sandbox')
        return train_class(self._world, self._saver)

    def get_test(self, category, scenario, is_occluded, movement):
        """Returns an instance of a test scene"""
        if scenario == 'O0' and movement == 'dynamic_1':
            scenario = random.choices(['O0a', 'O0b'])
            cls = self._import_class(f'test.{scenario}', f'{scenario}Test')
        elif scenario == 'O0':
            cls = self._import_class('test.O0a', 'O0aTest')
        else:
            cls = self._import_class(f'test.{scenario}', f'{scenario}Test')

        return cls(self._world, self._saver, category, is_occluded, movement)

    def parse(self, scenes_json):
        """Yields instance of Scene as defined in a JSON configuration file"""
        if not os.path.isfile(scenes_json):
            exit_ue(f'error: file does not exist: {scenes_json}')
            return

        try:
            data = json.load(open(scenes_json, 'r'))
        except ValueError as err:
            exit_ue(f'error: cannot parse {scenes_json}: {str(err)}')
            return

        for category, sub_data in data.items():
            for scene in self._parse_category(category, sub_data):
                yield scene

    def _import_class(self, module_name, class_name):
        class_key = '.'.join((module_name, class_name))
        if class_key not in self._classes:
            try:
                self._classes[class_key] = getattr(
                    importlib.import_module(module_name), class_name)
            except (ImportError, AttributeError):
                exit_ue(f'error: cannot import class {class_key}')

        return self._classes[class_key]

    @staticmethod
    def _is_occluded(scene):
        if 'occluded' in scene:
            return True
        elif 'visible' in scene:
            return False
        else:
            exit_ue('error: no "occluded" or "visible" in one JSON scene')

    @staticmethod
    def _check_movement(movement):
        if movement not in ('static', 'dynamic_1', 'dynamic_2'):
            exit_ue('error: no "static", "dynamic_1" or "dynamic_2"'
                    'in one JSON scene')

    def _parse_category(self, category, data):
        if category not in ('train', 'test', 'dev', 'sandbox'):
            exit_ue(
                f'error: category must be train, test or dev '
                'but is {category}')
            return

        if 'train' in category:
            # data is here the number of train scenes to generate
            scenes = (self.get_train() for _ in range(data))
        elif 'sandbox' in category:
            scenes = (self.get_sandbox() for _ in range(data))
        else:
            # category is either 'test' or 'dev'
            scenes = self._parse_test(data, category)

        for scene in scenes:
            yield scene

    def _parse_test(self, data, category):
        for scenario, scenes in data.items():
            for visibility, sub_scenes in scenes.items():
                # occluded or visible case
                is_occluded = self._is_occluded(visibility)
                for movement, num_scenes in sub_scenes.items():
                    # must be static, dynamic_1 or dynamic_2
                    self._check_movement(movement)
                    for _ in range(num_scenes):
                        yield self.get_test(
                            category, scenario, is_occluded, movement)


class Director(object):
    """Renders the scenes definded in `scenes_json`

    The director manages the scene creation, rendering and saving. The method
    Director.tick is called at each UE game tick and start a new scene when the
    former one is done, or restart it if failed, until all the scenes are
    rendered and saved.

    The scenes can be 'train', 'test' or 'dev' scenes. Each scene is rendered
    during `2 * size[2]` ticks and captured on even ticks.

    The director owns the camera.

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
        # and 'dev', this is usefull to name the subdirectories where the
        # scenes are saved.
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

        # create the camera
        self.camera = Camera(self.world)

        # manage the scenes capture and saving to disk
        self.saver = Saver(self.camera, size, seed, output_dir=output_dir)

        self.scene_factory = SceneFactory(self.world, self.saver)

        # the list of the scenes being rendered by the director, as instances
        # of the class Scene.
        self.scenes = list(self.scene_factory.parse(scenes_json))

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

    def tick(self, dt):
        """this method is called at each game tick by UE"""
        # if the renderer is paused, just wait the end of the pause
        self.pauser.tick()
        if self.pauser.is_paused():
            return

        # the ticker at 0 means we terminate a scene at the previous call to
        # the tick() method (or the is the very first tick)
        if self.ticker == 0:
            if self.current_scene_index < self.total_scenes:
                # we need to start a new scene
                self._start_scene()
                self.ticker += 1
            else:
                # we rendered all the scenes, exiting
                self._terminate()
                exit_ue()

        # we reach the end of a scene, stop it and prepare for the next one
        elif self.ticker > self.max_tick:
            self._stop_scene()
            self.ticker = 0

        # a scene is running, if it is valid, simply continue and capture
        # screenshots, if it becomes invalid, restart it
        else:
            if self.current_scene.is_valid() and self.camera.is_valid:
                self.current_scene.tick()
                if self.ticker % 2 == 1:
                    self.current_scene.capture()
                self.ticker += 1
            else:
                # the scene is not valid, reschedule it with new parameters and
                # prepare for the next scene
                self.current_scene.stop_run(
                    self.counter[self.current_scene.category],
                    self.total_scenes)
                self._regenerate_scene()
                self.ticker = 0

    def _start_scene(self):
        # log a brief description of the scene being started
        if self.current_scene.run == 0:
            if 'train' in self.current_scene.name:
                ue.log('Scene {}/{}: Train scenario'.format(
                    self.current_scene_index + 1, self.total_scenes))
            else:
                ue.log('Scene {}/{}: Test / scenario {} / {} / {}'.format(
                    self.current_scene_index + 1, self.total_scenes,
                    self.current_scene.name,
                    self.current_scene.movement,
                    'occluded' if self.current_scene.is_occluded is True
                    else 'visible'))

        # setup the camera parameters and setup the new scene (spawn actors)
        self.camera.setup(self.current_scene.params['Camera'])
        self.current_scene.play_run()

        # if the scene is not valid (because of overlapping actors for
        # instance) it will be immediatly restarted, so the pause is useless
        if self.current_scene.is_valid():
            self.pauser.pause()

        # # for train only, 'warmup' the scene to settle the physics simulation
        # if 'train' in self.current_scene.name:
        #     for _ in range(1, 10):
        #         self.current_scene.tick()

    def _stop_scene(self):
        run_stopped = self.current_scene.stop_run(
            self.counter[self.current_scene.category],
            self.total_scenes)

        # a test scene has been stopped before all the runs have been rendered,
        # we need to restart it
        if run_stopped is False:
            self._regenerate_scene()

        # the scene has been completely rendered, just increment the counters
        elif self.current_scene.is_over():
            if (self.current_scene.name !=
                self.scenes[
                    (self.current_scene_index + 1) % self.total_scenes].name):
                self.counter[self.current_scene.category] = 0
            else:
                self.counter[self.current_scene.category] += 1
            self.counter['total'] += 1

    def _regenerate_scene(self):
        """Generate new parameters for the current scene"""
        ue.log('Restarting scene')
        self.num_restarted_scenes += 1

        # clear the saver from any saved content and delete the output
        # directory of the failed scene (if any)
        self.saver.reset(True)
        if not self.saver.is_dry_mode:
            output_dir = self.current_scene.get_scene_subdir(
                self.counter[self.current_scene.category],
                self.total_scenes)
            if self.current_scene.is_test_scene():
                output_dir = '/'.join(output_dir.split('/')[:-1])
            shutil.rmtree(output_dir)

        if self.current_scene.is_test_scene():
            # we are restarting a test scene
            scene = self.scene_factory.get_test(
                self.current_scene.category,
                self.current_scene.is_occluded,
                self.current_scene.movement)
        elif 'sandbox' in self.current_scene.name:
            scene = self.scene_factory.get_sandbox()
        else:
            # we are restarting a train scene
            scene = self.scene_factory.get_train()

        # insert the new scene in the list and erase the current one
        self.scenes[self.current_scene_index] = scene

    def _terminate(self):
        """Conclude operations once all the scenes have been rendered

        informs on the amount of restarted scenes and shuffle the
        possible/impossible runs in test and dev scenes

        """
        if self.num_restarted_scenes:
            percent_restarted = (
                self.num_restarted_scenes / self.total_scenes)
            ue.log("Generated {}% more scenes due to restarted scenes".
                   format(int(percent_restarted * 100)))

        self.saver.shuffle_test_scenes(dataset='test')
        self.saver.shuffle_test_scenes(dataset='dev')
