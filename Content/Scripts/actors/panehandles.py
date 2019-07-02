import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material
from actors.base_mesh import BaseMesh
from actors.object import Object
from actors.parameters import PaneHandlesParams, ObjectParams
from tools.utils import as_dict
from tools.materials import get_random_material

"""
A long box with two handles, like a sign. It is used for O0.
"""
class Panehandles(BaseMesh):
	def __init__(self, world, params=PaneHandlesParams()):
		super().__init__(
            world.actor_spawn(ue.load_class('/Game/Object.Object_C')))
		self.get_parameters(params)
		self.set_parameters()

	def get_parameters(self, params):
		super().get_parameters(
			params.location,
			params.rotation,
			params.scale,
			params.friction,
			params.restitution,
			params.overlap,
			params.warning,
			'/Game/Meshes/PaneHandles.PaneHandles'
		)
		self.material = ue.load_object(Material, params.material)

	def set_parameters(self):
		super().set_parameters()
		self.get_mesh().set_simulate_physics(False)
