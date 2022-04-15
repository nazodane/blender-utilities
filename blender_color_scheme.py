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
# Color Scheme Addon for Blender
#
# Copyright (C) 2022 Toshimitsu Kimura <lovesyao@gmail.com>
# Copyright (C) 2005 Jonathon Jongsma
#
# Note: The code is based on Agave 0.4.7
# https://web.archive.org/web/20170327063642/http://home.gna.org/colorscheme/
# There are some incompatibilities between Agave and this addon.
# I don't check yet but it may comes from gamma correction.

import bpy
import random
from bpy.props import (
    IntProperty,
    FloatVectorProperty,
    EnumProperty,
    CollectionProperty,
)
from colorsys import hsv_to_rgb

# TODO: palette?

bl_info = {
    "name": "Color Scheme",
    "author": "Toshimitsu Kimura",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "3D Viewport > Sidebar",
    "description": "Color Scheme addon for Blender",
    "warning": "",
    "support": "COMMUNITY",
    "doc_url": "",
    "tracker_url": "",
    "category": "System"
}

class COLORSCHEME_OT_ColorRandomize(bpy.types.Operator):
    bl_idname = "colorscheme.colorrandomize"
    bl_label = "Color Randomize"
    bl_description = "Color Randomize"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene.colorscheme_base = [random.random() for i in range(3)];
        return {'FINISHED'}
    

maxHueValue = 1.0
maxSvValue = 1.0
# from gcs-mainwindow-actions.cc
class COLORSCHEME_OT_ColorLighten(bpy.types.Operator):
    bl_idname = "colorscheme.colorlighten"
    bl_label = "Increase the brightness"
    bl_description = "Get lighten color schemes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene.colorscheme_base = hsv_to_rgb(scene.colorscheme_base.h,
                                                scene.colorscheme_base.s,
                                                scene.colorscheme_base.v + 0.05 * maxSvValue)
        return {'FINISHED'}

class COLORSCHEME_OT_ColorDarken(bpy.types.Operator):
    bl_idname = "colorscheme.colordarken"
    bl_label = "Decrease the brightness"
    bl_description = "Get darken color schemes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene.colorscheme_base = hsv_to_rgb(scene.colorscheme_base.h,
                                                scene.colorscheme_base.s,
                                                scene.colorscheme_base.v - 0.05 * maxSvValue)
        return {'FINISHED'}


class COLORSCHEME_OT_ColorSaturate(bpy.types.Operator):
    bl_idname = "colorscheme.colorsaturate"
    bl_label = "Increase the saturation"
    bl_description = "Get lighten color schemes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene.colorscheme_base = hsv_to_rgb(scene.colorscheme_base.h,
                                                scene.colorscheme_base.s + 0.05 * maxSvValue,
                                                scene.colorscheme_base.v)
        return {'FINISHED'}

class COLORSCHEME_OT_ColorDesaturate(bpy.types.Operator):
    bl_idname = "colorscheme.colordesaturate"
    bl_label = "Decrease the saturation"
    bl_description = "Get darken color schemes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene.colorscheme_base = hsv_to_rgb(scene.colorscheme_base.h,
                                                scene.colorscheme_base.s - 0.05 * maxSvValue,
                                                scene.colorscheme_base.v)
        return {'FINISHED'}


class COLORSCHEME_PropertiesGroup(bpy.types.PropertyGroup):
    length: IntProperty(name="Color Length",
                        default=0)
    color1: FloatVectorProperty(name="Color 1", 
                                subtype='COLOR', 
                                get=lambda t: t["color1"],
                                set=lambda t, v: None)
    color2: FloatVectorProperty(name="Color 2", 
                                subtype='COLOR', 
                                get=lambda t: t["color2"],
                                set=lambda t, v: None)
    color3: FloatVectorProperty(name="Color 3", 
                                subtype='COLOR',
                                get=lambda t: t["color3"],
                                set=lambda t, v: None)
    color4: FloatVectorProperty(name="Color 4", 
                                subtype='COLOR',
                                get=lambda t: t["color4"],
                                set=lambda t, v: None)


def method_to_length(method):
    return 2 if method == 'COMPLEMENTS' else 4 if method == 'TETRADS' else 3

class COLORSCHEME_OT_ColorSchemeFavorite(bpy.types.Operator):
    bl_idname = "colorscheme.colorschemefavorite"
    bl_label = "Favorite colorscheme"
    bl_description = "Favorite colorscheme"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        cs = scene.colorscheme_favorites.add()
        cs.length = method_to_length(scene.colorscheme_method)
        cs["color1"] = scene.colorscheme_calculated1
        cs["color2"] = scene.colorscheme_calculated2
        cs["color3"] = scene.colorscheme_calculated3
        cs["color4"] = scene.colorscheme_calculated4
        return {'FINISHED'}

