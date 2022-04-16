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
# Calculator Addon for Blender
#
# Copyright (C) 2022 Toshimitsu Kimura <lovesyao@gmail.com>
#
# Note: The UI is some or less inspired from GNOME Calculator

import bpy
from bpy.props import (
    BoolProperty,
    StringProperty,
    IntProperty,
    CollectionProperty,
)

bl_info = {
    "name": "Calculator",
    "author": "Toshimitsu Kimura",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "3D Viewport > Sidebar",
    "description": "Hash addon for Blender",
    "warning": "",
    "support": "COMMUNITY",
    "doc_url": "",
    "tracker_url": "",
    "category": "System"
}

translation_dict = {
    "en_US": {
    },
    "ja_JP": {
        ("*", "Calculator"): "電卓",

        ("*", "Expression for calculation"): "計算する式",

        ("*", "History:"): "履歴:",
        ("*", "Clear History"): "履歴をクリア",
        ("*", "Remove all history"): "全ての履歴を削除する",

        ("*", "Live Calculation"): "逐次計算",
        ("*", "If you checked this, the valid expression will evaluate immediately. "+ \
              "If not, the evaluation is delayed to the input of '='"): 
                  "これにチェックを入れた場合、正しい式は直ぐに評価されます。" + \
                  "チェックを入れなかった場合、評価は「=」の入力まで遅延されます。",
    }
}

class CALC_UL_HistList(bpy.types.UIList):
    use_filter_show: False
    def draw_item(self, context, layout, data, item, icon, active_data):
        col = layout.column()
        row = col.row(align=True)
        row.prop(item, "exp", text="")
        row.label(text="", icon="FORWARD")
        row.prop(item, "result", text="")

    def draw_filter(self, context, layout): # hide useless filter menus
        row = layout.row()

import math
import numpy as np
from random import random
import re
def calc_update(self, context):
    exp = self.calc_exp
    if exp.find("__") >= 0 or exp == "": # dangerous
        return
    if (not self.calc_is_live) and exp[-1] != "=":
        return

    exp = exp if exp[-1] != "=" else exp[0:-1]
    exp_re = re.split("^\s*([a-zA-Z_][a-zA-Z_0-9]*)=(.+)$", exp)
    exp_inner = exp if exp_re[0] else exp_re[2]
    var_name = exp_re[1] if len(exp_re) > 1 else None

    dict = {}
    for i in self.calc_vars:
            dict[i.name] = eval(i.val)

    dict |= {"sqrt": math.sqrt,
             "factorial": lambda x: math.gamma(x + 1),
             "fabs": math.fabs,
             "log": np.log10,
             "ln": np.log,
             "_": eval(self.calc_hist[0].result) if len(self.calc_hist) else 0,
             "rand": random(),
            }

    try:
#    if True:
        res = str(eval(exp_inner, {'__builtins__': dict}))
        if res == exp:
            return

        if var_name:
            var = self.calc_vars.add()
            var.name = var_name
            var.val = exp_inner

        self.calc_exp = res
        hist = self.calc_hist.add()
        hist["exp"] = exp
        hist["result"] = res
        self.calc_hist.move(len(self.calc_hist)-1, 0)
    except: pass

class CALC_OT_InputBase():
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        scene = context.scene
        if self.c in ["sqrt", "factorial", "fabs", "log", "ln"]:
            scene.calc_exp = self.c + "(" + scene.calc_exp + ")"
        else:
            scene.calc_exp += self.c
        return {'FINISHED'}

def CALC_new_input_class(c, id = None):
    if not id:
        id = c
    return type('CALC_OT_Input_' + id, (bpy.types.Operator, CALC_OT_InputBase),
                {'c': c,
                 'bl_idname': "calc.input" + id,
                 'bl_label': "Input " + id,
                 'bl_description': "Input " + id},
               )
CALC_OT_Input_0 = CALC_new_input_class("0")
CALC_OT_Input_1 = CALC_new_input_class("1")
CALC_OT_Input_2 = CALC_new_input_class("2")
CALC_OT_Input_3 = CALC_new_input_class("3")
CALC_OT_Input_4 = CALC_new_input_class("4")
CALC_OT_Input_5 = CALC_new_input_class("5")
CALC_OT_Input_6 = CALC_new_input_class("6")
CALC_OT_Input_7 = CALC_new_input_class("7")
CALC_OT_Input_8 = CALC_new_input_class("8")
CALC_OT_Input_9 = CALC_new_input_class("9")
CALC_OT_Input_dot = CALC_new_input_class(".", "dot")
CALC_OT_Input_percent = CALC_new_input_class("%", "percent")
CALC_OT_Input_plus = CALC_new_input_class("+", "plus")
CALC_OT_Input_minus = CALC_new_input_class("-", "minus")
CALC_OT_Input_mul = CALC_new_input_class("*", "mul")
CALC_OT_Input_div = CALC_new_input_class("/", "div")
CALC_OT_Input_lp = CALC_new_input_class("(", "lp")
CALC_OT_Input_rp = CALC_new_input_class(")", "rp")
CALC_OT_Input_sq = CALC_new_input_class("**2", "sq")
CALC_OT_Input_sqrt = CALC_new_input_class("sqrt")
CALC_OT_Input_factorial = CALC_new_input_class("factorial")
CALC_OT_Input_fabs = CALC_new_input_class("fabs")
CALC_OT_Input_log = CALC_new_input_class("log")
CALC_OT_Input_ln = CALC_new_input_class("ln")

CALC_OT_Input_equal = CALC_new_input_class("=", "equal")

