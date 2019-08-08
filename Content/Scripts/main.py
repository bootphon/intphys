import os
import random

import unreal_engine as ue
from unreal_engine.classes import KismetSystemLibrary
from unreal_engine.enums import ETickingGroup

from tools.director import Director
from tools.utils import exit_ue


# the default game resolution, for both scene rendering and saved
# images (width * height in pixels)
DEFAULT_RESOLUTION = (288, 288)

# a pause at the beginnin gof each scene, in number of ticks (usefull to let
# the textures being completetly loaded)
DEFAULT_PAUSE_DURATION = 50

# the number of frames captured for each scene
NUM_FRAMES_PER_SCENE = 100


class Main:
    @staticmethod
    def set_game_resolution(world, resolution):
        """Set the game rendering resolution

        `resolution` is a tuple of (width, height) in pixels

        """
        # cast resolution to string
        resolution = (str(r) for r in resolution)

        # command that change the resolution
        command = 'r.SetRes {}'.format('x'.join(resolution))

        # execute the command
        KismetSystemLibrary.ExecuteConsoleCommand(world, command)

    def begin_play(self):
        # get the world from the attached component
        world = self.uobject.get_world()

        # execute main tick after physic played
        self.uobject.SetTickGroup(ETickingGroup.TG_PostPhysics)

        # the main loop continues to tick when the game is paused (but
        # all other actors are paused)
        self.uobject.SetTickableWhenPaused(True)

        # load the specifications of scenes we are going to generate
        try:
            scenes_json = os.environ['INTPHYS_SCENES']
        except KeyError:
            exit_ue('fatal error, INTPHYS_SCENES not defined, exiting')
            return

        # init random number generator
        try:
            seed = int(os.environ['INTPHYS_SEED'])
        except KeyError:
            seed = None
        random.seed(seed)

        # setup screen resolution
        try:
            res = os.environ['INTPHYS_RESOLUTION'].split('x')
            resolution = (res[0], res[1])
        except KeyError:
            resolution = DEFAULT_RESOLUTION
        self.set_game_resolution(world, resolution)

        # setup output directory where to save generated data
        try:
            output_dir = os.environ['INTPHYS_OUTPUTDIR']
        except KeyError:
            output_dir = None
            ue.log_warning('INTPHYS_OUTPUTDIR not defined, capture disabled')

        # setup the pause duration (in number of ticks) at the
        # begining of each run (to let time for the texture to be
        # correctly displayed)
        try:
            pause_duration = int(os.environ['INTPHYS_PAUSEDURATION'])
        except KeyError:
            pause_duration = DEFAULT_PAUSE_DURATION

        # setup the director with the list of scenes to generate, 100
        # images per video at the game resolution
        size = (resolution[0], resolution[1], NUM_FRAMES_PER_SCENE)
        self.director = Director(
            world,
            scenes_json,
            size,
            output_dir,
            seed or random.randint(0, 1e9),
            pause_duration=pause_duration)

    def tick(self, dt):
        # let the director handle the tick
        self.director.tick(dt)
