import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material
from actors.base_mesh import BaseMesh
from actors.object import Object
from actors.parameters import AxisCylinderParams, ObjectParams

class Axiscylinder():
	def __init__(self, world, params=AxisCylinderParams):
		#super().__init__(world.actor_spawn(ue.load_class('/Game/Object.Object_C')))
		self.get_parameters(params)

		self.cylinder = Object(world, ObjectParams())
		self.axis = Object(world, ObjectParams())

		self.is_valid = True
	
	def get_parameters(self, params):
		self.location = params.location
		self.rotation = params.rotation
		#self.material = params.material
