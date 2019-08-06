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
        """ Destroys the actor. """
        self.actor.actor_destroy()
        self.actor = None

    def get_parameters(self, location, rotation, overlap, warning):
        """ Gets the parameters.

        Parameters
        ----------
        location: FVector
            Location of the actor
        rotation: FRotator
            Rotation of the actor
        overlap: bool
        warning: bool

        """
        self.location = location
        self.rotation = rotation
        self.overlap = overlap
        self.warning = warning
        self.hidden = False

    def set_parameters(self):
        """ Sets the parameters : set location and rotation, and call the
        methods on_actor_hit (resp. on_actor_overlap) if an actor is
        hit (resp. overlapped).
        """
        self.set_location(self.location)
        self.set_rotation(self.rotation)

        # manage OnActorBeginOverlap events
        if self.warning and self.overlap:
            self.actor.bind_event('OnActorBeginOverlap', self.on_actor_overlap)
        elif self.warning and not self.overlap:
            self.actor.bind_event('OnActorHit', self.on_actor_hit)

    def set_location(self, location):
        """Sets the location of the actor and raise a warning if failed"""
        self.location = location
        if not self.actor.set_actor_location(self.location, False):
            ue.log_warning('Failed to set the location of an actor')
            return False
        return True

    def set_rotation(self, rotation):
        """Sets the rotation of the actor"""
        self.actor.set_actor_rotation(rotation)
        self.rotation = self.actor.get_actor_rotation()
        return True

    def on_actor_overlap(self, me, other):
        """Actors can't overlap.

        When an the actor is overlapping another actor, self.is_valid is
        set at False, and a message is printed.

        Parameters
        ----------
        me: AActor
            The current actor
        othe: AActor
            The actor overlapping the current actor

        """
        if me != other:
            message = '{} overlapping {}'.format(
                self.actor.get_name(), other.get_name())
            ue.log(message)
            self.is_valid = False

    def on_actor_hit(self, me, other, *args):
        """When an the actor is hitting another actor a message is printed.

        Parameters
        ----------
        me: AActor
            The current actor
        othe: AActor
            The actor hitting the current actor
        """
        pass
        # if (other.get_name()[:5] == "Floor" or me == other):
        #     return
        # message = '{} hitting {}'.format(
        #     self.actor.get_name(), other.get_name())
        # ue.log(message)

    def set_hidden(self, hidden):
        """ Sets the hidden parameter

        Parameters
        ----------
        hidden: bool
            If hidden is True, the actor is hidden
        """
        self.hidden = hidden
        self.actor.SetActorHiddenInGame(hidden)

    def get_status(self):
        """ Get the status

        Returns
        -------
        dict
            Status of the actor
        """
        status = {
            'name': self.actor.get_name(),
            # 'type': self.actor.get_name().split('_')[0],
            'location': as_dict(self.location),
            'rotation': as_dict(self.rotation)}
        return status

    def reset(self, params):
        """ Resets the actor with the parametres of parameters.py, hidden is
        set at False.
        """
        self.set_location(params.location)
        self.set_rotation(params.rotation)
        self.set_hidden(False)
