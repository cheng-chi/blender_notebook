from setuptools import setup
import pathlib
with pathlib.Path(__file__).parent.joinpath('README.md').open('r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = "blender_notebook",
    version = "0.0.3",
    description = "A simple command line tool to wrap blender 2.8+ as a jupyter kernel",
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    author = "Cheng Chi",
    author_email = "cheng-chi@outlook.com",
    license = "MIT",
    classifiers = [
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7'
    ],
    packages = ["blender_notebook"],
    zip_safe = True,
    install_requires = [
        'click',
        'ipykernel',
        'notebook'
    ],
    python_requires = '>=3.7',
    entry_points = {
        'console_scripts': [
            'blender_notebook = blender_notebook.installer:main',
            'blender-notebook = blender_notebook.installer:main'
        ]
    }
)