# -*- coding: utf-8 -*-
import os
import shlex
import subprocess
from bfx.util.cmds import get_firefox_cmd, get_file_explorer_cmd


def open_version_in_browser(version):
    import webbrowser
    webbrowser.open(version.url)


def open_version_in_file_explorer(version):
    path = version.default_burl.real_path

    if path and os.path.exists(path):
        cmd = '{0} {1}'.format(get_file_explorer_cmd(), path)
        try:
            subprocess.Popen(shlex.split(cmd))
        except:
            os.system(cmd)


