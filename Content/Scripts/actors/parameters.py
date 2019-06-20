from dataclasses import dataclass
from dataclasses import field
from unreal_engine import FVector, FRotator
from unreal_engine.enums import ECameraProjectionMode
from tools.materials import get_random_material


@dataclass
class CameraParams:
    location: FVector = FVector(0, 0, 0)
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
    type: str = 'SkyLight'

@dataclass
class AxisCylinderParams:
    location: FVector = FVector(0, 0, 0)
    rotation: FRotator = FRotator(0, 0, 0)

@dataclass
class WallsParams:
    material: str = get_random_material('Wall')
    length: float = 2000
    depth: float = 1000
    height: float = 1
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
    rotation:FVector = FVector(0, 0, 0)
