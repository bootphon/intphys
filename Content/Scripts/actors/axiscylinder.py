import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material
from actors.base_mesh import BaseMesh
from actors.object import Object
from actors.parameters import AxisCylinderParams, ObjectParams

"""
A cylinder with a cylindrical shaft, made from two joined cylinders
"""

class Axiscylinder():
	def __init__(self, world, params=AxisCylinderParams):
		self.get_parameters(params)

		if not self.is_long: # short axis-cylinder
			self.cylinder = Object(world, ObjectParams(
				mesh = 'Cylinder',
				location = FVector(500, 0, 200)))
			self.cylinder.get_mesh().set_simulate_physics(False)

			self.axis = Object(world, ObjectParams(
				mesh = 'Cylinder',
				location = FVector(500, 0, 300),
				scale = FVector(0.25, 0.25, 1)))
			self.axis.get_mesh().set_simulate_physics(False)
		else: # long axis-cylinder
			self.cylinder = Object(world, ObjectParams(
				mesh = 'Cylinder',
				location = FVector(500, 0, 200),
				scale = FVector(1, 1, 2)))
			self.cylinder.get_mesh().set_simulate_physics(False)

			self.axis = Object(world, ObjectParams(
				mesh = 'Cylinder',
				location = FVector(500, 0, 300),
				scale = FVector(0.25, 0.25, 4)))
			self.axis.get_mesh().set_simulate_physics(False)

		self.is_valid = True
	
	def get_parameters(self, params):
		self.location = params.location
		self.rotation = params.rotation
		self.is_long = params.is_long

	def get_status(self):
		pass