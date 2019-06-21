import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material
from actors.base_mesh import BaseMesh
from actors.object import Object
from actors.parameters import AxisCylinderParams, ObjectParams

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

		if not self.is_long: # short axis-cylinder
			if not self.down:
				self.cylinder = Object(world, ObjectParams(
					mesh = 'Cylinder',
					location = FVector(x, y, z+100)))
				self.axis = Object(world, ObjectParams(
					mesh = 'Cylinder',
					location = FVector(x, y, z+200),
					scale = FVector(0.25, 0.25, 1)))
			else:
				self.cylinder = Object(world, ObjectParams(
					mesh = 'Cylinder',
					location = FVector(x, y, z+100-100)))
				self.axis = Object(world, ObjectParams(
					mesh = 'Cylinder',
					location = FVector(x, y, z+200-300),
					scale = FVector(0.25, 0.25, 1)))
		else: # long axis-cylinder
			self.cylinder = Object(world, ObjectParams(
				mesh = 'Cylinder',
				location = FVector(x, y, z),
				scale = FVector(1, 1, 2)))
			self.axis = Object(world, ObjectParams(
				mesh = 'Cylinder',
				location = FVector(x, y, z-100),
				scale = FVector(0.25, 0.25, 4)))

		self.cylinder.get_mesh().set_simulate_physics(False)
		self.axis.get_mesh().set_simulate_physics(False)
		self.is_valid = True

		self.count = 0 # for movements
		self.dy = 0
	
	def get_parameters(self, params):
		self.location = params.location
		self.rotation = params.rotation
		self.is_long = params.is_long
		self.down = params.down
		self.moves = params.moves
		self.speed = params.speed
	
	def move(self):
		self.count += 1
		self.dy += self.speed

		self.cylinder.set_location(FVector(self.location.x, self.location.y + self.dy,
			self.cylinder.location.z))
		self.axis.set_location(FVector(self.location.x, self.location.y + self.dy,
			self.axis.location.z))

	def get_status(self):
		pass