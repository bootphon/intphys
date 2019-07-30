import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material

from actors.base_mesh import BaseMesh
from actors.parameters import FloorParams


class Floor(BaseMesh):
    """A rectangular plane which is the ground of other actors

    Parameters
    ----------
    world: UEngine world instance
    scale: FVector
        Scale factor (x, y, z) for the mesh, default to (10, 10, 1)
    material: uobject
        Actor's texture, random by default
    Disclaimer: if you change the size of the mesh, think about
    changing the formula

    """
    def __init__(self, world, params=FloorParams()):
        super().__init__(
            world.actor_spawn(ue.load_class('/Game/Floor.Floor_C')))
        self.get_parameters(params)
        self.set_parameters()

    def get_parameters(self, params):
        location = FVector(
            params.location.x,
            params.location.y - (400 * params.scale.y / 2),
            params.location.z)
        rotation = FRotator(
            params.rotation.pitch,
            params.rotation.roll,
            params.rotation.yaw)
        super().get_parameters(
            location, rotation, params.scale,
            params.friction, params.restitution, False, False,
            '/Game/Meshes/Floor_400x400')

        self.material = ue.load_object(Material, params.material)

    def set_parameters(self):
        super().set_parameters()
        self.get_mesh().call('SetCollisionProfileName BlockAll')

    def get_status(self):
        status = super().get_status()
        status['material'] = self.material.get_name()
        return status
