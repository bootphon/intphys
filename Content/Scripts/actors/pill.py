from actors.object import Object
from actors.base_mesh import BaseMesh
from actors.parameters import ObjectParams
from unreal_engine import FVector, FRotator, FLinearColor
from unreal_engine.classes import Material
import unreal_engine as ue


"""
Pill inherits from Object and spawns Capsule or Sphere.
It is used in O0b.
"""


class Pill(Object):

    shape = {
        'Capsule': '/Game/Meshes/Capsule.Capsule',
        'Sphere': '/Game/Meshes/Sphere.Sphere'
    }

    mass_factor = {
        'Sphere': 1.0,
        'Capsule': 1}

    def __init__(self, world, params=ObjectParams):
        BaseMesh.__init__(self,
            world.actor_spawn(ue.load_class('/Game/Pill.Pill_C')))
        self.get_parameters(params)
        self.set_parameters()

    def get_parameters(self, params):
        BaseMesh.get_parameters(self,
			params.location,
			params.rotation,
			params.scale,
			params.friction,
			params.restitution,
			params.overlap,
			params.warning,
			self.shape[params.mesh]
		)
        self.material = ue.load_object(Material, params.material)
        self.mass = params.mass
        self.force = params.force
        self.initial_force = params.initial_force