class COLORSCHEME_OT_ColorSchemeFavoriteRemove(bpy.types.Operator):
    bl_idname = "colorscheme.colorschemefavoriteremove"
    bl_label = "Remove the favorite colorscheme"
    bl_description = "Remove the favorite colorscheme"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        cs = scene.colorscheme_favorites.remove(scene.active_colorscheme_favorite_index)
        return {'FINISHED'}

class COLORSCHEME_UL_ColorsList(bpy.types.UIList):
    use_filter_show: False
    def draw_item(self, context, layout, data, item, icon, active_data):
#        self.use_filter_invert = False

        col = layout.column()
        row = col.row(align=True)
        row.label(text="", icon="SOLO_ON")
        for i in range(item.length):
            row.prop(item, "color%s"%(i+1), text="")

    def draw_filter(self, context, layout): # hide useless filter menus
        row = layout.row()

class COLORSCHEME_PT_CustomPanel(bpy.types.Panel):

    bl_label = "Color Schemes"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Color Schemes"
    bl_context = ""

    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='PLUGIN')

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Base Color:")
        row = layout.row(align=True)
        row.prop(scene, "colorscheme_base", text="")
        row.operator(COLORSCHEME_OT_ColorLighten.bl_idname, text="", icon="SORT_DESC")
        row.operator(COLORSCHEME_OT_ColorDarken.bl_idname, text="", icon="SORT_ASC")
        row.operator(COLORSCHEME_OT_ColorSaturate.bl_idname, text="", icon="EXPORT")
        row.operator(COLORSCHEME_OT_ColorDesaturate.bl_idname, text="", icon="IMPORT")
        row.operator(COLORSCHEME_OT_ColorRandomize.bl_idname, text="", icon="FILE_REFRESH")

        layout.prop(scene, "colorscheme_method", text="")

        layout.label(text="Calculated:")
        row = layout.row(align=True)
        for i in range(method_to_length(scene.colorscheme_method)):
            row.prop(scene, "colorscheme_calculated%s"%(i+1), text="")
        row.operator(COLORSCHEME_OT_ColorSchemeFavorite.bl_idname, text="", icon="SOLO_ON")

        row = layout.row(align=True)
        row.label(text="Favorites:")
        row.operator(COLORSCHEME_OT_ColorSchemeFavoriteRemove.bl_idname, text="", icon="PANEL_CLOSE")
#        layout.prop(scene, "colorscheme_favorites", text="")
        layout.template_list("COLORSCHEME_UL_ColorsList", "", scene, "colorscheme_favorites", scene, "active_colorscheme_favorite_index")

# from gcs-color.cc
redLuminance = 0.2126
greenLuminance = 0.7152
blueLuminance = 0.0722
def luminance(color):
    return color[0] * redLuminance + color[1] * greenLuminance + color[2] * blueLuminance

from math import modf

# from gcs-scheme.cc
def colorscheme_update(self, context):
    if self.colorscheme_method == "COMPLEMENTS":
        self["colorscheme_calculated1"] = self.colorscheme_base
#        self.colorscheme_calculated2 = self.colorscheme_base
#        self.colorscheme_calculated2.h += maxHueValue/2
        self["colorscheme_calculated2"] = hsv_to_rgb(self.colorscheme_base.h + maxHueValue/2,
                                                self.colorscheme_base.s,
                                                self.colorscheme_base.v)
    elif self.colorscheme_method == "SPLIT_COMPLEMENTS":
        offset = maxHueValue / 15
        self["colorscheme_calculated1"] = self.colorscheme_base
        self["colorscheme_calculated2"] = hsv_to_rgb(self.colorscheme_base.h + maxHueValue/2 - offset,
                                                self.colorscheme_base.s,
                                                self.colorscheme_base.v)
        self["colorscheme_calculated3"] = hsv_to_rgb(self.colorscheme_base.h + maxHueValue/2 + offset,
                                                self.colorscheme_base.s,
                                                self.colorscheme_base.v)
    elif self.colorscheme_method == "TRIADS":
        offset = maxHueValue / 3
        self["colorscheme_calculated1"] = self.colorscheme_base
        self["colorscheme_calculated2"] = hsv_to_rgb(self.colorscheme_base.h + offset,
                                                self.colorscheme_base.s,
                                                self.colorscheme_base.v)
        self["colorscheme_calculated3"] = hsv_to_rgb(self.colorscheme_base.h - offset,
                                                self.colorscheme_base.s,
                                                self.colorscheme_base.v)
    elif self.colorscheme_method == "TETRADS":
        offset = maxHueValue / 4
        self["colorscheme_calculated1"] = self.colorscheme_base
        self["colorscheme_calculated2"] = hsv_to_rgb(self.colorscheme_base.h + offset,
                                                self.colorscheme_base.s,
                                                self.colorscheme_base.v)
        self["colorscheme_calculated3"] = hsv_to_rgb(self.colorscheme_base.h + maxHueValue / 2,
                                                self.colorscheme_base.s,
                                                self.colorscheme_base.v)
        self["colorscheme_calculated4"] = hsv_to_rgb(self.colorscheme_base.h + maxHueValue / 2 + offset,
                                                self.colorscheme_base.s,
                                                self.colorscheme_base.v)
    elif self.colorscheme_method == "ANALOGOUS":
        offset = maxHueValue / 12
        self["colorscheme_calculated1"] = hsv_to_rgb(self.colorscheme_base.h - offset,
                                                self.colorscheme_base.s,
                                                self.colorscheme_base.v)
        self["colorscheme_calculated2"] = self.colorscheme_base
        self["colorscheme_calculated3"] = hsv_to_rgb(self.colorscheme_base.h + offset,
                                                self.colorscheme_base.s,
                                                self.colorscheme_base.v)
    elif self.colorscheme_method == "MONOCHROMATIC":
        tmp = [self.colorscheme_base]
        if self.colorscheme_base.s < maxSvValue / 10:
            tmp.append(hsv_to_rgb(self.colorscheme_base.h,
                                modf(self.colorscheme_base.s + maxSvValue / 3)[0],
                                self.colorscheme_base.v))
            tmp.append(hsv_to_rgb(self.colorscheme_base.h,
                                modf(self.colorscheme_base.s + 2 * maxSvValue / 3)[0],
                                self.colorscheme_base.v))
        else:

            tmp.append(hsv_to_rgb(self.colorscheme_base.h,
                                self.colorscheme_base.s,
                                modf(self.colorscheme_base.v + maxSvValue / 3)[0]))
            tmp.append(hsv_to_rgb(self.colorscheme_base.h,
                                        self.colorscheme_base.s,
                                        modf(self.colorscheme_base.v + 2 * maxSvValue / 3)[0]))

        tmp = sorted(tmp, key=lambda t: luminance(t))
        self["colorscheme_calculated1"] = tmp[0]
        self["colorscheme_calculated2"] = tmp[1]
        self["colorscheme_calculated3"] = tmp[2]

