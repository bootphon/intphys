import os
import random
import unreal_engine as ue
from tools.director import Director
from tools.utils import exit_ue, set_game_resolution
from unreal_engine.enums import ETickingGroup
# the default game resolution, for both scene rendering and saved
# images (width * height in pixels)
DEFAULT_RESOLUTION = (288, 288)


class Main:
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
            seed = os.environ['INTPHYS_SEED']
        except KeyError:
            seed = None
        random.seed(seed)

        # setup screen resolution
        try:
            res = os.environ['INTPHYS_RESOLUTION'].split('x')
            resolution = (res[0], res[1])
        except KeyError:
            resolution = DEFAULT_RESOLUTION
        set_game_resolution(world, resolution)

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
            pause_duration = 50

        # setup the director with the list of scenes to generate, 100
        # images per video at the game resolution
        size = (resolution[0], resolution[1], 100)
        self.director = Director(
            world, scenes_json, size, output_dir,
            pause_duration=pause_duration)

    def tick(self, dt):
        # let the director handle the tick
        self.director.tick(dt)
