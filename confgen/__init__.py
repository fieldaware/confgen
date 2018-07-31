import os
import shutil

__version__ = '0.7.0'

def dir_rm(path):
    # remove all files to avoid stale configs (they will re-generated)
    try:
        for root, dirs, files in os.walk(path):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
    except OSError as e:
        if e.errno == 2:  # build dir not found, it is fine, ignore
            pass
        else:
            raise
