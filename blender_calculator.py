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
    EnumProperty,
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

import math
from math import nan, inf
import numpy as np
import cmath
func_dict = {"sqrt": math.sqrt,
             "abs": math.fabs,
             "log": np.log10,
             "ln": np.log,
             "re": lambda x: x.real,
             "im": lambda x: x.imag,
             "conj": np.conj,
             "arg": lambda x: np.angle(x, deg=True),
             "sin": lambda x: np.sin(np.deg2rad(x)), # TODO: complex number
             "cos": lambda x: np.cos(np.deg2rad(x)), # TODO: complex number
             "tan": lambda x: np.tan(np.deg2rad(x)), # TODO: complex number

             "asin": lambda x: np.rad2deg(np.arcsin(x)), # TODO: complex number
             "acos": lambda x: np.rad2deg(np.arccos(x)), # TODO: complex number
             "atan": lambda x: np.rad2deg(np.arctan(x)), # TODO: complex number

             "sinh": np.sinh,
             "cosh": np.cosh,
             "tanh": np.tanh,
             "asinh": np.arcsinh,
             "acosh": np.arccosh,
             "atanh": np.arctanh,

             "sgn": np.sign,
             "round": np.round, # TODO: hmm... round(12.5) -> 12
             "floor": np.floor,
             "ceil": np.ceil,
             "int": int,
             "frac": lambda x: math.modf(x)[0],

#             "ones": ,
#             "twos": ,
#             "not": ,

              "sin⁻¹": None, # just for function menu
              "cos⁻¹": None,
              "sin⁻¹": None,
              "tan⁻¹": None,
              "sinh⁻¹": None,
              "cosh⁻¹": None,
              "tanh⁻¹": None,
            }

from random import random
def update_rand(scene):
    var = None
    for i in scene.calc_vars:
        if i.name == "rand":
            var = i
    if not var:
        var = scene.calc_vars.add()
    var.name = "rand"
    var.val = str(random())

def initialize_collection(scene):
    update_rand(scene)

    for i in sorted(func_dict.keys()):
        func = scene.calc_funcs.add()
        func.proto = i + "(x)"
        func.define = "___builtin"
        

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

import re

def calc_update(self, context):
    exp = self.calc_exp

    if not self.calc_is_inited:
        initialize_collection(self)
        self.calc_is_inited = True

    exp = exp.replace("/", "÷") \
             .replace("**", "^") \
             .replace("×*", "^") \
             .replace("*", "×") \
             .replace("-", "−") \
             .replace("<<", "«") \
             .replace(">>", "»") \
             .replace(",", ".")
    if exp != self.calc_exp:
        self.calc_exp = exp
        return

    if exp.find("__") >= 0 or exp == "": # dangerous
        return
    if (not self.calc_is_live) and exp[-1] != "=":
        return

    reg = re.match("^\s*([a-zA-Z_]+\\([a-zA-Z_;\s]*\\))\s*=(.*)$", exp) # "f(; y) = y" is acceptable
    rexp = None
    if reg:
        rexp = reg.group(2)
    if rexp and re.match(".*[a-zA-Z_0-9\\.π].*", rexp):
        # function define mode
        proto = reg.group(1)
        func_name = proto.split("(")[0]
        if func_name in func_dict.keys():
            return # don't overwrite builtin functions

#        print(proto + ":::" + reg.group(2))
        func = None
        for i in self.calc_funcs:
            if i.proto.split("(")[0] == func_name:
                func = i
        if not func:
            func = self.calc_funcs.add()
        func.proto = reg.group(1)
        func.define = reg.group(2)
        return

    exp = exp if exp[-1] != "=" else exp[0:-1]
    exp_re = re.split("^\s*([a-zA-Z_][a-zA-Z_0-9]*)=(.+)$", exp)
    exp_inner = exp if exp_re[0] else exp_re[2]
    var_name = exp_re[1] if len(exp_re) > 1 else None


    for i in self.calc_funcs:
        if i.define != "___builtin":
            func_name = i.proto.split("(")[0]
