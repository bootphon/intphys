"""Defines general utility functions used by intphys"""

import os

import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import GameplayStatics
from unreal_engine.classes import Exit


def as_dict(value):
    """Convert a FVector or FRotator to a dict

    Raise ValueError if value is not a FVector or a FRoator.

    """
    if isinstance(value, FVector):
        return {'x': value.x, 'y': value.y, 'z': value.z}
    elif isinstance(value, FRotator):
        return {'roll': value.roll, 'pitch': value.pitch, 'yaw': value.yaw}
    else:
        raise ValueError(f'expect FVector or FRotator, having {type(value)}')


def exit_ue(message=None):
    """Quit the game, optionally logging an error message

    `world` is the world reference from the running game.
    `message` is the error message to be looged.

    """
    if message:
        ue.log(message)

    Exit.ExitEngine()


def set_game_paused(world, paused):
    """Pause/unpause the game

    `paused` is a boolean value

    """
    GameplayStatics.SetGamePaused(world, paused)


def intphys_root_directory():
    """Return the absolute path to the intphys root directory"""
    # guess it from the evironment variable first, or from the
    # relative path from here
    try:
        root_dir = os.environ['INTPHYS_ROOT']
    except KeyError:
        root_dir = os.path.join(os.path.dirname(__file__), '../..')

    # make sure the directory is the good one
    assert os.path.isdir(root_dir)
    assert 'intphys.py' in os.listdir(root_dir)

    return os.path.abspath(root_dir)
