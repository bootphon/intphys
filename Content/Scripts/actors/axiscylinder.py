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

class Axiscylinder():
	def __init__(self, world, params=AxisCylinderParams):
		self.get_parameters(params)

		x, y, z = self.location.x, self.location.y, self.location.z

		self.material = get_random_material('Object')

		if not self.is_long: # short axis-cylinder
			if not self.down:
				self.cylinder = Object(world, ObjectParams(
					mesh = 'Lollipop',
					location = FVector(x, y, z+100),
					material = self.material))
			else:
				self.cylinder = Object(world, ObjectParams(
					mesh = 'Lollipop',
					location = FVector(x, y, z+100-100),
					rotation = FRotator(180, 0, 0),
					material = self.material))
		else: # long axis-cylinder
			self.cylinder = Object(world, ObjectParams(
				mesh = 'RollingPin',
				location = FVector(x, y, z)))

		self.cylinder.get_mesh().set_simulate_physics(False)
		self.is_valid = True
		self.hidden = False

		self.dy = 0
	
	def get_parameters(self, params):
		self.location = params.location
		self.rotation = params.rotation
		self.is_long = params.is_long
		self.down = params.down
		self.moves = params.moves
		self.speed = params.speed
	
	def move(self):
		self.dy = self.speed
		
		self.cylinder.set_location(FVector(self.cylinder.location.x, self.cylinder.location.y + self.dy,
			self.cylinder.location.z))

	def set_location(self, location):
		if self.is_long:
			v = location
			v.z = v.z + 100
			self.cylinder.set_location(v)
		else:
			self.cylinder.set_location(location)

	def actor_destroy(self):
		self.cylinder.actor_destroy()

	def get_status(self):
		status = {
			'name': self.cylinder.actor.get_name(),
			# 'type': self.actor.get_name().split('_')[0],
			'location': as_dict(self.location),
			'rotation': as_dict(self.rotation)}
		return status