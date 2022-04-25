# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENCE BLOCK #####
#
# Shadertoy Viewer Addon for Blender
#
# Copyright (C) 2022 Toshimitsu Kimura <lovesyao@gmail.com>

import bpy
import gpu
from gpu_extras.batch import batch_for_shader

bl_info = {
    "name": "Shadertoy Viewer",
    "author": "Toshimitsu Kimura",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "File > New > Shadertoy / Add Workspace > Shadertoy > Shadertoy",
    "description": "Shadertoy Viewer addon for Blender",
    "warning": "",
    "support": "COMMUNITY",
    "doc_url": "",
    "tracker_url": "",
    "category": "System"
}

# Shadertoy workspace:
# hide headers in viewport
# hide tools in viewport
# hide overlays in viewport
# hide gizmos in viewport
# hide object type visibilities in viewport

from gpu.types import (
    GPUBatch,
    GPUIndexBuf,
    GPUVertBuf,
)

from bpy.props import (
    StringProperty,
#    IntProperty,
)

from urllib import request
import ssl
import json
# https://www.shadertoy.com/howto

import time
from math import modf

def shadertoy_inputmenu(self, context):
    layout = self.layout
    scene = context.scene
    layout.label(text="Shadertoy ID:")
    layout.prop(scene, "shadertoy_id", text="")
#    layout.prop(scene, "shadertoy_id", text="Shadertoy ID")

import re

def shadertoy_shader_update(self, context):
    scene = self
    shadertoy_id = scene.shadertoy_id
    if shadertoy_id == "":
        return
    shadertoy_id = re.sub("^.*shadertoy\\.com\\/[a-zA-Z0-9]+\\/([a-zA-Z0-9]+)", "\\1", shadertoy_id)

    req = request.Request('https://www.shadertoy.com/shadertoy')
    req.add_header('Referer', 'https://www.shadertoy.com/view/' + shadertoy_id)
    req.add_header('User-Agent', 'Mozilla/5.0')
    data = 's={ "shaders" : ["'+ shadertoy_id +'"] }&nt=1&nl=1&np=1'
    res = request.urlopen(req, data=data.encode(), context = ssl._create_unverified_context())\
                .read().decode('utf-8')
    db = json.loads(res)
    code = (((db[0]["renderpass"][0]["code"] if "code" in db[0]["renderpass"][0] else "") \
                                          if len(db[0]["renderpass"]) else "") \
                                          if "renderpass" in db[0] else "") \
                                          if len(db) else ""
    if code == "":
        print("ERROR: shadertoy_id: %s"%shadertoy_id)
        return

    txt = bpy.data.texts.new(shadertoy_id)
    txt.write(code)
    context.space_data.text = txt

#    code = """
#void mainImage(out vec4 fragColor, in vec2 fragCoord) {
#  fragColor = vec4(1.0, 0.0, 0.0, 1.0);
#}
#"""
    # https://www.shadertoy.com/view/XsjGDt -> ok
    # https://www.shadertoy.com/view/3sySRK -> ok
    # https://www.shadertoy.com/view/MdX3zr -> ok

    shader = gpu.types.GPUShader("""
in vec2 pos;
void main()
{
   gl_Position = vec4(pos, 0.0, 1.0);
}
""", """
out vec4 FragColor; // todo: compatible name

uniform vec3 iResolution;
uniform float iTime;
uniform float iTimeDelta;
uniform int iFrame;
uniform float iFrameRate;
//uniform float iChannelTime[4];
//uniform vec3 iChannelResolution[4];
uniform vec4 iMouse;
//uniform samplerXX iChannel0..3;
//uniform vec4 iDate;
//uniform float iSampleRate;
""" + code + """
void main(){
    vec4 _fragColor;
    mainImage(_fragColor, gl_FragCoord.xy);
    FragColor = vec4(_fragColor.xyz, 1.0);
}
""")
#    scene["code"] = code

    vertices = ((-1.0, -1.0), (1.0, -1.0), (-1.0,  1.0), (1.0,  1.0))
    indices = ((0, 1, 2), (2, 1, 3))

