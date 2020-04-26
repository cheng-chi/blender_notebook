#!/usr/bin/env python3
import pathlib
import json
import collections
import sys
import subprocess
import tempfile
import shutil

def get_blender_config():
    this_file_path = pathlib.Path(__file__)
    json_path = this_file_path.parent.joinpath('blender_config.json')
    config_dict = None
    with json_path.open('r') as f:
        config_dict = json.load(f)
    
    print(config_dict)
    # check config
    assert(pathlib.Path(config_dict['blender_executable']).exists())
    for path in config_dict['python_path']:
        assert(pathlib.Path(path).exists())
    return config_dict


def main():
    blender_config = get_blender_config()
    blender_config['args'] = sys.argv[1:]
    print(blender_config)

    kernel_path = pathlib.Path(__file__).parent.joinpath('kernel.py')
    assert(kernel_path.exists())

    with tempfile.TemporaryDirectory() as tempdirname:
        tempdir = pathlib.Path(tempdirname)
        runtime_config_path = tempdir.joinpath('runtime_config.json')
        with runtime_config_path.open('w') as f:
            json.dump(blender_config, f)

        runtime_kernel_path = tempdir.joinpath('kernel.py')
        shutil.copyfile(kernel_path, runtime_kernel_path)

        blender_executable = blender_config['blender_executable']
        print(tempdirname)
        subprocess.run([blender_executable, "-P", str(runtime_kernel_path)])
        

main()
