# coding: utf-8

import unreal_engine as ue
from unreal_engine.classes import Material, StaticMesh, Friction

from actors.base_actor import BaseActor
from tools.utils import as_dict


class BaseMesh(BaseActor):
    """
    BaseMesh inherits from BaseActor.
    It is the base class of every python component build with a mesh.
    """

    def __init__(self, actor):
        super().__init__(actor)

    def get_parameters(self, location, rotation,
                       scale, friction, restitution,
                       overlap, warning, mesh_str):
        """ Gets the parameters.

        Parameters
        ----------
        location: FVector
            Location of the actor
        rotation: FRotator
            Rotation of the actor
        scale: FVector
            Scale of the actor
        friction:
        restitution:
        overlap: bool
        warning: bool
        mesh_str: str

        """
        super().get_parameters(location, rotation, overlap, warning)
        self.scale = scale
        self.friction = friction
        self.restitution = restitution
        self.mesh_str = mesh_str

    def set_parameters(self):
        """Sets the parameters

        Set location, rotation, mesh, scale, friction, restitution and call the
        methods on_actor_hit (resp. on_actor_overlap) if an actor is hit (resp.
        overlapped).

        """
        super().set_parameters()
        self.set_mesh()
        self.set_scale(self.scale)
        self.set_friction(self.friction)
        self.set_restitution(self.restitution)
        if self.overlap is False:
            self.mesh.call('SetCollisionProfileName BlockAll')

    def set_mesh(self):
        """Sets the mesh and set the material"""
        self.mesh = self.actor.get_actor_component_by_type(
            ue.find_class('StaticMeshComponent'))
        # setup mesh and material
        self.mesh.SetStaticMesh(ue.load_object(StaticMesh, self.mesh_str))
        self.mesh.set_material(0, self.material)

    def get_mesh(self):
        """ Gets the mesh
        """
        return self.actor.get_actor_component_by_type(
            ue.find_class('StaticMeshComponent'))

    def set_mesh_str(self, mesh_str):
        """
        Changes the current mesh by another.

        Parameters
        ----------
        mesh_str: str
            Mesh that replaces the current one.
        """
        self.mesh_str = mesh_str
        self.mesh.SetStaticMesh(ue.load_object(StaticMesh, self.mesh_str))

    def set_material(self, material_str):
        """
        Sets the material

        Parameters
        ----------
        material_str: str
            Material to set

        """
        self.material = ue.load_object(Material, material_str)
        self.mesh.set_material(0, self.material)

    def set_scale(self, scale):
        """ Sets the scale"""
        self.scale = scale
        self.actor.set_actor_scale(self.scale)

    def set_friction(self, friction):
        """ Sets the coefficient of friction"""
        self.friction = friction
        Friction.SetFriction(self.material, friction)

    def set_restitution(self, restitution):
        """ Sets the coefficient of restitution"""
        self.restitution = restitution
        Friction.SetRestitution(self.material, self.restitution)

    def get_status(self):
        """ Returns the current status of the actor"""
        status = super().get_status()
        status['scale'] = as_dict(self.scale)
        status['friction'] = self.friction
        status['restitution'] = self.restitution
        return status

    def reset(self, params):
        """Resets the actor with the parametres of parameters.py, hidden is
        set at False.
        """
        super().reset(params)
        self.set_scale(params.scale)
        self.set_material(params.material)
        self.set_friction(params.friction)
        self.set_restitution(params.restitution)
