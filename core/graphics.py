#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Graphics pack management."""
from __future__ import print_function, unicode_literals, absolute_import

import sys, os, shutil, glob, tempfile
import distutils.dir_util as dir_util
from .launcher import open_folder
from .lnp import lnp
from . import df, paths

def open_graphics():
    """Opens the graphics pack folder."""
    open_folder(paths.get('graphics'))

def current_pack():
    """
    Returns the currently installed graphics pack.
    If the pack cannot be identified, returns "FONT/GRAPHICS_FONT".
    """
    packs = read_graphics()
    for p in packs:
        if (lnp.settings.FONT == p[1] and
                lnp.settings.GRAPHICS_FONT == p[2]):
            return p[0]
    return str(lnp.settings.FONT)+'/'+str(lnp.settings.GRAPHICS_FONT)

def read_graphics():
    """Returns a list of graphics directories."""
    packs = [
        os.path.basename(o) for o in
        glob.glob(os.path.join(paths.get('graphics'), '*')) if
        os.path.isdir(o)]
    result = []
    for p in packs:
        font = lnp.settings.read_value(os.path.join(
            paths.get('graphics'), p, 'data', 'init', 'init.txt'), 'FONT')
        graphics = lnp.settings.read_value(
            os.path.join(paths.get('graphics'), p, 'data', 'init', 'init.txt'),
            'GRAPHICS_FONT')
        result.append((p, font, graphics))
    return tuple(result)

def install_graphics(pack):
    """
    Installs the graphics pack located in LNP/Graphics/<pack>.

    Params:
        pack
            The name of the pack to install.

    Returns:
        True if successful,
        False if an exception occured
        None if required files are missing (raw/graphics, data/init)
    """
    gfx_dir = os.path.join(paths.get('graphics'), pack)
    if (os.path.isdir(gfx_dir) and
            os.path.isdir(os.path.join(gfx_dir, 'raw', 'graphics')) and
            os.path.isdir(os.path.join(gfx_dir, 'data', 'init'))):
        try:
            # Delete old graphics
            if os.path.isdir(os.path.join(paths.get('df'), 'raw', 'graphics')):
                dir_util.remove_tree(
                    os.path.join(paths.get('df'), 'raw', 'graphics'))
            # Copy new raws
            dir_util.copy_tree(
                os.path.join(gfx_dir, 'raw'),
                os.path.join(paths.get('df'), 'raw'))
            if os.path.isdir(os.path.join(paths.get('data'), 'art')):
                dir_util.remove_tree(
                    os.path.join(paths.get('data'), 'art'))
            dir_util.copy_tree(
                os.path.join(gfx_dir, 'data', 'art'),
                os.path.join(paths.get('data'), 'art'))
            patch_inits(gfx_dir)
            shutil.copyfile(
                os.path.join(gfx_dir, 'data', 'init', 'colors.txt'),
                os.path.join(paths.get('init'), 'colors.txt'))
            try: # TwbT support
                os.remove(os.path.join(paths.get('init'), 'overrides.txt'))
            except:
                pass
            try: # TwbT support
                shutil.copyfile(
                    os.path.join(gfx_dir, 'data', 'init', 'overrides.txt'),
                    os.path.join(paths.get('init'), 'overrides.txt'))
            except:
                pass
        except Exception:
            sys.excepthook(*sys.exc_info())
            return False
        else:
            return True
    else:
        return None
    df.load_params()

