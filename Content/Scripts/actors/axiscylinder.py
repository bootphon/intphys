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

The down variable defines wether the small end of the AxisCylinder is at top (False) or bottom (True).
It has no effect on long AxisCylinders.

The moves variable describes the movement as such:
	[[speed1, loc1], [speed2, loc2], ...],
where locN is the y-location where the object changes speed to speedN+1
"""

class Axiscylinder(BaseMesh):

	length = {
		'Lollipop': '/Game/Meshes/Lollipop.Lollipop',
        'RollingPin': '/Game/Meshes/Rolling_Pin.Rolling_Pin'
	}

	def __init__(self, world, params=AxisCylinderParams()):
		super().__init__(
            world.actor_spawn(ue.load_class('/Game/AxisCylinder.AxisCylinder_C')))
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
		self.is_long = params.is_long
		self.down = params.down
		self.moves = params.moves

		self.current_move = 0
		self.speed = self.moves[self.current_move][0]

		self.location.z += 50
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
		if abs(self.location.y - self.moves[self.current_move][1]) < 3.0:
			self.current_move += 1
			self.speed = self.moves[self.current_move][0]
		
		self.set_location(FVector(
			self.location.x,
			self.location.y + self.speed,
			self.location.z))
