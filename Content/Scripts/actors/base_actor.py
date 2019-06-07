import unreal_engine as ue
from tools.utils import as_dict


class BaseActor():
    """BaseActor is the very base of the actors inheritance tree

    It is the base class of every python component build with an actor
    (all of them, though).

    Parameters
    ----------
    actor: UObject
        The spawned actor

    """
    def __init__(self, actor):
        self.actor = actor

        # this flag becomes False when something illegal occurs to
        # that actor (e.g. an overlap)
        self.is_valid = True

    def actor_destroy(self):
        self.actor.actor_destroy()
        self.actor = None

    def get_parameters(self, location, rotation, overlap, warning):
        self.location = location
        self.rotation = rotation
        self.overlap = overlap
        self.warning = warning
        self.hidden = False

    def set_parameters(self):
        self.set_location(self.location)
        self.set_rotation(self.rotation)

        # manage OnActorBeginOverlap events
        if self.warning and self.overlap:
            self.actor.bind_event('OnActorBeginOverlap', self.on_actor_overlap)
        elif self.warning and not self.overlap:
            self.actor.bind_event('OnActorHit', self.on_actor_hit)

    def set_location(self, location):
        self.location = location
        if not self.actor.set_actor_location(self.location, False):
            ue.log_warning('Failed to set the location of an actor')
            return False
        return True

    def set_rotation(self, rotation):
        # if not self.actor.set_actor_rotation(rotation):
        # the set_actor_rotation is very strict, looks for
        # equality in asked and obtained rotation. We tolerate an
        # epsilon of e-3.
        # r0 = self.actor.get_actor_rotation()
        self.actor.set_actor_rotation(rotation)
        self.rotation = self.actor.get_actor_rotation()
        """
        r1, r2 = rotation, self.actor.get_actor_rotation()
        rd = [abs(d) for d in (
            r0.roll - r1.roll, r0.yaw - r1.yaw, r0.pitch - r1.pitch)]
        if max(rd) > 1e-3:
            ue.log_warning(
                f'Failed to set the rotation of {self.actor.get_name()}, '
                f'had {str(r0)}, asked {str(r1)} but have {str(r2)}')
            return False
        """
        return True

    def on_actor_overlap(self, me, other):
        if (me == other):
            return
        message = '{} overlapping {}'.format(
            self.actor.get_name(), other.get_name())
        ue.log(message)
        self.is_valid = False

    def on_actor_hit(self, me, other, *args):
        if (other.get_name()[:5] == "Floor" or me == other):
            return
        message = '{} hitting {}'.format(
            self.actor.get_name(), other.get_name())
        ue.log(message)

    def set_hidden(self, hidden):
        self.hidden = hidden
        self.actor.SetActorHiddenInGame(hidden)

    def get_status(self):
        status = {
            'name': self.actor.get_name(),
            # 'type': self.actor.get_name().split('_')[0],
            'location': as_dict(self.location),
            'rotation': as_dict(self.rotation)}
        return status

    def reset(self, params):
        self.set_location(params.location)
        self.set_rotation(params.rotation)
        self.set_hidden(False)
