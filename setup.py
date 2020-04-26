from setuptools import setup

setup(
    name = "blender_notebook",
    version = "0.0.1",
    description = "Script to wrap blender as a jupyter kernel",
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
        'ipykernel'
    ],
    python_requires = '>=3.6',
    entry_points = {
        'console_scripts': [
            'blender_notebook = blender_notebook.installer:main',
        ]
    }
)