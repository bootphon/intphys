import unreal_engine as ue
from unreal_engine import FVector, FRotator, UObject
from unreal_engine.classes import Material

from actors.base_mesh import BaseMesh
from actors.parameters import SkysphereParams

"""
It is the sky.
You can change the skin to a night sky (with stars and so on)
"""


class Skysphere(BaseMesh):
    def __init__(self, world, params=SkysphereParams()):
        if isinstance(params, Skysphere):
            super().__init__(world.actor_spawn(
                ue.load_class("/Game/Meshes/SkySphere/BP_Sky_Sphere1." +
                              "BP_Sky_Sphere1_C")))
            self.mesh_str = '/Game/Meshes/SkySphere/SM_SkySphere'
            self.material = ue.load_object(Material, params.material)
            self.set_mesh()
            self.rotation = params.rotation
        elif isinstance(params, UObject):
            super().__init__(params)
        """
        self.actor.set_actor_rotation(self.rotation)
        self.actor.DirectionalLight.set_actor_location(FVector(0, 0, -1000))
        self.actor.DirectionalLight.set_actor_rotation(FRotator(0, 0, 0))
        """

    def get_status(self):
        status = {
            'name': self.actor.get_name(),
            'material': self.material.get_name()}
        return status
