import json
import os

import unreal_engine as ue
from unreal_engine.classes import ScreenshotManager


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
    dry_mode : bool, optional
        When False (default), capture PNG images and metadata from the
        rendered scenes. When True, do not take any captures nor save
        any data.

    """
    def __init__(self, size, dry_mode=False, output_dir=None):
        self.size = size
        self.camera = None
        if output_dir is None:
            dry_mode = True
        self.is_dry_mode = dry_mode
        self.output_dir = output_dir

        # an empty list to append status along the run
        self.status_header = {}
        self.status = []

        # initialize the capture.
        verbose = False
        ScreenshotManager.Initialize(
            int(self.size[0]), int(self.size[1]), int(self.size[2]),
            None, verbose)

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
        done, max_depth, masks = ScreenshotManager.Save(output_dir)
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
        masks = {names_map[k]: v for k, v in masks.items()}

        # save images max depth and actors's masks to status
        self.status_header.update({'max_depth': max_depth, 'masks': masks})
        status = {'header': self.status_header, 'frames': self.status}

        # save the status as JSON file
        json_file = os.path.join(output_dir, 'status.json')
        with open(json_file, 'w') as fin:
            fin.write(json.dumps(status, indent=4))

        return True

    def update(self, actors):
        self.camera = actors['Camera']
        ScreenshotManager.SetOriginActor(self.camera.actor)
        res = []
        for name, actor in actors.items():
            if 'wall' in name.lower():
                res.append(actor.left.actor)
                res.append(actor.right.actor)
                res.append(actor.front.actor)
            else:
                res.append(actor.actor)
        ScreenshotManager.SetActors(res)
