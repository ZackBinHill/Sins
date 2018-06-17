# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/14/2018
import os
from sins.utils.color import rgba_to_int10


DEFAULT_DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'default_data')


cmp_description = 'Compositing is the combining of visual elements from separate sources into single images, ' \
                  'often to create the illusion that all those elements are parts of the same scene. ' \
                  'Live-action shooting for compositing is variously called "chroma key", "blue screen", ' \
                  '"green screen" and other names. Today, most, though not all, ' \
                  'compositing is achieved through digital image manipulation'
lgt_description = 'Lighting or illumination is the deliberate use of light to achieve a practical or aesthetic effect.'
mod_description = 'In 3D computer graphics, 3D modeling (or three-dimensional modeling) is the process of ' \
                  'developing a mathematical representation of any surface of an object (either inanimate or living) ' \
                  'in three dimensions via specialized software. '
ani_description = 'Computer animation is the art of creating moving images via the use of computers. ' \
                  'It is a subfield of computer graphics and animation.'

Department = [
    {'code': 'CMP', 'full_name': 'compositing', 'description': cmp_description, 'color': rgba_to_int10([87, 212, 113], alpha_index=0, max=255)},
    {'code': 'LGT', 'full_name': 'lighting', 'description': lgt_description, 'color': rgba_to_int10([87, 212, 113], alpha_index=0, max=255)},
    {'code': 'MOD', 'full_name': 'model', 'description': mod_description, 'color': rgba_to_int10([87, 212, 113], alpha_index=0, max=255)},
    {'code': 'TEX', 'full_name': 'texture', 'description': '', 'color': rgba_to_int10([87, 212, 113], alpha_index=0, max=255)},
    {'code': 'MTP', 'full_name': 'matte painting', 'description': '', 'color': rgba_to_int10([87, 212, 113], alpha_index=0, max=255)},
    {'code': 'RIG', 'full_name': 'rigging', 'description': '', 'color': rgba_to_int10([87, 212, 113], alpha_index=0, max=255)},
    {'code': 'ANI', 'full_name': 'animation', 'description': ani_description, 'color': rgba_to_int10([87, 212, 113], alpha_index=0, max=255)},
    {'code': 'EFX', 'full_name': 'effects', 'description': '', 'color': rgba_to_int10([87, 212, 113], alpha_index=0, max=255)},
    {'code': 'PRV', 'full_name': 'preview', 'description': '', 'color': rgba_to_int10([87, 212, 113], alpha_index=0, max=255)},
    {'code': 'ROT', 'full_name': 'roto paint', 'description': '', 'color': rgba_to_int10([87, 212, 113], alpha_index=0, max=255)},
    {'code': 'EDI', 'full_name': 'editing', 'description': '', 'color': rgba_to_int10([87, 212, 113], alpha_index=0, max=255)},
]


PermissionGroup = [
    {'code': 'Artist'},
    {'code': 'Lead'},
    {'code': 'Manager'},
    {'code': 'Supervisor'},
    {'code': 'Coordinator'},
    {'code': 'Read-only'},
    {'code': 'Root'},
]


Status = [
    {'name': 'wts', 'full_name': 'wait to start', 'color': None, 'referred_table': 'Project;Shot;Sequence;Asset;Task'},
    {'name': 'wip', 'full_name': 'work in progress', 'color': None, 'referred_table': 'Project;Shot;Sequence;Asset;Task;Version'},
    {'name': 'fin', 'full_name': 'final', 'color': None, 'referred_table': 'Project;Shot;Sequence;Asset;Task'},
    {'name': 'hld', 'full_name': 'hold', 'color': None, 'referred_table': 'Project;Shot;Sequence;Asset'},
    {'name': 'cld', 'full_name': 'cancelled', 'color': None, 'referred_table': 'Project;Shot;Sequence;Asset'},
    {'name': 'smtr', 'full_name': 'submit to review', 'color': None, 'referred_table': 'Version'},
    {'name': 'smts', 'full_name': 'submit to supervisor', 'color': None, 'referred_table': 'Version'},
    {'name': 'smtc', 'full_name': 'submit to client', 'color': None, 'referred_table': 'Version'},
    {'name': 'aprl', 'full_name': 'approve by lead', 'color': None, 'referred_table': 'Version'},
    {'name': 'aprs', 'full_name': 'approve by supervisor', 'color': None, 'referred_table': 'Version'},
    {'name': 'aprc', 'full_name': 'approve by client', 'color': None, 'referred_table': 'Version'},
]


PipelineStep = [
    {'name': 'cmp', 'color': rgba_to_int10([87, 212, 113], max=255, alpha_index=0)},
    {'name': 'lay', 'color': rgba_to_int10([229, 211, 204], max=255, alpha_index=0)},
    {'name': 'lgt', 'color': rgba_to_int10([202, 237, 111], max=255, alpha_index=0)},
    {'name': 'rig', 'color': rgba_to_int10([229, 201, 209], max=255, alpha_index=0)},
    {'name': 'pnt', 'color': rgba_to_int10([114, 73, 47], max=255, alpha_index=0)},
    {'name': 'rto', 'color': rgba_to_int10([107, 88, 52], max=255, alpha_index=0)},
    {'name': 'pla', 'color': rgba_to_int10([119, 238, 254], max=255, alpha_index=0)},
    {'name': 'ani', 'color': rgba_to_int10([229, 202, 94], max=255, alpha_index=0)},
    {'name': 'dem', 'color': rgba_to_int10([223, 176, 89], max=255, alpha_index=0)},
    {'name': 'efx', 'color': rgba_to_int10([255, 254, 105], max=255, alpha_index=0)},
    {'name': 'cfx', 'color': rgba_to_int10([253, 254, 152], max=255, alpha_index=0)},
    {'name': 'tex', 'color': rgba_to_int10([230, 190, 222], max=255, alpha_index=0)},
    {'name': 'cpt', 'color': rgba_to_int10([100, 100, 100], max=255, alpha_index=0)},
    {'name': 'mod', 'color': rgba_to_int10([119, 77, 198], max=255, alpha_index=0)},
]


