import shutil

__version__ = '0.5.4'

def dir_rm(path):
    # remove all files to avoid stale configs (they will re-generated)
    try:
        shutil.rmtree(path)
    except OSError as e:
        if e.errno == 2:  # build dir not found, it is fine, ignore
            pass
        else:
            raise