def patch_inits(gfx_dir):
    """
    Installs init files from a graphics pack by selectively changing
    specific fields. All settings outside of the mentioned fields are
    preserved.

    TODO: Consider if there's a better option than listing all fields
    explicitly...
    """
    d_init_fields = [
        'WOUND_COLOR_NONE', 'WOUND_COLOR_MINOR',
        'WOUND_COLOR_INHIBITED', 'WOUND_COLOR_FUNCTION_LOSS',
        'WOUND_COLOR_BROKEN', 'WOUND_COLOR_MISSING', 'SKY', 'CHASM',
        'PILLAR_TILE',
        # Tracks
        'TRACK_N', 'TRACK_S', 'TRACK_E', 'TRACK_W', 'TRACK_NS',
        'TRACK_NE', 'TRACK_NW', 'TRACK_SE', 'TRACK_SW', 'TRACK_EW',
        'TRACK_NSE', 'TRACK_NSW', 'TRACK_NEW', 'TRACK_SEW',
        'TRACK_NSEW', 'TRACK_RAMP_N', 'TRACK_RAMP_S', 'TRACK_RAMP_E',
        'TRACK_RAMP_W', 'TRACK_RAMP_NS', 'TRACK_RAMP_NE',
        'TRACK_RAMP_NW', 'TRACK_RAMP_SE', 'TRACK_RAMP_SW',
        'TRACK_RAMP_EW', 'TRACK_RAMP_NSE', 'TRACK_RAMP_NSW',
        'TRACK_RAMP_NEW', 'TRACK_RAMP_SEW', 'TRACK_RAMP_NSEW',
        # Trees
        'TREE_ROOT_SLOPING', 'TREE_TRUNK_SLOPING',
        'TREE_ROOT_SLOPING_DEAD', 'TREE_TRUNK_SLOPING_DEAD',
        'TREE_ROOTS', 'TREE_ROOTS_DEAD', 'TREE_BRANCHES',
        'TREE_BRANCHES_DEAD', 'TREE_SMOOTH_BRANCHES',
        'TREE_SMOOTH_BRANCHES_DEAD', 'TREE_TRUNK_PILLAR',
        'TREE_TRUNK_PILLAR_DEAD', 'TREE_CAP_PILLAR',
        'TREE_CAP_PILLAR_DEAD', 'TREE_TRUNK_N', 'TREE_TRUNK_S',
        'TREE_TRUNK_N_DEAD', 'TREE_TRUNK_S_DEAD', 'TREE_TRUNK_EW',
        'TREE_TRUNK_EW_DEAD', 'TREE_CAP_WALL_N', 'TREE_CAP_WALL_S',
        'TREE_CAP_WALL_N_DEAD', 'TREE_CAP_WALL_S_DEAD', 'TREE_TRUNK_E',
        'TREE_TRUNK_W', 'TREE_TRUNK_E_DEAD', 'TREE_TRUNK_W_DEAD',
        'TREE_TRUNK_NS', 'TREE_TRUNK_NS_DEAD', 'TREE_CAP_WALL_E',
        'TREE_CAP_WALL_W', 'TREE_CAP_WALL_E_DEAD',
        'TREE_CAP_WALL_W_DEAD', 'TREE_TRUNK_NW', 'TREE_CAP_WALL_NW',
        'TREE_TRUNK_NW_DEAD', 'TREE_CAP_WALL_NW_DEAD', 'TREE_TRUNK_NE',
        'TREE_CAP_WALL_NE', 'TREE_TRUNK_NE_DEAD',
        'TREE_CAP_WALL_NE_DEAD', 'TREE_TRUNK_SW', 'TREE_CAP_WALL_SW',
        'TREE_TRUNK_SW_DEAD', 'TREE_CAP_WALL_SW_DEAD', 'TREE_TRUNK_SE',
        'TREE_CAP_WALL_SE', 'TREE_TRUNK_SE_DEAD',
        'TREE_CAP_WALL_SE_DEAD', 'TREE_TRUNK_NSE',
        'TREE_TRUNK_NSE_DEAD', 'TREE_TRUNK_NSW', 'TREE_TRUNK_NSW_DEAD',
        'TREE_TRUNK_NEW', 'TREE_TRUNK_NEW_DEAD', 'TREE_TRUNK_SEW',
        'TREE_TRUNK_SEW_DEAD', 'TREE_TRUNK_NSEW',
        'TREE_TRUNK_NSEW_DEAD', 'TREE_TRUNK_BRANCH_N',
        'TREE_TRUNK_BRANCH_N_DEAD', 'TREE_TRUNK_BRANCH_S',
        'TREE_TRUNK_BRANCH_S_DEAD', 'TREE_TRUNK_BRANCH_E',
        'TREE_TRUNK_BRANCH_E_DEAD', 'TREE_TRUNK_BRANCH_W',
        'TREE_TRUNK_BRANCH_W_DEAD', 'TREE_BRANCH_NS',
        'TREE_BRANCH_NS_DEAD', 'TREE_BRANCH_EW', 'TREE_BRANCH_EW_DEAD',
        'TREE_BRANCH_NW', 'TREE_BRANCH_NW_DEAD', 'TREE_BRANCH_NE',
        'TREE_BRANCH_NE_DEAD', 'TREE_BRANCH_SW', 'TREE_BRANCH_SW_DEAD',
        'TREE_BRANCH_SE', 'TREE_BRANCH_SE_DEAD', 'TREE_BRANCH_NSE',
        'TREE_BRANCH_NSE_DEAD', 'TREE_BRANCH_NSW',
        'TREE_BRANCH_NSW_DEAD', 'TREE_BRANCH_NEW',
        'TREE_BRANCH_NEW_DEAD', 'TREE_BRANCH_SEW',
        'TREE_BRANCH_SEW_DEAD', 'TREE_BRANCH_NSEW',
        'TREE_BRANCH_NSEW_DEAD', 'TREE_TWIGS', 'TREE_TWIGS_DEAD',
        'TREE_CAP_RAMP', 'TREE_CAP_RAMP_DEAD', 'TREE_CAP_FLOOR1',
        'TREE_CAP_FLOOR2', 'TREE_CAP_FLOOR1_DEAD',
        'TREE_CAP_FLOOR2_DEAD', 'TREE_CAP_FLOOR3', 'TREE_CAP_FLOOR4',
        'TREE_CAP_FLOOR3_DEAD', 'TREE_CAP_FLOOR4_DEAD',
        'TREE_TRUNK_INTERIOR', 'TREE_TRUNK_INTERIOR_DEAD']
    init_fields = [
        'FONT', 'FULLFONT', 'GRAPHICS', 'GRAPHICS_FONT',
        'GRAPHICS_FULLFONT', 'TRUETYPE']
    lnp.settings.read_file(
        os.path.join(gfx_dir, 'data', 'init', 'init.txt'), init_fields,
        False)
    lnp.settings.read_file(
        os.path.join(gfx_dir, 'data', 'init', 'd_init.txt'), d_init_fields,
        False)
    df.save_params()