#    vbo_format = shader.format_calc()
#    vbo = GPUVertBuf(vbo_format, 4)
#    vbo.attr_fill("pos", vertices)
#    ibo = GPUIndexBuf(type="TRIS", seq=indices)
#    batch = GPUBatch(type="TRIS", buf=vbo, elem=ibo)
    batch = batch_for_shader(shader, 'TRIS', {"pos":vertices}, indices=indices)

    bpy.app.driver_namespace["shadertoy_shader_param"] = (shader, batch)

    scene.render.engine = "SHADERTOY_ENGINE"
    sc = context.screen
    for (area, space) in [(area, area.spaces[0]) for area in sc.areas if area.type == "VIEW_3D"]:
        space.shading.type = "RENDERED"
        space.overlay.show_overlays = False
        space.show_gizmo = False
        space.show_object_viewport_mesh = False
        space.show_object_viewport_curve = False
        space.show_object_viewport_surf = False
        space.show_object_viewport_meta = False
        space.show_object_viewport_font = False
        space.show_object_viewport_pointcloud = False
        space.show_object_viewport_volume = False
        space.show_object_viewport_grease_pencil = False
        space.show_object_viewport_armature = False
        space.show_object_viewport_lattice = False
        space.show_object_viewport_empty = False
        space.show_object_viewport_light = False
        space.show_object_viewport_light_probe = False
        space.show_object_viewport_camera = False
        space.show_object_viewport_speaker = False
        space.show_region_tool_header = False
        space.show_region_header = False
        space.show_region_ui = False

        override_context = context.copy()
        override_context['area'] = area
        override_context['region'] = area.regions[-1]
        override_context['space_data'] = space
        bpy.ops.wm.tool_set_by_id(override_context, name='shadertoy.shadertoy_tool')

        space.show_region_toolbar = False

    bpy.app.driver_namespace["shadertoy_clock"] = 0.0
    bpy.app.driver_namespace["shadertoy_framecount"] = 0
    bpy.app.driver_namespace["shadertoy_startclock"] = 0.0

class ShadertoyRenderEngine(bpy.types.RenderEngine):
    bl_idname = 'SHADERTOY_ENGINE'
    bl_label = 'Shadertoy Engine'

    bl_use_image_save = False

    # def update(self, data=None, depsgraph=None):
    #    pass

    # def render(self, depsgraph):
    #    pass

    # def render_frame_finish(self):
    #    pass

    # def draw(self, context, depsgraph):
    #    pass

    def view_update(self, context, depsgraph):
        pass

    def view_draw(self, context, depsgraph):
        scene = context.scene
        region = context.region
        screen = context.screen

        param = bpy.app.driver_namespace["shadertoy_shader_param"]
        if not param:
            return

        (shader, batch) = param
        gpu.state.blend_set('ALPHA_PREMULT')
        shader.bind()
        try:
            shader.uniform_float("iResolution", (region.width, region.height, 1.0)) # TODO: pixel aspect ratio
        except: pass
        try:
            shader.uniform_float("iTime", scene.frame_float/scene.render.fps)
        except: pass
        try:
            shader.uniform_float("iMouse", bpy.app.driver_namespace["shadertoy_mouse"])
        except: pass
        try:
            shader.uniform_int("iFrame", int(modf(scene.frame_float)[1]))
        except: pass


        t = time.perf_counter()
        tdelta = t - bpy.app.driver_namespace["shadertoy_clock"]
        if tdelta >= 1.0 or bpy.app.driver_namespace["shadertoy_framecount"] == 0:
            bpy.app.driver_namespace["shadertoy_framecount"] = 0
            bpy.app.driver_namespace["shadertoy_startclock"] = time.perf_counter()
        try:
            shader.uniform_float("iTimeDelta", tdelta)
        except: pass
        try:
            shader.uniform_float("iFrameRate", bpy.app.driver_namespace["shadertoy_framecount"] / \
                (t - bpy.app.driver_namespace["shadertoy_startclock"]))
        except: pass
        bpy.app.driver_namespace["shadertoy_clock"] = time.perf_counter()
        bpy.app.driver_namespace["shadertoy_framecount"] += 1

        # 描画
        batch.draw(shader)
        gpu.state.blend_set('NONE')


class ShadertoyModalOperator(bpy.types.Operator):
    bl_idname = "shadertoy.modal_operator"
    bl_label = "Shadertoy Modal Operator"

    def invoke(self, context, event):
        scene = context.scene
#        print("click");
        bpy.app.driver_namespace["shadertoy_mouse"][0] = \
        bpy.app.driver_namespace["shadertoy_mouse"][2] = event.mouse_region_x
        bpy.app.driver_namespace["shadertoy_mouse"][1] = \
        bpy.app.driver_namespace["shadertoy_mouse"][3] = event.mouse_region_y
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def execute(self, context):
        return {'FINISHED'}

    def modal(self, context, event):
