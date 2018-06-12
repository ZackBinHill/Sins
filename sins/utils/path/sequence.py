# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 5/2/2018

import os
import re
import time


seq_patern = re.compile(r'(?P<prefix>^.+[._])(?P<frame>#+|%\d*d|\$F\d*)(?P<suffix>[._].+$)')
seq_patern_with_digit = re.compile(r'(?P<prefix>^.+[._])(?P<frame>#+|%\d*d|\$F\d*|\d+)(?P<suffix>[._].+$)')


def is_sequence(path):
    result = seq_patern.match(os.path.basename(path))
    if result:
        return True
    return False


def get_sequences(path, only_sequence=False):
    """
    return sequence info from given folder or sequence
    :param str path: e.g: '/folder' or '../sequence.####.exr'(# or d%)
    :param bool only_sequence: return only sequence files or all files
    :return: a list of seq dict::
        'filename': '../sequence.####.exr',
        'files': ['../sequence.0001.exr', '../sequence.0002.exr', ...],
        'first_frame': '0001',
        'last_frame': '0003',
        'frame_length': 3,
        'frames': ['0001', '0002', ...],
        'non_digit_part': '../sequence..exr',
        'is_sequence': True
    """

    IMAGES = ["tif", "tiff", "jpg", "jpeg", "bmp", "png",
              "exr", "dpx", "rat", "tga", "hdr", "pic", "vdb", "bgeo", "bgeo.sc"]

    def get_sequence_groups(_files=[], only_sequence=True):
        """
        find files with seq numbers in filename from given files
        e.g: '../sequence.0001.exr'
        :param _files: file list to find files with seq number
        :param bool only_sequence: only return seq files
        :return: a list with dict format::
            'files':
            'filename':
            'frames':
            'seq_len':
            'non_digit_part':
            'has_padding':
        """
        reg = re.compile(r'(?P<base>^.+[._])(?P<frame_num>\d+)(?P<ext>[._].+$)')
        _files.sort()
        seq_groups = []

        for _f in _files:
            _basename = os.path.basename(_f)
            _ext = _basename.split('.')[-1].lower()
            _dirname = os.path.dirname(_f)
            _result = reg.search(_basename)
            if not _result or _ext not in IMAGES:
                if not only_sequence:
                    grp_data = {
                        'filename':_f,
                        'is_sequence':False,
                        'non_digit_part':_f,
                        'frame_length':0,
                        'first_frame':0,
                        'last_frame':0,
                        'frames':[],
                        'files':[_f],
                        'has_padding':False
                    }
                    seq_groups.append(grp_data)
                    continue
                else:
                    continue

            base = _result.group('base')
            ext = _result.group('ext')
            frame_num = _result.group('frame_num')
            frame_length = len(frame_num)
            non_digit_part = os.path.join(_dirname, base + ext).replace("\\", "/")

            find_seq_grp = False
            for seq_group in seq_groups:
                if non_digit_part == seq_group['non_digit_part']:
                    if frame_length != seq_group['frame_length']:
                        seq_group['has_padding'] = False

                    seq_group['files'].append(_f)
                    seq_group['frame_length'] = frame_length
                    seq_group['frames'].append(frame_num)
                    find_seq_grp = True

            if not find_seq_grp:
                grp_data = {
                    'filename': os.path.join(_dirname, base + '#' * frame_length + ext).replace("\\", "/"),
                    'is_sequence': True,
                    'non_digit_part': non_digit_part,
                    'frame_length': frame_length,
                    'frames': [frame_num],
                    'files': [_f],
                    'has_padding': True
                }
                seq_groups.append(grp_data)

        for grp in seq_groups:
            if not grp.get('frames', 0):
                continue

            grp['first_frame'] = min(grp['frames'], key=int)
            grp['last_frame'] = max(grp['frames'], key=int)

        for seq in seq_groups:
            if 'files' in seq and len(seq['files']) == 1:
                seq['is_sequence'] = False

        return seq_groups

    files = []
    if isinstance(path, list):
        return get_sequence_groups(path, only_sequence)

    elif os.path.isdir(path):
        for f in os.listdir(path):
            f = os.path.join(path, f).replace("\\", "/")

            if os.path.isfile(f):
                files.append(f)

        return get_sequence_groups(files, only_sequence)

    basename = os.path.basename(path)
    dirname = os.path.dirname(path)
    result = seq_patern_with_digit.match(basename)
    if result:
        matched_files = []
        pattern = '({prefix})(\d+)({suffix})'.format(prefix=result.group('prefix'), suffix=result.group('suffix'))
        pattern = re.compile(pattern)
        for f in os.listdir(dirname):
            if re.match(pattern, f):
                matched_files.append(os.path.join(dirname, f).replace("\\", "/"))
        matched_files.sort()
        return get_sequence_groups(matched_files, only_sequence)
    else:
        return get_sequence_groups([path], only_sequence)