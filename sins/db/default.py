# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/14/2018
from sins.utils.color import rgba_to_int10


Department = [
    {'name': 'CMP', 'full_name': 'compositing', 'description': 'Compositing is the combining of visual elements from separate sources into single images, often to create the illusion that all those elements are parts of the same scene. Live-action shooting for compositing is variously called "chroma key", "blue screen", "green screen" and other names. Today, most, though not all, compositing is achieved through digital image manipulation', 'color': rgba_to_int10([87, 212, 113], alpha_index=0)},
    {'name': 'LGT', 'full_name': 'lighting', 'description': 'Lighting or illumination is the deliberate use of light to achieve a practical or aesthetic effect.', 'color': rgba_to_int10([87, 212, 113], alpha_index=0)},
    {'name': 'MOD', 'full_name': 'model', 'description': 'In 3D computer graphics, 3D modeling (or three-dimensional modeling) is the process of developing a mathematical representation of any surface of an object (either inanimate or living) in three dimensions via specialized software. ', 'color': rgba_to_int10([87, 212, 113], alpha_index=0)},
    {'name': 'TEX', 'full_name': 'texture', 'description': '', 'color': rgba_to_int10([87, 212, 113], alpha_index=0)},
    {'name': 'MTP', 'full_name': 'matte painting', 'description': '', 'color': rgba_to_int10([87, 212, 113], alpha_index=0)},
    {'name': 'RIG', 'full_name': 'rigging', 'description': '', 'color': rgba_to_int10([87, 212, 113], alpha_index=0)},
    {'name': 'ANI', 'full_name': 'animation', 'description': 'Computer animation is the art of creating moving images via the use of computers. It is a subfield of computer graphics and animation.', 'color': rgba_to_int10([87, 212, 113], alpha_index=0)},
    {'name': 'EFX', 'full_name': 'effects', 'description': '', 'color': rgba_to_int10([87, 212, 113], alpha_index=0)},
    {'name': 'PRV', 'full_name': 'preview', 'description': '', 'color': rgba_to_int10([87, 212, 113], alpha_index=0)},
    {'name': 'ROT', 'full_name': 'roto paint', 'description': '', 'color': rgba_to_int10([87, 212, 113], alpha_index=0)},
    {'name': 'EDI', 'full_name': 'editing', 'description': '', 'color': rgba_to_int10([87, 212, 113], alpha_index=0)},
]


PermissionGroup = [
    {'name': 'Artist'},
    {'name': 'Manager'},
    {'name': 'Supervisor'},
    {'name': 'Coordinator'},
    {'name': 'Read-only'},
    {'name': 'Root'},
]


Status = [
    {'name': 'wts', 'full_name': 'wait to start', 'color': None, 'icon': '', 'referred_table': 'Project;Shot;Sequence;Asset;Task'},
    {'name': 'wip', 'full_name': 'work in progress', 'color': None, 'icon': '', 'referred_table': 'Project;Shot;Sequence;Asset;Task;Version'},
    {'name': 'fin', 'full_name': 'final', 'color': None, 'icon': '', 'referred_table': 'Project;Shot;Sequence;Asset;Task'},
    {'name': 'hld', 'full_name': 'hold', 'color': None, 'icon': '', 'referred_table': 'Project;Shot;Sequence;Asset'},
    {'name': 'cld', 'full_name': 'cancelled', 'color': None, 'icon': '', 'referred_table': 'Project;Shot;Sequence;Asset'},
    {'name': 'smtr', 'full_name': 'submit to review', 'color': None, 'icon': '', 'referred_table': 'Version'},
    {'name': 'smts', 'full_name': 'submit to supervisor', 'color': None, 'icon': '', 'referred_table': 'Version'},
    {'name': 'smtc', 'full_name': 'submit to client', 'color': None, 'icon': '', 'referred_table': 'Version'},
    {'name': 'aprl', 'full_name': 'approve by lead', 'color': None, 'icon': '', 'referred_table': 'Version'},
    {'name': 'aprs', 'full_name': 'approve by supervisor', 'color': None, 'icon': '', 'referred_table': 'Version'},
    {'name': 'aprc', 'full_name': 'approve by client', 'color': None, 'icon': '', 'referred_table': 'Version'},
]


PipelineStep = [
    {'name': 'cmp', 'color': rgba_to_int10([87, 212, 113], alpha_index=0)},
    {'name': 'lay', 'color': rgba_to_int10([229, 211, 204], alpha_index=0)},
    {'name': 'lgt', 'color': rgba_to_int10([202, 237, 111], alpha_index=0)},
    {'name': 'rig', 'color': rgba_to_int10([229, 201, 209], alpha_index=0)},
    {'name': 'pnt', 'color': rgba_to_int10([114, 73, 47], alpha_index=0)},
    {'name': 'rto', 'color': rgba_to_int10([107, 88, 52], alpha_index=0)},
    {'name': 'pla', 'color': rgba_to_int10([119, 238, 254], alpha_index=0)},
    {'name': 'ani', 'color': rgba_to_int10([229, 202, 94], alpha_index=0)},
    {'name': 'dem', 'color': rgba_to_int10([223, 176, 89], alpha_index=0)},
    {'name': 'efx', 'color': rgba_to_int10([255, 254, 105], alpha_index=0)},
    {'name': 'cfx', 'color': rgba_to_int10([253, 254, 152], alpha_index=0)},
    {'name': 'tex', 'color': rgba_to_int10([230, 190, 222], alpha_index=0)},
    {'name': 'cpt', 'color': rgba_to_int10([100, 100, 100], alpha_index=0)},
    {'name': 'mod', 'color': rgba_to_int10([119, 77, 198], alpha_index=0)},
]