#        print("modal");
        bpy.app.driver_namespace["shadertoy_mouse"][0] = event.mouse_region_x
        bpy.app.driver_namespace["shadertoy_mouse"][1] = event.mouse_region_y
        if bpy.app.driver_namespace["shadertoy_mouse"][3] > 0:
            bpy.app.driver_namespace["shadertoy_mouse"][3] = -bpy.app.driver_namespace["shadertoy_mouse"][3]
        if event.value == 'RELEASE':
            bpy.app.driver_namespace["shadertoy_mouse"][2] = \
                -bpy.app.driver_namespace["shadertoy_mouse"][2];
#            print("released");
            return {'FINISHED'}

        return {'RUNNING_MODAL'}


#import addon_utils
from pathlib import Path

def init_props():
    clear_props()
    scene = bpy.types.Scene
    scene.shadertoy_id = StringProperty(name="Shadertoy ID", 
                                          default="",
                                          update=shadertoy_shader_update)
    bpy.app.driver_namespace["shadertoy_inputmenu_handle"] = shadertoy_inputmenu
    bpy.types.TEXT_HT_header.append(shadertoy_inputmenu)
    if not Path(bpy.utils.script_path_user() + "/startup/bl_app_templates_user/Shadertoy/startup.blend").exists():
        #self.report({"WARNING"}, 
        print("The Shadertoy Viewer addon will not work correctly: the application template is not installed. You should ensure to install the template to {BLENDER_USER_SCRIPTS}/startup/bl_app_templates_user directory.")
        # TODO: error reporting in GUI
    bpy.app.driver_namespace["shadertoy_shader_param"] = None
    bpy.app.driver_namespace["shadertoy_mouse"] = [0, 0, 0, 0]
    bpy.app.driver_namespace["shadertoy_clock"] = 0.0
    bpy.app.driver_namespace["shadertoy_framecount"] = 0
    bpy.app.driver_namespace["shadertoy_startclock"] = 0.0
#    if not "Shadertoy" in bpy.data.workspaces:
#        for mod in addon_utils.modules():
#            if mod.bl_info['name'] == "Shadertoy Viewer":
#                filepath = mod.__file__.replace(".py", ".blend")
#                bpy.ops.wm.append(filename="Shadertoy", directory=filepath+"/WorkSpace/")                
                

def clear_props():
    scene = bpy.types.Scene
    if "shadertoy_inputmenu_handle" in bpy.app.driver_namespace:
        bpy.types.TEXT_HT_header.remove(bpy.app.driver_namespace["shadertoy_inputmenu_handle"])
        del bpy.app.driver_namespace["shadertoy_inputmenu_handle"]
    if hasattr(scene, "shadertoy_id"):
        del scene.shadertoy_id
    if "shadertoy_shader_param" in bpy.app.driver_namespace:
        del bpy.app.driver_namespace["shadertoy_shader_param"]
    if "shadertoy_mouse" in bpy.app.driver_namespace:
        del bpy.app.driver_namespace["shadertoy_mouse"]
    if "shadertoy_clock" in bpy.app.driver_namespace:
        del bpy.app.driver_namespace["shadertoy_clock"]
    if "shadertoy_framecount" in bpy.app.driver_namespace:
        del bpy.app.driver_namespace["shadertoy_framecount"]
    if "shadertoy_startclock" in bpy.app.driver_namespace:
        del bpy.app.driver_namespace["shadertoy_startclock"]

class ShadertoyTool(bpy.types.WorkSpaceTool):  
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'
    bl_idname = "shadertoy.shadertoy_tool"
    bl_label = " Shadertoy Tool"
    bl_description = ("Mouse and keyboard capture for Shadertoy shader evaluation")
    bl_icon =  "SHADERFX"          
    bl_widget = None
    bl_keymap = (
        ("shadertoy.modal_operator", {"type": 'LEFTMOUSE', "value": 'PRESS'}, {}),
    )

classes = [
    ShadertoyRenderEngine,
    ShadertoyModalOperator,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    init_props()
    bpy.utils.register_tool(ShadertoyTool, after=None, separator=True, group=False)

def unregister():
    clear_props()
    for c in classes:
        bpy.utils.unregister_class(c)
    bpy.utils.unregister_tool(ShadertoyTool)

if __name__ == "__main__":
    register()
