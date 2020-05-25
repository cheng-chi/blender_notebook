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
        click.echo("Kernel path {} does not exist!".format(kernel_path))
        if click.confirm("Are you sure to create?"):
            kernel_path.mkdir(parents=True, exist_ok=True)
        else:
            raise RuntimeError("Abort!")
    return kernel_path


@click.group()
def cli():
    """
    Command line tool to wrap blender 2.8+ as a jupyter kernel
    """
    pass


@cli.command()
@click.option('--blender-exec', required=True, type=str, help="Path the blender executable")
@click.option('--kernel-dir', default=None, type=str, help="Path to jupyter's kernels directory")
@click.option('--kernel-name', default='blender', type=str, help="Name of the kernel to be installed")
def install(blender_exec, kernel_dir, kernel_name):
    """
    Install kernel to jupyter notebook
    """
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

    # find python path
    python_path = list()
    for path in sys.path:
        if pathlib.Path(path).is_dir():
            python_path.append(str(path))

    # dump jsons
    kernel_dict = {
        "argv": [
            sys.executable,
            str(kernel_launcher_py_dst), 
            "-f", 
            r"{connection_file}"],
        "display_name": kernel_name,
        "language": "python"
    }
    blender_config_dict = {
        "blender_executable": str(blender_exec),
        "python_path": python_path,
    }
    kernel_json_dst = kernel_install_path.joinpath('kernel.json')
    blender_config_json_dst = kernel_install_path.joinpath('blender_config.json')

    with kernel_json_dst.open('w') as f:
        json.dump(kernel_dict, f, indent=2)
    with blender_config_json_dst.open('w') as f:
        json.dump(blender_config_dict, f, indent=2)


@cli.command()
@click.option('--kernel-dir', default=None, type=str, help="Path to jupyter's kernels directory")
@click.option('--kernel-name', default='blender', type=str, help="Name of the kernel to be removed")
def remove(kernel_dir, kernel_name):
    """
    Remove the kernel
    """
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
