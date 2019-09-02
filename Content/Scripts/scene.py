import os
import importlib
import unreal_engine as ue


class Scene:
    def __init__(self, world, saver, category):
        self.world = world
        self.params = {}
        self.saver = saver
        self.category = category

        self.generate_parameters()

        self.actors = None
        self.run = 0
        self.last_locations = []

    def get_status(self):
        """Return the current status of each MOVING actor in the scene"""
        if self.actors is not None:
            return {k.lower(): v.get_status() for k, v in self.actors.items()
                    if 'object' in k or 'occluder' in k}

    def get_status_header(self):
        """Return the status of each CONSTANT actor in the scene"""
        header = {
            'block_name': self.name,
            'block_type': (
                'train' if 'Train' in type(self).__name__ else 'test'),
            'is_possible': self.is_possible()}
        for k, v in self.actors.items():
            if 'object' not in k and 'occluder' not in k:
                header[k.lower()] = v.get_status()
        return header

    def generate_parameters(self):
        raise NotImplementedError

    def play_run(self):
        if self.run == 0:
            self.spawn_actors()

    def stop_run(self):
        self.saver.set_status_header(self.get_status_header())

    def is_valid(self):
        return all([a.is_valid for a in self.actors.values()])

    def is_possible(self):
        """Return True if the current run is plausible, False otherwise"""
        # implementation delegated to Train and Test subclasses
        raise NotImplementedError

    def is_test_scene(self):
        """Return True if this is a Test scene, False for a Train scene"""
        # implementation delegated to Train and Test subclasses
        raise NotImplementedError

    def spawn_actors(self):
        self.actors = {}
        for actor, actor_params in self.params.items():
            if ('magic' in actor):
                # the magic trick is managed by test classes
                continue
            elif actor == 'Camera':
                # the camera is managed by the director, not by the scene
                continue
            else:
                class_name = actor.split('_')[0].title()

            ue.log('spawning {}'.format(actor))
            # dynamically import and instantiate the actor's class
            module_path = "actors.{}".format(actor.lower().split('_')[0])
            module = importlib.import_module(module_path)

            try:
                self.actors[actor] = getattr(module, class_name)(
                    world=self.world, params=actor_params)
            except RuntimeError:
                ue.log('failed to spawn {}'.format(actor))

    def reset_actors(self):
        for name, actor in self.actors.items():
            if 'object' in name.lower() or 'occluder' in name.lower():
                actor.reset(self.params[name])

    def del_actors(self):
        for actor in self.actors.values():
            actor.actor_destroy()
        self.actors = None

    def get_nobjects(self):
        """Return the number of objetcs in the scene"""
        return len([k for k in self.params.keys() if 'object' in k])

    def get_scene_subdir(self, scene_index, total):
        # build the scene sub-directory name, for exemple
        # 'test/O1/006' or
        # 'dev/O4/39' or
        # 'train/1029'
        idx = scene_index + 1

        # putting as much zeroes as necessary according
        # to the total number of scenes
        padded_idx = str(idx).zfill(len(str(total)))
        if 'train' in self.category:
            scene_name = (
                'train/' +
                padded_idx)
        else:
            scene_name = (
                self.category + '/' +
                self.name +
                '/' + padded_idx)
        out = os.path.join(self.saver.output_dir, scene_name)

        if 'Test' in type(self).__name__:
            # 1, 2, 3 and 4 subdirectories for test scenes
            run_idx = self.run + 1
            out = os.path.join(out, str(run_idx))

        return out

    def tick(self):
        if self.actors is not None:
            for actor_name, actor in self.actors.items():
                if (
                        'object' in actor_name
                        or 'occluder' in actor_name
                        or 'axiscylinder' in actor_name
                        or 'pill' in actor_name
                ):
                    actor.move()
