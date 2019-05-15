# coding: utf-8

import unreal_engine as ue
from unreal_engine.classes import Material, StaticMesh, Friction

from actors.base_actor import BaseActor
from tools.utils import as_dict

"""
BaseMesh inherits from BaseActor.
It is the base class of every python component build with a mesh.
"""


class BaseMesh(BaseActor):
    def __init__(self, actor):
        super().__init__(actor)

    def get_parameters(self, location, rotation,
                       scale, friction, restitution,
                       overlap, warning, mesh_str):
        super().get_parameters(location, rotation, overlap, warning)
        self.scale = scale
        self.friction = friction
        self.restitution = restitution
        self.mesh_str = mesh_str

    def set_parameters(self):
        super().set_parameters()
        self.set_mesh()
        self.set_scale(self.scale)
        self.set_friction(self.friction)
        self.set_restitution(self.restitution)
        if self.overlap is False:
            self.mesh.call('SetCollisionProfileName BlockAll')

    """
    set_mesh sets the mesh and set the material
    """
    def set_mesh(self):
        self.mesh = self.actor.get_actor_component_by_type(
            ue.find_class('StaticMeshComponent'))
        # setup mesh and material
        self.mesh.SetStaticMesh(ue.load_object(StaticMesh, self.mesh_str))
        self.mesh.set_material(0, self.material)

    def get_mesh(self):
        return self.actor.get_actor_component_by_type(
            ue.find_class('StaticMeshComponent'))

    """
    set_mesh_str change the current mesh by another
    """
    def set_mesh_str(self, mesh_str):
        self.mesh_str = mesh_str
        self.mesh.SetStaticMesh(ue.load_object(StaticMesh, self.mesh_str))

    def set_material(self, material_str):
        self.material = ue.load_object(Material, material_str)
        self.mesh.set_material(0, self.material)

    def set_scale(self, scale):
        self.scale = scale
        self.actor.set_actor_scale(self.scale)

    def set_friction(self, friction):
        self.friction = friction
        Friction.SetFriction(self.material, friction)

    def set_restitution(self, restitution):
        self.restitution = restitution
        Friction.SetRestitution(self.material, self.restitution)

    def get_status(self):
        status = super().get_status()
        status['scale'] = as_dict(self.scale)
        status['friction'] = self.friction
        status['restitution'] = self.restitution
        return status

    def reset(self, params):
        super().reset(params)
        self.set_scale(params.scale)
        self.set_material(params.material)
        self.set_friction(params.friction)
        self.set_restitution(params.restitution)