def simplify_graphics():
    """Removes unnecessary files from all graphics packs."""
    for pack in read_graphics():
        simplify_pack(pack)

def simplify_pack(pack):
    """
    Removes unnecessary files from LNP/Graphics/<pack>.

    Params:
        pack
            The pack to simplify.

    Returns:
        The number of files removed if successful
        False if an exception occurred
        None if folder is empty
    """
    pack = os.path.join(paths.get('graphics'), pack)
    files_before = sum(len(f) for (_, _, f) in os.walk(pack))
    if files_before == 0:
        return None
    tmp = tempfile.mkdtemp()
    try:
        dir_util.copy_tree(pack, tmp)
        if os.path.isdir(pack):
            dir_util.remove_tree(pack)

        os.makedirs(pack)
        os.makedirs(os.path.join(pack, 'data', 'art'))
        os.makedirs(os.path.join(pack, 'raw', 'graphics'))
        os.makedirs(os.path.join(pack, 'raw', 'objects'))
        os.makedirs(os.path.join(pack, 'data', 'init'))

        dir_util.copy_tree(
            os.path.join(tmp, 'data', 'art'),
            os.path.join(pack, 'data', 'art'))
        dir_util.copy_tree(
            os.path.join(tmp, 'raw', 'graphics'),
            os.path.join(pack, 'raw', 'graphics'))
        dir_util.copy_tree(
            os.path.join(tmp, 'raw', 'objects'),
            os.path.join(pack, 'raw', 'objects'))
        shutil.copyfile(
            os.path.join(tmp, 'data', 'init', 'colors.txt'),
            os.path.join(pack, 'data', 'init', 'colors.txt'))
        shutil.copyfile(
            os.path.join(tmp, 'data', 'init', 'init.txt'),
            os.path.join(pack, 'data', 'init', 'init.txt'))
        shutil.copyfile(
            os.path.join(tmp, 'data', 'init', 'd_init.txt'),
            os.path.join(pack, 'data', 'init', 'd_init.txt'))
        shutil.copyfile(
            os.path.join(tmp, 'data', 'init', 'overrides.txt'),
            os.path.join(pack, 'data', 'init', 'overrides.txt'))
    except IOError:
        sys.excepthook(*sys.exc_info())
        retval = False
    else:
        files_after = sum(len(f) for (_, _, f) in os.walk(pack))
        retval = files_after - files_before
    if os.path.isdir(tmp):
        dir_util.remove_tree(tmp)
    return retval

def update_savegames():
    """Update save games with current raws."""
    saves = [
        o for o in glob.glob(os.path.join(paths.get('save'), '*'))
        if os.path.isdir(o) and not o.endswith('current')]
    count = 0
    if saves:
        for save in saves:
            count = count + 1
            # Delete old graphics
            if os.path.isdir(os.path.join(save, 'raw', 'graphics')):
                dir_util.remove_tree(os.path.join(save, 'raw', 'graphics'))
            # Copy new raws
            dir_util.copy_tree(
                os.path.join(paths.get('df'), 'raw'),
                os.path.join(save, 'raw'))
    return count