def init_props():
    scene = bpy.types.Scene

    scene.colorscheme_base = FloatVectorProperty(name="Color Scheme Base", 
                                                subtype='COLOR', 
                                                default=[0.0,0.0,0.0],
                                                update=colorscheme_update)

    scene.colorscheme_method = EnumProperty(
        name="Color Scheme Method",
        description="Generating method for color scheme",
        items=[
            ('COMPLEMENTS', "Complements", "Complements"),
            ('SPLIT_COMPLEMENTS', "Split Complements", "Split Complements"),
            ('TRIADS', "Triads", "Triads"),
            ('TETRADS', "Tetrads", "Tetrads"),
            ('ANALOGOUS', "Analogous", "Analogous"),
            ('MONOCHROMATIC', "Monochromatic", "Monochromatic")
        ],
        default='COMPLEMENTS',
        update=colorscheme_update
    )



    scene.colorscheme_calculated1 = FloatVectorProperty(name="Color Scheme Calculated 1", 
                                                subtype='COLOR', 
                                                get=lambda t: t["colorscheme_calculated1"],
                                                set=lambda t, v: None)

    scene.colorscheme_calculated2 = FloatVectorProperty(name="Color Scheme Calculated 2", 
                                                subtype='COLOR',
                                                get=lambda t: t["colorscheme_calculated2"],
                                                set=lambda t, v: None)

    scene.colorscheme_calculated3 = FloatVectorProperty(name="Color Scheme Calculated 3", 
                                                subtype='COLOR', 
                                                get=lambda t: t["colorscheme_calculated3"],
                                                set=lambda t, v: None)

    scene.colorscheme_calculated4 = FloatVectorProperty(name="Color Scheme Calculated 4", 
                                                subtype='COLOR', 
                                                get=lambda t: t["colorscheme_calculated4"],
                                                set=lambda t, v: None)

    scene.colorscheme_favorites = CollectionProperty(type=COLORSCHEME_PropertiesGroup)
    scene.active_colorscheme_favorite_index = IntProperty(name="Active favorite color scheme index")

def clear_props():
    scene = bpy.types.Scene
    del scene.colorscheme_base
    del scene.colorscheme_method
    del scene.colorscheme_calculated1
    del scene.colorscheme_calculated2
    del scene.colorscheme_calculated3
    del scene.colorscheme_calculated4
    del scene.colorscheme_favorites
    del scene.active_colorscheme_favorite_index

classes = [
    COLORSCHEME_OT_ColorRandomize,
    COLORSCHEME_OT_ColorLighten,
    COLORSCHEME_OT_ColorDarken,
    COLORSCHEME_OT_ColorSaturate,
    COLORSCHEME_OT_ColorDesaturate,
    COLORSCHEME_OT_ColorSchemeFavorite,
    COLORSCHEME_OT_ColorSchemeFavoriteRemove,
    COLORSCHEME_PT_CustomPanel,
    COLORSCHEME_PropertiesGroup,
    COLORSCHEME_UL_ColorsList,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    init_props()


def unregister():
    clear_props()
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
