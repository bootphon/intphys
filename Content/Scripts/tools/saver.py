import json
import os

import unreal_engine as ue
from unreal_engine.classes import ScreenshotManager
import actors.parameters


class Saver:
    """Take screen captures during a run and save them at the end

    The saver manages screenshots and scene's status. It store them
    during a run and save them at the end, respectively as png images
    (scene, depth and masks) and status.json file.

    Parameters
    ----------
    size : tuple of (width, height, nimages)
        The size of a scene where (width, height) is the screen
        resolution in pixels and nimages the number of images captured
        in a single scene.
    camera : AActor
        The camera actor from which to capture screenshots.
    output_dir : string, optional
        The directory where to save captured images, if None (default) does not
        save anything.

    """
    def __init__(self, size, seed, output_dir=None):
        self.size = size
        self.camera = None
        self.is_dry_mode = True if output_dir is None else False
        self.output_dir = output_dir

        # an empty list to append status along the run
        self.status_header = {}
        self.status = []

        # initialize the capture.
        verbose = False
        ScreenshotManager.Initialize(
            int(self.size[0]), int(self.size[1]), int(self.size[2]),
            None,
            actors.parameters.theoretical_max_depth(),
            seed, verbose)

    def set_status_header(self, header):
        self.status_header = header

    def capture(self, ignored_actors, status):
        """Push the scene's current screenshot and status to memory"""
        if not self.is_dry_mode:
            # scene, depth and masks images are stored from C++
            ScreenshotManager.Capture(ignored_actors)

            # save the current status
            self.status.append(status)

    def reset(self, reset_actors):
        """Reset the saver and delete all data in cache"""
        if not self.is_dry_mode:
            ScreenshotManager.Reset(reset_actors)
            self.status_header = {}
            self.status = []

    def save(self, output_dir):
        """Save the captured data to `output_dir`"""
        if self.is_dry_mode:
            return True

        # save the captured images as PNG
        done, masks = ScreenshotManager.Save(output_dir)
        if not done:
            ue.log_warning('failed to save images to {}'.format(output_dir))
            return False

        # postprocess actor names in masks to be intphys names, and
        # not UE names (to be 'object_1' instead of eg
        # 'Object_C_126'), as well suppress the 'name' field in actor
        # status
        names_map = {
            'Sky': 'sky',
            'Walls': 'walls',
            'AxisCylinders': 'axiscylinders'}

        for k, v in self.status_header.items():
            if isinstance(v, dict) and 'name' in v.keys():
                names_map[v['name']] = k
                del self.status_header[k]['name']
        for i, frame in enumerate(self.status):
            for k, v in frame.items():
                if isinstance(v, dict) and 'name' in v.keys():
                    names_map[v['name']] = k
                    del self.status[i][k]['name']

        # postprocess the masks to make it JSON compatible and save it to
        # status
        masks = self.parse_masks(masks, names_map)
        for i in range(len(self.status)):
            self.status[i].update({'masks': masks[i]})
        status = {'header': self.status_header, 'frames': self.status}

        # save the status as JSON file
        json_file = os.path.join(output_dir, 'status.json')
        with open(json_file, 'w') as fin:
            fin.write(json.dumps(status, indent=4))

        return True

    def update(self, actors):
        self.camera = actors['Camera']
        ScreenshotManager.SetOriginActor(self.camera.actor)

    def parse_masks(self, masks, names_map):
        parsed = [{} for _ in range(self.size[2])]
        for mask in masks:
            frame, actor, gray_level = tuple(mask.split('__'))
            frame = int(frame) - 1
            actor = names_map[actor]
            gray_level = int(gray_level)
            parsed[frame].update({actor: gray_level})
        return parsed
