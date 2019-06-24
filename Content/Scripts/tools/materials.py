"""Python interface to load materials from Content/Materials"""

import os
import random
import unreal_engine as ue
from unreal_engine.classes import Material, StaticMesh
from tools.utils import intphys_root_directory

# UNAUTHORIZED is a Dictionary that contains the unauthorized combinations of
# material.
UNAUTHORIZED = {"/Game/Materials/Floor/M_FloorTile_02.M_FloorTile_02" :
                    ["/Game/Materials/Wall/M_Metal_Rust.M_Metal_Rust"]}

def get_random_material(category, material = None):
    """Return a random material for the given category

    Parameters
    ----------
    category: str
        The actor category to choose a material for. Must be 'Floor',
        'Object' or 'Wall'.

    Returns
    -------
    material: str
        The path to a material assset following the UE
        conventions. The material can them be loaded using
        'ue.load_object(Material, material)'.

    Raises
    ------
    ValueError if the requested category is unknown.

    """
    # the list of valid actor categories
    valid_categories = ['Floor', 'Object', 'Wall']
    if category not in valid_categories:
        raise ValueError(
            f'category {category} unknown, must be in {valid_categories}')

    # build the list of possible materials and shuffle it, return the
    # 1st element in it
    available_materials = _load_materials('Materials/' + category)
    if material in UNAUTHORIZED.keys():
        available_materials = list(set(available_materials)-set(UNAUTHORIZED[material]))
    random.shuffle(available_materials)  # in-place list shuffling
    return available_materials[0]


def _get_material_path(path):
    """Convert the `path` to a material asset to its name in UE conventions"""
    base_path = os.path.splitext('/Game/' + path.split('/Content/')[1])[0]
    return base_path + '.' + os.path.basename(base_path)


def _load_materials(path):
    """Return the list of materials found in `path` following UE conventions

    `path` must be relative to the 'intphys/Content' directory

    """
    materials_dir = os.path.join(intphys_root_directory(), 'Content', path)
    if not os.path.isdir(materials_dir):
        raise ValueError('directory not found: {}'.format(materials_dir))

    return [_get_material_path(os.path.join(materials_dir, f))
            for f in os.listdir(materials_dir) if f.endswith('.uasset')]

def load():
     valid_categories = ['Floor', 'Object', 'Wall']
     for category in valid_categories:
         available_materials = _load_materials('Materials/' + category)
         for material in available_materials:
             try:
                 ue.load_object(Material, material)
             except Exception as e:
                 ue.log_warning(e)
     for mesh in _load_materials('Meshes'):
         try:
             ue.load_object(StaticMesh, mesh)
         except Exception as e:
             ue.log_warning(e)
