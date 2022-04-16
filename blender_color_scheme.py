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

translation_dict = {
    "en_US": {
    },
    "ja_JP": { # based on po/ja.po which was created by me!
        ("*", "Color Schemes"): "色スキーム",
        ("*", "Base Color:"): "ベース色:",

        ("*", "Random"): "ランダム",
        ("*", "Generate a random color"): "ランダムな色を生成します",

        ("*", "Lighten Scheme"): "明るいスキーム",
        ("*", "Darken Scheme"): "暗いスキーム",
        ("*", "Increase the brightness"): "明るさを増加します",
        ("*", "Decrease the brightness"): "明るさを減少します",
        ("*", "Saturate Scheme"): "濃いスキーム",
        ("*", "Desaturate Scheme"): "薄いスキーム",
        ("*", "Increase the saturation"): "彩度を増加します",
        ("*", "Decrease the saturation"): "彩度を減少します",

        ("*", "Color Scheme Method"): "色スキーム方式",
        ("*", "Complements"): "補色（対峙色）",
        ("*", "Split Complements"): "分裂補色",
        ("*", "Triads"): "三色配色",
        ("*", "Tetrads"): "四色配色",
        ("*", "Analogous"): "類似色",
        ("*", "Monochromatic"): "単色",

        ("*", "Calculated:"): "結果:",
        ("*", "Color Scheme Calculated 1"): "色スキーム結果 1",
        ("*", "Color Scheme Calculated 2"): "色スキーム結果 2",
        ("*", "Color Scheme Calculated 3"): "色スキーム結果 3",
        ("*", "Color Scheme Calculated 4"): "色スキーム結果 4",
        ("*", "Add to Favorites"): "お気に入りに追加する",
        ("*", "Add the current color scheme to favorites"): "現在の色スキームをお気に入りに追加します",

        ("*", "Favorites:"): "お気に入り:",
        ("*", "Remove Selected"): "選択しているものを削除",
        ("*", "Remove the selected color scheme from your favorites"): "お気に入りから選んだ色スキームを削除します",

        ("*", "Color 1"): "色 1",
        ("*", "Color 2"): "色 2",
        ("*", "Color 3"): "色 3",
        ("*", "Color 4"): "色 4",
    }
}



class COLORSCHEME_OT_ColorRandomize(bpy.types.Operator):
    bl_idname = "colorscheme.colorrandomize"
    bl_label = "Random"
    bl_description = "Generate a random color"
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
    bl_label = "Lighten Scheme"
    bl_description = "Increase the brightness"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene.colorscheme_base = hsv_to_rgb(scene.colorscheme_base.h,
                                                scene.colorscheme_base.s,
                                                scene.colorscheme_base.v + 0.05 * maxSvValue)
        return {'FINISHED'}

class COLORSCHEME_OT_ColorDarken(bpy.types.Operator):
    bl_idname = "colorscheme.colordarken"
    bl_label = "Darken Scheme"
    bl_description = "Decrease the brightness"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene.colorscheme_base = hsv_to_rgb(scene.colorscheme_base.h,
                                                scene.colorscheme_base.s,
                                                scene.colorscheme_base.v - 0.05 * maxSvValue)
        return {'FINISHED'}


class COLORSCHEME_OT_ColorSaturate(bpy.types.Operator):
    bl_idname = "colorscheme.colorsaturate"
    bl_label = "Saturate Scheme"
    bl_description = "Increase the saturation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene.colorscheme_base = hsv_to_rgb(scene.colorscheme_base.h,
                                                scene.colorscheme_base.s + 0.05 * maxSvValue,
                                                scene.colorscheme_base.v)
        return {'FINISHED'}

class COLORSCHEME_OT_ColorDesaturate(bpy.types.Operator):
    bl_idname = "colorscheme.colordesaturate"
    bl_label = "Desaturate Scheme"
    bl_description = "Decrease the saturation"
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
                                get=lambda t: t["color1"]
                                              if "color1" in t else [0.0,0.0,0.0],
                                set=lambda t, v: None)
    color2: FloatVectorProperty(name="Color 2", 
                                subtype='COLOR', 
                                get=lambda t: t["color2"]
                                              if "color2" in t else [0.0,0.0,0.0],
                                set=lambda t, v: None)
    color3: FloatVectorProperty(name="Color 3", 
                                subtype='COLOR',
                                get=lambda t: t["color3"]
                                              if "color3" in t else [0.0,0.0,0.0],
                                set=lambda t, v: None)
    color4: FloatVectorProperty(name="Color 4", 
                                subtype='COLOR',
                                get=lambda t: t["color4"]
                                              if "color4" in t else [0.0,0.0,0.0],
                                set=lambda t, v: None)


def method_to_length(method):
    return 2 if method == 'COMPLEMENTS' else 4 if method == 'TETRADS' else 3

class COLORSCHEME_OT_ColorSchemeFavorite(bpy.types.Operator):
    bl_idname = "colorscheme.colorschemefavorite"
    bl_label = "Add to Favorites"
    bl_description = "Add the current colors to favorites"
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
    bl_label = "Remove Selected"
    bl_description = "Remove the selected colors from your favorites"
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
                                                default=[0.8,0.8,0.8],
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
                                                get=lambda t: t["colorscheme_calculated1"]
                                                if "colorscheme_calculated1" in t else [0.0,0.0,0.0],
                                                set=lambda t, v: None)

    scene.colorscheme_calculated2 = FloatVectorProperty(name="Color Scheme Calculated 2", 
                                                subtype='COLOR',
                                                get=lambda t: t["colorscheme_calculated2"]
                                                if "colorscheme_calculated2" in t else [0.0,0.0,0.0],
                                                set=lambda t, v: None)

    scene.colorscheme_calculated3 = FloatVectorProperty(name="Color Scheme Calculated 3", 
                                                subtype='COLOR', 
                                                get=lambda t: t["colorscheme_calculated3"]
                                                if "colorscheme_calculated3" in t else [0.0,0.0,0.0],
                                                set=lambda t, v: None)

    scene.colorscheme_calculated4 = FloatVectorProperty(name="Color Scheme Calculated 4", 
                                                subtype='COLOR', 
                                                get=lambda t: t["colorscheme_calculated4"]
                                                if "colorscheme_calculated4" in t else [0.0,0.0,0.0],
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
    try:
        bpy.app.translations.register(__name__, translation_dict)
    except: pass


def unregister():
    clear_props()
    for c in classes:
        bpy.utils.unregister_class(c)
    try:
        bpy.app.translations.unregister(__name__)
    except: pass

if __name__ == "__main__":
    register()
