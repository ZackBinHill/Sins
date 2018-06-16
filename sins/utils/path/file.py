import os
import time
from sins.utils.path.sequence import is_sequence, get_sequences
from sins.module import filetype
use_magic = False
try:
    import magic
    use_magic = True
except ImportError:
    pass

def get_dirs(folder):
    dirs = []
    for f in os.listdir(folder):
        absPath = os.path.join(folder, f).replace("\\", "/")
        if os.path.isdir(absPath):
            dirs.append(absPath)
    return dirs


def get_files(folder):
    files = []
    for f in os.listdir(folder):
        absPath = os.path.join(folder, f).replace("\\", "/")
        if os.path.isfile(absPath):
            files.append(absPath)
    return files


def get_path_mtime(f):
    try:
        absTime = os.path.getmtime(f)
        localTime = time.localtime(absTime)
        timeStr = time.strftime("%Y-%m-%d %H:%M:%S", localTime)
        return timeStr
    except:
        return "unknow"


def get_files_mtime(fileList):
    absTime = 0
    for file in fileList:
        if os.path.exists(file):
            try:
                if os.path.getmtime(file) > absTime:
                    absTime = os.path.getmtime(file)
            except:
                pass
    localTime = time.localtime(absTime)
    timeStr = time.strftime("%Y-%m-%d %H:%M:%S", localTime)
    return timeStr


def get_file_mime(f):
    if use_magic:
        return magic.from_file(f, mime=True)
    else:
        result = filetype.guess(f)
        if result is not None:
            return result.mime
        else:
            return ''


def get_file_size(f, get="str"):
    size = 0.0
    try:
        if get == "byte":
            return os.path.getsize(f)
        size = float(os.path.getsize(f) / 1024.0 / 1024.0)
        if get == "float":
            return size
    except:
        pass
    if size < 1.0:
        sizeStr = "%.3f kb" % (size * 1024.0)
    else:
        sizeStr = "%.3f mb" % size
    # print sizeStr
    if get == "str":
        return sizeStr


def get_files_size(files, get="str"):
    size = 0.0
    for f in files:
        size = size + get_file_size(f, get="float")
    if size < 1.0:
        sizeStr = "%.3f kb" % (size * 1024.0)
    else:
        sizeStr = "%.3f mb" % size
    if get == "str":
        return sizeStr
    if get == "float":
        return size


def get_detail_of_path(path):
    """
    :param path: file or folder or dict from func get_sequences
    :return: dict{
        "name":
        "type":
        "size":
        "modified date":
    }
    """
    if isinstance(path, dict):
        keys = path.keys()
        if "files" in keys and "filename" in keys and "is_sequence" in keys:
            files = path["files"]
            filename = path["filename"]
            isSequence = " sequence" if path["is_sequence"] else ""
            frameRange = "%s-%s" % (path["first_frame"], path["last_frame"]) if path["is_sequence"] else None
            name = os.path.basename(filename)
            type = os.path.splitext(filename)[1].split(".")[1]
            size = get_files_size(files)
            modifiedDate = get_files_mtime(files)
            return {
                "name": name,
                "type": type,
                "size": size,
                "modified date": modifiedDate,
                "file path": filename,
                "frame range": frameRange
            }
        else:
            return {
                "name": "unknow",
                "type": "unknow",
                "size": "unknow",
                "modified date": "unknow",
                "file path": "unknow"
            }
    else:
        if os.path.isdir(path):
            name = os.path.basename(path)
            modifiedDate = get_path_mtime(path)
            return {
                "name": name,
                "type": "folder",
                "size": "",
                "modified date": modifiedDate,
                "file path": path
            }
        elif is_sequence(path):
            data = get_sequences(path)[0]
            files = data["files"]
            filename = data["filename"]
            name = os.path.basename(filename)
            type = os.path.splitext(filename)[1].split(".")[1]
            size = get_files_size(files)
            modifiedDate = get_files_mtime(files)
            frameRange = "%s-%s" % (data["first_frame"], data["last_frame"]) if data["is_sequence"] else None
            return {
                "name": name,
                "type": "%s sequence" % type,
                "size": size,
                "modified date": modifiedDate,
                "file path": path,
                "frame range": frameRange
            }
        else:
            name = os.path.basename(path)
            type = os.path.splitext(path)[1].split(".")[-1]
            size = get_file_size(path)
            modifiedDate = get_path_mtime(path)
            return {
                "name": name,
                "type": type,
                "size": size,
                "modified date": modifiedDate,
                "file path": path
            }


if __name__ == "__main__":
    for i in get_sequences("F:/Temp/render_test"):
        print i
        print get_detail_of_path(i)

    # print get_dirs("F:/Temp/render_test")
    # print get_detail_of_path("F:/Temp/render_test")
    # print get_detail_of_path("F:/Temp/render_test/test.1.exr")
    # print get_detail_of_path("F:/Temp/render_test/test.#.exr")


