import click
import pathlib
import shutil
import subprocess
import os
import site
import json
import sys
import textwrap

def get_kernel_path(kernel_dir):
    kernel_path = None
    if kernel_dir:
        kernel_path = pathlib.Path(kernel_dir)
    else:
        result = subprocess.run(["jupyter", "--data-dir"], capture_output=True)
        data_dir = result.stdout.decode('utf8').strip()
        kernel_path = pathlib.Path(data_dir).joinpath('kernels')
    if not kernel_path.exists():
        raise RuntimeError("Kernel path {} does not exist!".format(kernel_path))
    return kernel_path


@click.group()
def cli():
    pass

@cli.command()
@click.option('--blender-exec', required=True, type=str)
@click.option('--kernel-dir', default=None, type=str)
def install(blender_exec, kernel_dir):
    # check version
    supported_py_version = (3, 7)
    current_py_version = (sys.version_info.major, sys.version_info.minor)
    if current_py_version != supported_py_version:
        message = """
        Current python interpreter version is not {}.{}!
        blender_notebook will link pip packages installed in this interpreter to the 
        blender embedded python interpreter. Mismatch in python version might cause
        problem launching the jupyter kernel. Are you sure to continue?
        """.format(*supported_py_version)
        if not click.confirm(textwrap.dedent(message)):
            return

    # check input
    blender_path = pathlib.Path(blender_exec)
    if not blender_path.exists():
        raise RuntimeError("Invalid blender executable path!")

    kernel_path = get_kernel_path(kernel_dir)
    print(kernel_path)

    kernel_name = "blender"
    kernel_install_path = kernel_path.joinpath(kernel_name)
    if kernel_install_path.exists():
        if not click.confirm('kernel "{}" already exitsts, do you want to overwrite?'.format(kernel_name)):
            return
        shutil.rmtree(kernel_install_path)
        
    # check files to copy
    kernel_py_path = pathlib.Path(__file__).parent.joinpath('kernel.py')
    kernel_launcher_py_path = pathlib.Path(__file__).parent.joinpath('kernel_launcher.py')
    assert(kernel_py_path.exists())
    assert(kernel_launcher_py_path.exists())

    # start dumping files
    click.echo("Saving files to {}".format(kernel_install_path))
    # create directory
    kernel_install_path.mkdir()

    # copy python files
    kernel_py_dst = kernel_install_path.joinpath(kernel_py_path.name)
    kernel_launcher_py_dst = kernel_install_path.joinpath(kernel_launcher_py_path.name)

    shutil.copyfile(kernel_py_path, kernel_py_dst)
    shutil.copyfile(kernel_launcher_py_path, kernel_launcher_py_dst)
    kernel_launcher_py_dst.chmod(0o755)

    # dump jsons
    kernel_dict = {
        "argv": [str(kernel_launcher_py_dst), "-f", r"{connection_file}"],
        "display_name": kernel_name,
        "language": "python"
    }
    blender_config_dict = {
        "blender_executable": str(blender_exec),
        "python_path": [str(x) for x in site.getsitepackages()],
    }
    kernel_json_dst = kernel_install_path.joinpath('kernel.json')
    blender_config_json_dst = kernel_install_path.joinpath('blender_config.json')

    with kernel_json_dst.open('w') as f:
        json.dump(kernel_dict, f, indent=2)
    with blender_config_json_dst.open('w') as f:
        json.dump(blender_config_dict, f, indent=2)


@cli.command()
@click.option('--kernel-dir', default=None, type=str)
def remove(kernel_dir):
    kernel_name = "blender"
    kernel_path = get_kernel_path(kernel_dir)
    kernel_install_path = kernel_path.joinpath(kernel_name)
    if not kernel_install_path.exists():
        return

    if not click.confirm('Are you sure to delete {} ?'.format(kernel_install_path)):
        return

    shutil.rmtree(kernel_install_path)
    click.echo("blender jupyter kernel is removed!")

def main():
    cli()

if __name__ == '__main__':
    main()