class CALC_OT_HistClear(bpy.types.Operator):
    bl_idname = "calc.histclear"
    bl_label = "Clear History"
    bl_description = "Remove all history"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene.calc_hist.clear()
        scene.calc_vars.clear()
        return {'FINISHED'}

class CALC_PT_CustomPanel(bpy.types.Panel):
    bl_label = "Calculator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Calculator"
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
        layout.prop(scene, "calc_exp", text="Expression")
        row = layout.row(align=True)
        row.label(text="History:")
        row.operator(CALC_OT_HistClear.bl_idname, text="", icon="X")
        layout.template_list("CALC_UL_HistList", "", scene, "calc_hist", scene, "active_calc_hist_index")

        layout.prop(scene, "calc_is_live")

        row = layout.row(align=True)
        row.operator(CALC_OT_Input_7.bl_idname, text="7")
        row.operator(CALC_OT_Input_8.bl_idname, text="8")
        row.operator(CALC_OT_Input_9.bl_idname, text="9")
        row.operator(CALC_OT_Input_div.bl_idname, text="/")
        row.operator(CALC_OT_Input_log.bl_idname, text="log")
        row.operator(CALC_OT_Input_ln.bl_idname, text="ln")
        row = layout.row(align=True)
        row.operator(CALC_OT_Input_4.bl_idname, text="4")
        row.operator(CALC_OT_Input_5.bl_idname, text="5")
        row.operator(CALC_OT_Input_6.bl_idname, text="6")
        row.operator(CALC_OT_Input_mul.bl_idname, text="*")
        row.operator(CALC_OT_Input_lp.bl_idname, text="(")
        row.operator(CALC_OT_Input_rp.bl_idname, text=")")
        row = layout.row(align=True)
        row.operator(CALC_OT_Input_1.bl_idname, text="1")
        row.operator(CALC_OT_Input_2.bl_idname, text="2")
        row.operator(CALC_OT_Input_3.bl_idname, text="3")
        row.operator(CALC_OT_Input_minus.bl_idname, text="-")
        row.operator(CALC_OT_Input_sq.bl_idname, text="x²")
        row.operator(CALC_OT_Input_sqrt.bl_idname, text="√")
        row = layout.row(align=True)
        row.operator(CALC_OT_Input_0.bl_idname, text="0")
        row.operator(CALC_OT_Input_dot.bl_idname, text=".")
        row.operator(CALC_OT_Input_percent.bl_idname, text="%")
        row.operator(CALC_OT_Input_plus.bl_idname, text="+")
        row.operator(CALC_OT_Input_factorial.bl_idname, text="x!")
        row.operator(CALC_OT_Input_fabs.bl_idname, text="|x|")

        row = layout.row()
        row.enabled = not scene.calc_is_live
        row.operator(CALC_OT_Input_equal.bl_idname, text="=")


class CALC_Hist_PropertiesGroup(bpy.types.PropertyGroup):
    exp: StringProperty(name="Expression", default="", 
                        get=lambda t: t["exp"]
                        if "exp" in t else "",
                        set=lambda t, v: None)
    result: StringProperty(name="Result", default="", 
                           get=lambda t: t["result"]
                           if "result" in t else "",
                           set=lambda t, v: None)

class CALC_Variable_PropertiesGroup(bpy.types.PropertyGroup):
    name: StringProperty(name="Variable Name", default="")
    val: StringProperty(name="Variable Value", default="")

def init_props():
    scene = bpy.types.Scene
    scene.calc_exp = StringProperty(name="Expression for calculation",
                                    default="", update=calc_update)
    scene.calc_hist = CollectionProperty(type=CALC_Hist_PropertiesGroup)
    scene.active_calc_hist_index = IntProperty(name="Active calculation history index")

    scene.calc_vars = CollectionProperty(type=CALC_Variable_PropertiesGroup)

    scene.calc_is_live = BoolProperty(name="Live Calculation",
                                      description="If you checked this, the valid expression will evaluate immediately. "+ \
                                                   "If not, the evaluation is delayed to the input of '='",
                                      default=False)

def clear_props():
    del calc_exp
    del scene.calc_hist
    del scene.active_calc_hist_index
    del scene.calc_is_live

classes = [
    CALC_PT_CustomPanel,
    CALC_OT_HistClear,
    CALC_Hist_PropertiesGroup,
    CALC_UL_HistList,
    CALC_Variable_PropertiesGroup,
    CALC_OT_Input_0,
    CALC_OT_Input_1,
    CALC_OT_Input_2,
    CALC_OT_Input_3,
    CALC_OT_Input_4,
    CALC_OT_Input_5,
    CALC_OT_Input_6,
    CALC_OT_Input_7,
    CALC_OT_Input_8,
    CALC_OT_Input_9,
    CALC_OT_Input_dot,
    CALC_OT_Input_percent,
    CALC_OT_Input_plus,
    CALC_OT_Input_minus,
    CALC_OT_Input_mul,
    CALC_OT_Input_div,
    CALC_OT_Input_lp,
    CALC_OT_Input_rp,
    CALC_OT_Input_sq,
    CALC_OT_Input_sqrt,
    CALC_OT_Input_factorial,
    CALC_OT_Input_fabs,
    CALC_OT_Input_log,
    CALC_OT_Input_ln,
    CALC_OT_Input_equal,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    init_props()
    try:
        bpy.app.translations.register("blender_calculator", translation_dict)
    except: pass

def unregister():
    clear_props()
    for c in classes:
        bpy.utils.unregister_class(c)
    try:
        bpy.app.translations.unregister("blender_calculator")
    except: pass

if __name__ == "__main__":
    register()

