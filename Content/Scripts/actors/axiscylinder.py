import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material
from actors.base_mesh import BaseMesh
from actors.object import Object
from actors.parameters import AxisCylinderParams, ObjectParams
from tools.utils import as_dict
from tools.materials import get_random_material

"""
A cylinder with a cylindrical shaft, made from two joined cylinders

The move variable is used to make the axis-cylinder move as occluders do.
The down variable defines wether the small end of the AxisCylinder is at top (False) or bottom (True).
It has no effect on long AxisCylinders.
"""

class Axiscylinder(BaseMesh):

	length = {
		'Lollipop': '/Game/Meshes/Lollipop.Lollipop',
        'RollingPin': '/Game/Meshes/Rolling_Pin.Rolling_Pin'
	}

	def __init__(self, world, params=AxisCylinderParams()):
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
			self.length[params.mesh]
		)
		self.material = ue.load_object(Material, params.material)
		self.dy = 0
		self.is_long = params.is_long
		self.down = params.down
		self.moves = params.moves
		self.speed = params.speed

		if not self.is_long: # short axis-cylinder
			self.mesh_str = self.length['Lollipop']
			if not self.down:
				self.location.z += 100
			else:
				self.rotation.pitch = 180
		else: # long axis-cylinder
			self.mesh_str = self.length['RollingPin']

	def set_parameters(self):
		super().set_parameters()
		self.get_mesh().set_simulate_physics(False)

	def move(self):
		self.dy = self.speed
		self.set_location(FVector(
			self.location.x,
			self.location.y + self.dy,
			self.location.z))
