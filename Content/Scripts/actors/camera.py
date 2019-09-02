import unreal_engine as ue
from unreal_engine.classes import CameraComponent
from unreal_engine.classes import GameplayStatics

from actors.parameters import CameraParams
from tools.utils import as_dict


class Camera:
    _camera_class = ue.load_class('/Game/Camera.Camera_C')

    def __init__(self, world, params=CameraParams()):
        ue.log('camera spawn')
        self._actor = world.actor_spawn(
            self._camera_class, params.location, params.rotation)

        self._actor.bind_event('OnActorBeginOverlap', self._on_overlap)
        self._component = self._actor.get_component_by_type(CameraComponent)

        # Attach the viewport to the camera. This initialization was present
        # in the intphys-1.0 blueprint but seems to be useless in UE-4.17.
        # This is maybe done by default.
        player_controller = GameplayStatics.GetPlayerController(world, 0)
        player_controller.SetViewTargetWithBlend(NewViewTarget=self._actor)

        self._actor.SetTickableWhenPaused(True)
        self._component.SetTickableWhenPaused(True)

        self.field_of_view = params.field_of_view
        self.aspect_ratio = params.aspect_ratio
        self.projection_mode = params.projection_mode
        self._is_valid = True

    def _on_overlap(self, me, other):
        if me != other:
            message = '{} overlapping {}'.format(
                self._actor.get_name(), other.get_name())
            ue.log(message)
            self._is_valid = False

    @property
    def actor(self):
        return self._actor

    @property
    def is_valid(self):
        return self._is_valid

    @property
    def location(self):
        return self._actor.get_actor_location()

    @location.setter
    def location(self, value):
        ue.log('change camera location')
        if not self._actor.set_actor_location(value, False):
            ue.log_warning('Failed to set the camera location')

    @property
    def rotation(self):
        return self._actor.get_actor_rotation()

    @rotation.setter
    def rotation(self, value):
        if not self._actor.set_actor_rotation(value, False):
            ue.log_warning('Failed to set the camera rotation')

    @property
    def field_of_view(self):
        return self._component.FieldOfView

    @field_of_view.setter
    def field_of_view(self, value):
        self._component.SetFieldOfView(value)

    @property
    def aspect_ratio(self):
        return self._component.AspectRatio

    @aspect_ratio.setter
    def aspect_ratio(self, value):
        self._component.SetAspectRatio(value)

    @property
    def projection_mode(self):
        return self._component.ProjectionMode

    @projection_mode.setter
    def projection_mode(self, value):
        self._component.SetProjectionMode(value)

    def setup(self, params=CameraParams()):
        self.location = params.location
        self.rotation = params.rotation
        self.field_of_view = params.field_of_view
        self.aspect_ratio = params.aspect_ratio
        self.projection_mode = params.projection_mode
        self._is_valid = True

    def get_status(self):
        return {
            'name': self._actor.get_name(),
            'location': as_dict(self.location),
            'rotation': as_dict(self.rotation),
            'field_of_view': self.field_of_view,
            'aspect_ratio': self.aspect_ratio,
            'projection_mode': self.projection_mode}
