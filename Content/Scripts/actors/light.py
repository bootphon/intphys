from collections import defaultdict

import unreal_engine as ue
from unreal_engine import FLinearColor
from unreal_engine.classes import SkyLightComponent

from actors.base_actor import BaseActor
from actors.parameters import LightParams

"""
The light is... a light ? which is... lighting something ?
There is 3 kinds of lights :
    Directionnal : like a spot, it points toward somewhere, you chose
        location and rotation
    SkyLight : Diffuse light which doesn't need location or rotation.
        It comes from the skysphere (therefore it needs the skyshpere)
    PointLight : like a bulb. It requires a location
"""


class Light(BaseActor):
    def __init__(self, world, params=LightParams()):
        types = {
            'Directional': '/Game/DirectionalLight.DirectionalLight_C',
            'SkyLight': '/Game/SkyLight.SkyLight_C',
            'PointLight': '/Game/PointLight.PointLight_C'
            }
        super().__init__(
            world.actor_spawn(ue.load_class(types[params.type])))

        self.type = params.type

        self.get_parameters(params)
        self.set_parameters()
        
        """
        if 'Directional' in params.type:
            self.actor.bUsedAsAtmosphereSunLight = True
        """

    def get_parameters(self, params):
        self.color = params.color
        super().get_parameters(params.location, params.rotation, True, False)

    def set_parameters(self):
        super().set_parameters()

        if self.type == 'SkyLight':
            self.skylight_component = self.actor.get_component_by_type(SkyLightComponent)
            self.skylight_component.SetLightColor(self.color)

        # deactivate the physics (we don't want the light to fall)
        # self.get_mesh().set_simulate_physics(False)

    def get_status(self):
        if self.type != 'SkyLight':
            status = super().get_status()
        else:
            status = {}
        status['type'] = self.type
        return status
