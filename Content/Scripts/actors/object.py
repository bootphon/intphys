# coding: utf-8

import unreal_engine as ue
from unreal_engine.classes import Material, Friction
from unreal_engine import FVector

from actors.base_mesh import BaseMesh
from actors.parameters import ObjectParams
from tools.utils import as_dict

# Object is the python component for the main actors of the magic
# tricks (the sphere, the cube, or else).  It inherits from BaseMesh.


class Object(BaseMesh):
    """
    shape is a dictionnary with the path of every
    shape (mesh) available for the Object actor
    """
    shape = {
        'Sphere': '/Game/Meshes/Sphere.Sphere',
        'Cube': '/Game/Meshes/Cube.Cube',
        'Cone': '/Game/Meshes/Cone.Cone',
        # we exclude cylinder because it looks like a cube (from a face)
        # or like a sphere (from the other face)
        # 'Cylinder': '/Game/Meshes/Cylinder.Cylinder'
    }

    # factor to normalize the mass of meshes wrt the mass of a sphere
    # at scale 1. This is usefull to force objects to have the same
    # trajectories when submitted to the same force.
    mass_factor = {
        'Sphere': 1.0,
        'Cube': 0.6155297517867,
        'Cone': 1.6962973279499}

    def __init__(self, world, params=ObjectParams()):
        super().__init__(
            world.actor_spawn(ue.load_class('/Game/Object.Object_C')))
        self.get_parameters(params)
        self.set_parameters()

    def get_parameters(self, params):
        # adjust the location.z to be placed at the bottom of the mesh
        # (by default the pivot is on the middle), mesh is 100x100x100
        location = FVector(
                params.location.x,
                params.location.y,
                params.location.z + (50 * params.scale.z))
        super().get_parameters(
            location,
            params.rotation,
            params.scale,
            params.friction,
            params.restitution,
            params.overlap,
            params.warning,
            self.shape[params.mesh])
        self.material = ue.load_object(Material, params.material)
        self.mass = params.mass
        self.force = params.force
        self.initial_force = params.initial_force

    def set_parameters(self):
        super().set_parameters()
        self.set_mass(self.mass)
        self.set_force(self.force)
        self.get_mesh().set_simulate_physics()

    """
    set the mass of the mesh
    to be honnest I don't really know what the second line do
    """
    def set_mass(self, mass):
        self.mass = mass
        # set the mass scale differently for each shape
        Friction.SetMassScale(self.mesh,
                              self.mass_factor[self.mesh_str.split('.')[-1]])
        self.mesh.SetMassScale(
            BoneName='None',
            InMassScale=self.mass / self.mesh.GetMassScale())

    """
    If set to True, persistent will make the force apply to the object at
    every tick
    """
    def set_force(self, force, persistent=False):
        if (persistent):
            self.force = force
        # the heavier the object is, the more violent the applied force will be
        self.get_mesh().add_force(force *
                                  self.mesh.GetMass())

    """
    Apply peristent force to the mesh
    """
    def move(self):
        self.get_mesh().add_force(self.force)
        self.location = self.actor.get_actor_location()
        self.rotation = self.actor.get_actor_rotation()

    def get_status(self):
        status = super().get_status()
        status['material'] = self.material.get_name()
        status['mass'] = self.mesh.GetMass()
        # status['force'] = as_dict(self.force)
        status['initial_force'] = as_dict(self.initial_force)
        status['velocity'] = as_dict(self.actor.get_actor_velocity())
        status['shape'] = self.mesh_str.split(".")[-1]
        return status

    def reset(self, params):
        # BaseActor.reset(params)
        location = FVector(
                params.location.x,
                params.location.y,
                params.location.z + (50 * params.scale.z))
        self.set_location(location)
        self.set_rotation(params.rotation)
        self.set_hidden(False)
        self.set_mesh_str(self.shape[params.mesh])
        self.set_scale(params.scale)
        self.set_material(params.material)
        self.set_friction(params.friction)
        self.set_restitution(params.restitution)
        self.get_mesh().set_simulate_physics(False)
        self.get_mesh().set_simulate_physics()

    def reset_force(self):
        self.get_mesh().set_simulate_physics(False)
        self.get_mesh().set_simulate_physics()