#            exp_inner.replace(func_name, "")
            params = re.split("\s*;\s*", re.sub("^[a-zA-Z_]+\\(\s*(.*?)\s*\\)$", "\\1", i.proto))
            reg = "(^|[^a-zA-Z_])" + func_name + "\\("
            treg = "\\1(" + i.define
            for n, param in enumerate(params):
                reg +=  "([^;]*);"
                if param == "":
                    continue
                treg = re.sub("(^|[^a-zA-Z_])" + param + "(?![a-zA-Z_])", "\\1"+"\\\\"+str(n+2), treg)
#                print(str(n) + ":" + param)
#                print(treg)
            reg = reg[0:-1] + "\\)"
            treg += ")"
            print(i.proto)
            print(reg)
            print(i.define)
            print(treg)
            exp_inner = re.sub(reg, treg, exp_inner)

    dict = {}
    for i in self.calc_vars:
            dict[i.name] = eval(i.val.replace("i", "j").replace("jnf", "inf"))

    exp_inner = exp_inner.replace("^", "**")

    exp_inner = exp_inner.replace("√", "sqrt") \
                         .replace("sin⁻¹", "asin") \
                         .replace("cos⁻¹", "acos") \
                         .replace("sin⁻¹", "asin") \
                         .replace("tan⁻¹", "atan") \
                         .replace("sinh⁻¹", "asinh") \
                         .replace("cosh⁻¹", "acosh") \
                         .replace("tanh⁻¹", "atanh") \
                         .replace("÷", "/") \
                         .replace("×", "*") \
                         .replace("−", "-") \
                         .replace("«", "<<") \
                         .replace("»", ">>") \
                         .replace("∧", "&") \
                         .replace("∨", "|") \
                         .replace("⊻", "^") \
                         .replace("⁻¹", "**-1") \
                         .replace("²", "**2") \
                         .replace("π", "___pi") \
                         .replace("%", "*0.01")

    exp_inner = re.sub("([⁰¹²³⁴⁵⁶⁷⁸⁹]+)", "**\\1", exp_inner)
    exp_inner = exp_inner.translate(str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹","0123456789"))

    exp_inner = re.sub("([^a-zA-Z_]|^)log\s*([₀₁₂₃₄₅₆₇₈₉]+)\\((.+)\\)", "\\1___log(\\3,\\2)", exp_inner) # log₂₃(12)
    exp_inner = re.sub("([^a-zA-Z_]|^)log\s*([₀₁₂₃₄₅₆₇₈₉]+)\s*([0-9\\.]+)", "\\1___log(\\3,\\2)", exp_inner) # log₂₃12
    exp_inner = re.sub("([^a-zA-Z_]|^)log\s*([₀₁₂₃₄₅₆₇₈₉]+)\s*([a-zA-Z_]+)", "\\1___log(\\3,\\2)", exp_inner) # log₂₃aa
    exp_inner = exp_inner.translate(str.maketrans("₀₁₂₃₄₅₆₇₈₉","0123456789"))

    exp_inner = re.sub("([0-9\\.\s]+)and([0-9\\.\s]+)", "\\1&\\2", exp_inner) # 12 and 5 = 4
    exp_inner = re.sub("([0-9\\.\s]+)or([0-9\\.\s]+)", "\\1|\\2", exp_inner) # 12 and 5 = 13
    exp_inner = re.sub("([0-9\\.\s]+)xor([0-9\\.\s]+)", "\\1^\\2", exp_inner)
    exp_inner = re.sub("([0-9\\.\s]+)mod([0-9\\.\s]+)", "\\1%\\2", exp_inner)
    # TODO: mod with hexadecimal mode

    # 11e -> 11 * e ; 4(12) -> 4 * (12) ; (12)(12) -> (12) * (12) ; (12)e -> (12) * e
    exp_inner = re.sub("([0-9\\.\\)]+)\s*([a-zA-Z_\\(]+)", "\\1 * \\2", exp_inner)
    exp_inner = re.sub("([\\)]+)\s*([0-9\\.]+)", "\\1 * \\2", exp_inner) # (12)4 -> (12) * 4
    exp_inner = re.sub("([a-zA-Z_]+)\s*([0-9\\.]+|\s+[a-zA-Z_]+)", "\\1(\\2)", exp_inner) # frac11 -> frac(11)

# a=2
# sqrt2a = 2.8284

    exp_inner = re.sub("([0-9\\.]+|[a-zA-Z_]+)\s*!", " ___factorial(\\1)", exp_inner)

    # Complex Number translation
    exp_inner = re.sub("(([^a-zA-Z_0-9\\.]+|^)[0-9\\.]+) \\* i([^a-zA-Z_]+|$)", "\\1j\\3", exp_inner)

#    print(exp_inner)

    dict |= func_dict

    dict |= {
             "___factorial": lambda x: math.gamma(x + 1), # internal
             "___log": math.log,
             "___pi": math.pi,
             "e": math.e,
             "i": 1j,
    }

    try:
#    if True:
        res = str(eval(exp_inner, {'__builtins__': dict})).replace("j", "i")
        if res == exp:
            return

        if var_name:
            var = None
            for i in self.calc_vars:
                if i.name == var_name:
                    var = i
            if not var:
                var = self.calc_vars.add()
            var.name = var_name
            var.val = res

        self.calc_exp = res
        hist = self.calc_hist.add()
        hist["exp"] = exp
        hist["result"] = res
        self.calc_hist.move(len(self.calc_hist)-1, 0)

        var = None
        for i in self.calc_vars:
            if i.name == "_":
                var = i
        if not var:
            var = self.calc_vars.add()
        var.name = "_"
        var.val = res

        update_rand(self)

    except: pass

class CALC_OT_InputBase():
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        scene = context.scene
        if self.c in ["sqrt", "abs", "arg", "log", "ln", "re", "im", "conj", \
                      "sin", "cos", "tan", "sinh", "cosh", "tanh"]:
            if scene.calc_is_live:
                scene.calc_exp = self.c + "(" + scene.calc_exp + ")"
            else:
                scene.calc_exp = scene.calc_exp + self.c + " "
        elif self.c in "0123456789":
            if scene.calc_is_subscript_input:
                while scene.calc_exp[-1] == " ":
                    scene.calc_exp = scene.calc_exp[0:-1]
                scene.calc_exp += "₀₁₂₃₄₅₆₇₈₉"[int(self.c[0])-int('0')]
            elif scene.calc_is_superscript_input:
                scene.calc_exp += "⁰¹²³⁴⁵⁶⁷⁸⁹"[int(self.c[0])-int('0')]
            else:
                scene.calc_exp += self.c
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
CALC_OT_Input_minus = CALC_new_input_class("−", "minus")
CALC_OT_Input_mul = CALC_new_input_class("×", "mul")
CALC_OT_Input_div = CALC_new_input_class("÷", "div")
CALC_OT_Input_mod = CALC_new_input_class(" mod ", "mod")
CALC_OT_Input_lp = CALC_new_input_class("(", "lp")
CALC_OT_Input_rp = CALC_new_input_class(")", "rp")
CALC_OT_Input_sq = CALC_new_input_class("²", "sq")
CALC_OT_Input_inv = CALC_new_input_class("⁻¹", "inv")
CALC_OT_Input_pow = CALC_new_input_class("^", "pow")
CALC_OT_Input_sqrt = CALC_new_input_class("√", "sqrt")
CALC_OT_Input_factorial = CALC_new_input_class("!", "factorial")
CALC_OT_Input_imag = CALC_new_input_class("i", "imag")
CALC_OT_Input_abs = CALC_new_input_class("abs")
CALC_OT_Input_arg = CALC_new_input_class("arg")
CALC_OT_Input_log = CALC_new_input_class("log")
CALC_OT_Input_ln = CALC_new_input_class("ln")
CALC_OT_Input_re = CALC_new_input_class("re")
CALC_OT_Input_im = CALC_new_input_class("im")
CALC_OT_Input_conj = CALC_new_input_class("conj")
CALC_OT_Input_sin = CALC_new_input_class("sin")
CALC_OT_Input_cos = CALC_new_input_class("cos")
CALC_OT_Input_tan = CALC_new_input_class("tan")
CALC_OT_Input_sinh = CALC_new_input_class("sinh")
CALC_OT_Input_cosh = CALC_new_input_class("cosh")
CALC_OT_Input_tanh = CALC_new_input_class("tanh")
CALC_OT_Input_pi = CALC_new_input_class("π", "pi")
CALC_OT_Input_e = CALC_new_input_class("e")
CALC_OT_Input_sexp = CALC_new_input_class("×10^", "sexp")

CALC_OT_Input_equal = CALC_new_input_class("=", "equal")


class CALC_OT_ExpClear(bpy.types.Operator):
    bl_idname = "calc.expclear"
    bl_label = "Clear Expression"
    bl_description = "Make the expression text filed to empty"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene.calc_exp = ""
        return {'FINISHED'}

class CALC_OT_HistClear(bpy.types.Operator):
    bl_idname = "calc.histclear"
    bl_label = "Clear History"
    bl_description = "Remove all history"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene.calc_hist.clear()
        scene.calc_vars.clear()
        scene.calc_funcs.clear()
        initialize_collection(scene)
        return {'FINISHED'}

class CALC_UL_VariablesList(bpy.types.UIList):
    use_filter_show: False
    def draw_item(self, context, layout, data, item, icon, active_data):
        col = layout.column()
        row = col.row(align=True)
        row.label(text=item.name)
        row.label(text="", icon="FORWARD")
        row.prop(item, "val", text="")

    def draw_filter(self, context, layout): # hide useless filter menus
        row = layout.row()

class CALC_MT_Variables(bpy.types.Menu):
    bl_idname="CALC_MT_variables"
    bl_label="Menu"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.template_list("CALC_UL_VariablesList", "", scene, "calc_vars", scene, "active_calc_vars_index")

class CALC_UL_FunctionsList(bpy.types.UIList):
    use_filter_show: False
    def draw_item(self, context, layout, data, item, icon, active_data):
        col = layout.column()
        row = col.row(align=True)
        row.label(text=item.proto + " = " + item.define)
#        row.label(text=item.proto)
#        row.label(text="", icon="FORWARD")
#        row.prop(item, "define", text="")

    def draw_filter(self, context, layout): # hide useless filter menus
        row = layout.row()

class CALC_MT_Functions(bpy.types.Menu):
    bl_idname="CALC_MT_functions"
    bl_label="Menu"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.template_list("CALC_UL_FunctionsList", "", scene, "calc_funcs", scene, "active_calc_funcs_index")

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

        row = layout.row()
        row.prop(scene, "calc_mode", text="Mode")
        row.prop(scene, "calc_is_live")

        if scene.calc_mode == "BASIC":
            row = layout.row(align=True)
            row.operator(CALC_OT_Input_7.bl_idname, text="7")
            row.operator(CALC_OT_Input_8.bl_idname, text="8")
            row.operator(CALC_OT_Input_9.bl_idname, text="9")
            row.operator(CALC_OT_Input_div.bl_idname, text="÷")
            row.operator("ed.undo", text="Undo")
            row.operator(CALC_OT_ExpClear.bl_idname, text="C")
            row = layout.row(align=True)
            row.operator(CALC_OT_Input_4.bl_idname, text="4")
            row.operator(CALC_OT_Input_5.bl_idname, text="5")
            row.operator(CALC_OT_Input_6.bl_idname, text="6")
            row.operator(CALC_OT_Input_mul.bl_idname, text="×")
            row.operator(CALC_OT_Input_lp.bl_idname, text="(")
            row.operator(CALC_OT_Input_rp.bl_idname, text=")")
            row = layout.row(align=True)
            row.operator(CALC_OT_Input_1.bl_idname, text="1")
            row.operator(CALC_OT_Input_2.bl_idname, text="2")
            row.operator(CALC_OT_Input_3.bl_idname, text="3")
            row.operator(CALC_OT_Input_minus.bl_idname, text="−")
            row.operator(CALC_OT_Input_sq.bl_idname, text="x²")
            row.operator(CALC_OT_Input_sqrt.bl_idname, text="√")
            row = layout.row(align=True)
            row.operator(CALC_OT_Input_0.bl_idname, text="0")
            row.operator(CALC_OT_Input_dot.bl_idname, text=".")
            row.operator(CALC_OT_Input_percent.bl_idname, text="%")
            row.operator(CALC_OT_Input_plus.bl_idname, text="+")

            row.label(text="") # placeholder
            col = row.column()
            col.enabled = not scene.calc_is_live
            col.operator(CALC_OT_Input_equal.bl_idname, text="=")
        elif scene.calc_mode == "ADVANCED":
            row = layout.row(align=True)
            row.prop(scene, "calc_is_subscript_input", text="↓n", toggle=True)
            row.prop(scene, "calc_is_superscript_input", text="↑n", toggle=True)
            row.operator(CALC_OT_Input_sexp.bl_idname, text="×10ʸ")
            row.operator(CALC_OT_Input_mod.bl_idname, text="mod")
            row.operator("ed.undo", text="Undo")
            row.operator(CALC_OT_ExpClear.bl_idname, text="C")
            row.label(text="") # placeholder
            row.operator(CALC_OT_Input_cos.bl_idname, text="cos")
            row.operator(CALC_OT_Input_sin.bl_idname, text="sin")
            row.operator(CALC_OT_Input_tan.bl_idname, text="tan")
            row = layout.row(align=True)
            row.operator(CALC_OT_Input_7.bl_idname, text="7")
            row.operator(CALC_OT_Input_8.bl_idname, text="8")
            row.operator(CALC_OT_Input_9.bl_idname, text="9")
            row.operator(CALC_OT_Input_div.bl_idname, text="÷")
            row.operator(CALC_OT_Input_lp.bl_idname, text="(")
            row.operator(CALC_OT_Input_rp.bl_idname, text=")")
            row.label(text="") # placeholder
            row.operator(CALC_OT_Input_sinh.bl_idname, text="sinh")
            row.operator(CALC_OT_Input_cosh.bl_idname, text="cosh")
            row.operator(CALC_OT_Input_tanh.bl_idname, text="tanh")
            row = layout.row(align=True)
            row.operator(CALC_OT_Input_4.bl_idname, text="4")
            row.operator(CALC_OT_Input_5.bl_idname, text="5")
            row.operator(CALC_OT_Input_6.bl_idname, text="6")
            row.operator(CALC_OT_Input_mul.bl_idname, text="×")
            row.menu(CALC_MT_Variables.bl_idname, text="x")
            row.label(text="") # placeholder
            row.operator(CALC_OT_Input_inv.bl_idname, text="x⁻¹")
            row.operator(CALC_OT_Input_factorial.bl_idname, text="x!")
            row.operator(CALC_OT_Input_abs.bl_idname, text="|x|")
            row.operator(CALC_OT_Input_arg.bl_idname, text="Arg")
            row = layout.row(align=True)
            row.operator(CALC_OT_Input_1.bl_idname, text="1")
            row.operator(CALC_OT_Input_2.bl_idname, text="2")
            row.operator(CALC_OT_Input_3.bl_idname, text="3")
            row.operator(CALC_OT_Input_minus.bl_idname, text="−")
            row.operator(CALC_OT_Input_pi.bl_idname, text="π")
            row.operator(CALC_OT_Input_e.bl_idname, text="e")
            row.operator(CALC_OT_Input_pow.bl_idname, text="xʸ")
            row.operator(CALC_OT_Input_sqrt.bl_idname, text="√")
            row.operator(CALC_OT_Input_log.bl_idname, text="log")
            row.operator(CALC_OT_Input_ln.bl_idname, text="ln")
            row = layout.row(align=True)
            row.operator(CALC_OT_Input_0.bl_idname, text="0")
            row.operator(CALC_OT_Input_dot.bl_idname, text=".")
            row.operator(CALC_OT_Input_imag.bl_idname, text="i")
            row.operator(CALC_OT_Input_plus.bl_idname, text="+")
            col = row.column()
            col.enabled = not scene.calc_is_live
            col.operator(CALC_OT_Input_equal.bl_idname, text="=")
            row.label(text="") # placeholder
            row.operator(CALC_OT_Input_re.bl_idname, text="Re")
            row.operator(CALC_OT_Input_im.bl_idname, text="Im")
            row.operator(CALC_OT_Input_conj.bl_idname, text="conj")
            row.menu(CALC_MT_Functions.bl_idname, text="f(x)")


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

class CALC_Function_PropertiesGroup(bpy.types.PropertyGroup):
    proto: StringProperty(name="Function Prototype", default="")
    define: StringProperty(name="Function Define", default="")

def update_superscript(self, context):
    if self.calc_is_superscript_input:
        self.calc_is_subscript_input = False

def update_subscript(self, context):
    if self.calc_is_subscript_input:
        self.calc_is_superscript_input = False

def update_active_calc_vars_index(self, context):
    self.calc_exp += self.calc_vars[self.active_calc_vars_index].name

def update_active_calc_funcs_index(self, context):
    self.calc_exp += self.calc_funcs[self.active_calc_funcs_index].proto.split("(")[0]+"("

def update_mode(self, context):
    if not self.calc_is_inited:
        initialize_collection(self)
        self.calc_is_inited = True

def init_props():
    scene = bpy.types.Scene
    scene.calc_exp = StringProperty(name="Expression for calculation",
                                    default="", update=calc_update)
    scene.calc_hist = CollectionProperty(type=CALC_Hist_PropertiesGroup)
    scene.active_calc_hist_index = IntProperty(name="Active calculation history index")

    scene.calc_vars = CollectionProperty(type=CALC_Variable_PropertiesGroup)
    scene.active_calc_vars_index = IntProperty(name="Active calculation variables index",
                                               update=update_active_calc_vars_index)

    scene.calc_funcs = CollectionProperty(type=CALC_Function_PropertiesGroup)
    scene.active_calc_funcs_index = IntProperty(name="Active calculation functions index",
                                               update=update_active_calc_funcs_index)

    scene.calc_mode = EnumProperty(
        name="Calculator Mode",
        description="The mode of calculator",
        items=[
            ('BASIC', "Basic Mode", "Basic Mode"),
            ('ADVANCED', "Advanced Mode", "Advanced Mode"),
        ],
        default='BASIC',
        update=update_mode
    )

    scene.calc_is_live = BoolProperty(name="Live Calculation",
                                      description="If you checked this, the valid expression will evaluate immediately. "+ \
                                                   "If not, the evaluation is delayed to the input of '='",
                                      default=False)

    scene.calc_is_superscript_input = BoolProperty(name="Superscript Input",
                                                   default=False,
                                                   update=update_superscript)
    scene.calc_is_subscript_input = BoolProperty(name="Subscript Input",
                                                 default=False,
                                                 update=update_subscript)

    scene.calc_is_inited = BoolProperty(name="Is Calculator Inited",
                                        default=False)


def clear_props():
    del calc_exp
    del scene.calc_hist
    del scene.active_calc_hist_index
    del scene.calc_vars
    del scene.active_calc_vars_index
    del scene.calc_funcs
    del scene.active_calc_funcs_index
    del scene.calc_mode
    del scene.calc_is_live
    del scene.calc_is_inited

classes = [
    CALC_PT_CustomPanel,
    CALC_OT_HistClear,
    CALC_Hist_PropertiesGroup,
    CALC_UL_HistList,
    CALC_Variable_PropertiesGroup,
    CALC_UL_VariablesList,
    CALC_MT_Variables,
    CALC_Function_PropertiesGroup,
    CALC_UL_FunctionsList,
    CALC_MT_Functions,
    CALC_OT_ExpClear,
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
    CALC_OT_Input_mod,
    CALC_OT_Input_lp,
    CALC_OT_Input_rp,
    CALC_OT_Input_sq,
    CALC_OT_Input_inv,
    CALC_OT_Input_pow,
    CALC_OT_Input_sqrt,
    CALC_OT_Input_factorial,
    CALC_OT_Input_imag,
    CALC_OT_Input_abs,
    CALC_OT_Input_arg,
    CALC_OT_Input_log,
    CALC_OT_Input_ln,
    CALC_OT_Input_re,
    CALC_OT_Input_im,
    CALC_OT_Input_conj,
    CALC_OT_Input_sin,
    CALC_OT_Input_cos,
    CALC_OT_Input_tan,
    CALC_OT_Input_sinh,
    CALC_OT_Input_cosh,
    CALC_OT_Input_tanh,
    CALC_OT_Input_pi,
    CALC_OT_Input_e,
    CALC_OT_Input_sexp,
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

