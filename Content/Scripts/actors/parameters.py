import math
import random

from dataclasses import dataclass
from dataclasses import field
from unreal_engine import FVector, FRotator, FLinearColor
from unreal_engine.enums import ECameraProjectionMode
from tools.materials import get_random_material


def camera_location(type=None):
    """Return the camera location parameter

    If type is 'train', this is for a train scene, if type is 'O0' this is for
    a O0 test, else this is for a non-specified test scene.

    """
    # the default, when type is None
    X = 0
    Y = 0
    Z = 200

    if type in ('train', 'O3'):
        Z = random.uniform(175, 225)
    elif type == 'O0':
        X = 60
        Z = 275

    return FVector(X, Y, Z)


def theoretical_max_depth():
    """Return the maximal depth that can be observed in a dataset

    the theorical depth is obtained by looking the corner of the floor at
    (2000, 4000, 0) from the camera at (0, 0, 275)

    This function returns 4480.583109373154

    """
    # the floor mesh is 400x400x20. The camera is located at the center of the
    # floor
    floor = FloorParams()
    a = 400 * floor.scale.y / 2
    b = 400 * floor.scale.x / 2
    # the maximum height of the camera (from camera_location() above)
    c = 275

    return math.sqrt(a**2 + b**2 + c**2)


@dataclass
class CameraParams:
    location: FVector = camera_location(type=None)
    rotation: FRotator = FRotator(0, 0, 0)
    field_of_view: float = 90
    aspect_ratio: float = 1
    projection_mode: int = ECameraProjectionMode.Perspective


@dataclass
class FloorParams:
    material: str = get_random_material('Floor')
    scale: FVector = FVector(10, 20, 1)
    location: FVector = FVector(0, 0, 0)
    rotation: FRotator = FRotator(0, 0, 0)
    friction: float = 0.5
    restitution: float = 0.5


@dataclass
class LightParams:
    location: FVector = FVector(0, 0, 0)
    rotation: FRotator = FRotator(0, 0, 0)
    color: FLinearColor = FLinearColor(1, 1, 1, 1)
    type: str = 'SkyLight'
    varIntensity: float = 0


@dataclass
class AxisCylinderParams:
    location: FVector = FVector(0, 0, 0)
    rotation: FRotator = FRotator(0, 0, 0)
    scale: FVector = FVector(1, 1, 1)
    friction: float = 0.5
    restitution: float = 0.5
    overlap: bool = False
    warning: bool = False
    mesh: str = 'Lollipop'
    material: str = get_random_material('Object')
    is_long: bool = False
    down: bool = False
    moves: list = field(default_factory=list)


@dataclass
class PaneHandlesParams:
    location: FVector = FVector(0, 0, 0)
    rotation: FRotator = FRotator(0, 0, 0)
    scale: FVector = FVector(1, 1, 1)
    friction: float = 0.5
    restitution: float = 0.5
    overlap: bool = False
    warning: bool = False
    # mesh: str = 'PaneHandles'
    material: str = get_random_material('Object')


@dataclass
class WallsParams:
    material: str = get_random_material('Wall')
    length: float = 2000
    depth: float = 1000
    height: float = 1
    z: float = 0
    overlap: bool = False
    warning: bool = False


@dataclass
class ObjectParams:
    mesh: str = 'Sphere'
    material: str = get_random_material('Object')
    location: FVector = FVector(0, 0, 0)
    rotation: FRotator = FRotator(0, 0, 0)
    scale: FVector = FVector(1, 1, 1)
    force: FVector = FVector(0, 0, 0)
    initial_force: FVector = FVector(0, 0, 0)
    mass: float = 1
    friction: float = 0.5
    restitution: float = 0.5
    overlap: bool = False
    warning: bool = False


@dataclass
class OccluderParams:
    material: str = get_random_material('Wall')
    location: FVector = FVector(0, 0, 0)
    rotation: FRotator = FRotator(0, 0, 0)
    scale: FVector = FVector(1, 1, 1)
    friction: float = 0.5
    restitution: float = 0.5
    # moves: tuple = (0, 1)  # list not supported
    moves: list = field(default_factory=list)
    speed: float = 1
    overlap: bool = False
    warning: bool = False
    start_up: bool = False


@dataclass
class SkysphereParams:
    material: str = '/Game/Meshes/SkySphere/M_Sky_Panning_Clouds2'
    rotation: FVector = FVector(0, 0, 0)
