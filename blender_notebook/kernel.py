"""
Inspired by https://github.com/cameronfr/BlenderKernel
"""

import pathlib
import json

def get_runtime_config():
    this_file_path = pathlib.Path(__file__)
    json_path = this_file_path.parent.joinpath('runtime_config.json')
    config_dict = None
    with json_path.open('r') as f:
        config_dict = json.load(f)
    
    print(config_dict)
    # check config
    assert('args' in config_dict)
    for path in config_dict['python_path']:
        assert(pathlib.Path(path).exists())
    return config_dict

RUNTIME_CONFIG = get_runtime_config()
print(RUNTIME_CONFIG)

import asyncio
import sys
# Must append system python path with ipykernel etc.
sys.path.extend(RUNTIME_CONFIG['python_path'])
import bpy
from ipykernel.kernelapp import IPKernelApp
from bpy.app.handlers import persistent

class JupyterKernelLoop(bpy.types.Operator):
    bl_idname = "asyncio.jupyter_kernel_loop"
    bl_label = "Jupyter Kernel Loop"

    _timer = None

    kernelApp = None

    def modal(self, context, event):

        if event.type == 'TIMER':
            loop = asyncio.get_event_loop()
            loop.call_soon(loop.stop)
            loop.run_forever()

        return {'PASS_THROUGH'}

    def execute(self, context):

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.016, window=context.window)
        wm.modal_handler_add(self)

        if not JupyterKernelLoop.kernelApp:
            JupyterKernelLoop.kernelApp = IPKernelApp.instance()
            JupyterKernelLoop.kernelApp.initialize(['python'] + RUNTIME_CONFIG['args'])
            JupyterKernelLoop.kernelApp.kernel.start() # doesn't start event loop, kernelApp.start() does

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

class TmpTimer(bpy.types.Operator):
    bl_idname = "asyncio.tmp_timer"
    bl_label = "TMP Timer"

    _timer = None

    def modal(self, context, event):

        if event.type == 'TIMER':
            bpy.ops.asyncio.jupyter_kernel_loop()
            self.cancel(context)

        return {'FINISHED'}

    def execute(self, context):

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.016, window=context.window)
        wm.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

bpy.utils.register_class(JupyterKernelLoop)
bpy.utils.register_class(TmpTimer)

# start Kernel and asyncio on initial load
bpy.ops.asyncio.tmp_timer()

# start asyncio on any successive loads
@persistent
def loadHandler(dummy):
    bpy.ops.asyncio.jupyter_kernel_loop()
    # If call tmp_timer here instead, kernel doesn't work on successive files if have used kernel in current file.
bpy.app.handlers.load_post.append(loadHandler)

# Need the timer hack because if immediately call registered operation, get
# self.user_global_ns is None error in IPython/core/interactiveshell.py
# The bpy.app.timers causes a segfault when used with jupyter_kernel_loop()