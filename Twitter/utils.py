import os
import shutil

# create nested directories based on list of path's
def create_directories(*args):
    """
    # Create directories \ nested directories if not exists

    :param *args: path of directory
    """
    try:
        for folder in args:
            # create directories if not exists
            if not os.path.exists(str(folder)):
                print('creating folder: ' + str(folder))
                os.makedirs(str(folder))
            else:
                print(str(folder), ' path is already exists ')
    except OSError as exc:
        print('failed to create folder: ' + str(folder), exc_info=True)
        pass

def copy_files(source_file_path, target_file_path):
    """
    # Create directories \ nested directories if not exists

    :param source: path of file to copy from
    :param target: path of file target
    """
    try:
        shutil.copy(source_file_path, target_file_path)
        print(f'copy file {source_file_path} to {target_file_path}')
    except IOError as e:
        print("Unable to copy file. %s" % e)
    except:
        print("Unexpected error:", sys.exc_info())




