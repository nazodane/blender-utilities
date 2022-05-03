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
#        return

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
#            print(i.proto)
#            print(reg)
#            print(i.define)
#            print(treg)
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
    exp_inner = re.sub("(([^a-zA-Z_0-9\\.]+|^)[0-9\\.]+) \\* i(?![a-zA-Z_])", "\\1j", exp_inner)
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
        if rexp:
            res = "0"
        else:
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

    @classmethod
    def poll(cls, context):
        if context.space_data.type != "VIEW_3D" and \
           context.space_data.type != "PREFERENCES":
            return False
        return True

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

CALC_OT_Input_sub0 = CALC_new_input_class("₀", "sub0")
CALC_OT_Input_sub1 = CALC_new_input_class("₁", "sub1")
CALC_OT_Input_sub2 = CALC_new_input_class("₂", "sub2")
CALC_OT_Input_sub3 = CALC_new_input_class("₃", "sub3")
CALC_OT_Input_sub4 = CALC_new_input_class("₄", "sub4")
CALC_OT_Input_sub5 = CALC_new_input_class("₅", "sub5")
CALC_OT_Input_sub6 = CALC_new_input_class("₆", "sub6")
CALC_OT_Input_sub7 = CALC_new_input_class("₇", "sub7")
CALC_OT_Input_sub8 = CALC_new_input_class("₈", "sub8")
CALC_OT_Input_sub9 = CALC_new_input_class("₉", "sub9")

CALC_OT_Input_super0 = CALC_new_input_class("⁰", "super0")
CALC_OT_Input_super1 = CALC_new_input_class("¹", "super1")
CALC_OT_Input_super2 = CALC_new_input_class("²", "super2")
CALC_OT_Input_super3 = CALC_new_input_class("³", "super3")
CALC_OT_Input_super4 = CALC_new_input_class("⁴", "super4")
CALC_OT_Input_super5 = CALC_new_input_class("⁵", "super5")
CALC_OT_Input_super6 = CALC_new_input_class("⁶", "super6")
CALC_OT_Input_super7 = CALC_new_input_class("⁷", "super7")
CALC_OT_Input_super8 = CALC_new_input_class("⁸", "super8")
CALC_OT_Input_super9 = CALC_new_input_class("⁹", "super9")

CALC_OT_Input_a = CALC_new_input_class("a")
CALC_OT_Input_b = CALC_new_input_class("b")
CALC_OT_Input_c = CALC_new_input_class("c")
CALC_OT_Input_d = CALC_new_input_class("d")
CALC_OT_Input_e = CALC_new_input_class("e")
CALC_OT_Input_f = CALC_new_input_class("f")
CALC_OT_Input_g = CALC_new_input_class("g")
CALC_OT_Input_h = CALC_new_input_class("h")
CALC_OT_Input_i = CALC_new_input_class("i")
CALC_OT_Input_j = CALC_new_input_class("j")
CALC_OT_Input_k = CALC_new_input_class("k")
CALC_OT_Input_l = CALC_new_input_class("l")
CALC_OT_Input_m = CALC_new_input_class("m")
CALC_OT_Input_n = CALC_new_input_class("n")
CALC_OT_Input_o = CALC_new_input_class("o")
CALC_OT_Input_p = CALC_new_input_class("p")
CALC_OT_Input_q = CALC_new_input_class("q")
CALC_OT_Input_r = CALC_new_input_class("r")
CALC_OT_Input_s = CALC_new_input_class("s")
CALC_OT_Input_t = CALC_new_input_class("t")
CALC_OT_Input_u = CALC_new_input_class("u")
CALC_OT_Input_v = CALC_new_input_class("v")
CALC_OT_Input_w = CALC_new_input_class("w")
CALC_OT_Input_x = CALC_new_input_class("x")
CALC_OT_Input_y = CALC_new_input_class("y")
CALC_OT_Input_z = CALC_new_input_class("z")

CALC_OT_Input_A = CALC_new_input_class("A", "ua")
CALC_OT_Input_B = CALC_new_input_class("B", "ub")
CALC_OT_Input_C = CALC_new_input_class("C", "uc")
CALC_OT_Input_D = CALC_new_input_class("D", "ud")
CALC_OT_Input_E = CALC_new_input_class("E", "ue")
CALC_OT_Input_F = CALC_new_input_class("F", "uf")
CALC_OT_Input_G = CALC_new_input_class("G", "ug")
CALC_OT_Input_H = CALC_new_input_class("H", "uh")
CALC_OT_Input_I = CALC_new_input_class("I", "ui")
CALC_OT_Input_J = CALC_new_input_class("J", "uj")
CALC_OT_Input_K = CALC_new_input_class("K", "uk")
CALC_OT_Input_L = CALC_new_input_class("L", "ul")
CALC_OT_Input_M = CALC_new_input_class("M", "um")
CALC_OT_Input_N = CALC_new_input_class("N", "un")
CALC_OT_Input_O = CALC_new_input_class("O", "uo")
CALC_OT_Input_P = CALC_new_input_class("P", "up")
CALC_OT_Input_Q = CALC_new_input_class("Q", "uq")
CALC_OT_Input_R = CALC_new_input_class("R", "ur")
CALC_OT_Input_S = CALC_new_input_class("S", "us")
CALC_OT_Input_T = CALC_new_input_class("T", "ut")
CALC_OT_Input_U = CALC_new_input_class("U", "uu")
CALC_OT_Input_V = CALC_new_input_class("V", "uv")
CALC_OT_Input_W = CALC_new_input_class("W", "uw")
CALC_OT_Input_X = CALC_new_input_class("X", "ux")
CALC_OT_Input_Y = CALC_new_input_class("Y", "uy")
CALC_OT_Input_Z = CALC_new_input_class("Z", "uz")

CALC_OT_Input_underbar = CALC_new_input_class("_", "underbar")

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
CALC_OT_Input_abs = CALC_new_input_class("|", "abs")
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

CALC_OT_Input_equal = CALC_new_input_class("=", "equal")

class CALC_OT_Input_sexp(bpy.types.Operator):
    bl_idname = "calc.input_sexp"
    bl_label = "Input sexp"
    bl_description = "Input sexp"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        scene = context.scene
        scene.calc_exp += "×10"
        scene.calc_is_superscript_input = True
        return {'FINISHED'}

class CALC_OT_Input_backspace(bpy.types.Operator):
    bl_idname = "calc.input_backspace"
    bl_label = "Input backspace"
    bl_description = "Input backspace"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        scene = context.scene
        if len(scene.calc_exp):
            scene.calc_exp = scene.calc_exp[0:-1]
        return {'FINISHED'}

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
#        layout.scale_y = 1.5

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
            _row = layout.row(align=True)

            col = _row.column()
            row = col.row(align=True)
#            row.scale_x = 0.83
            row.operator(CALC_OT_Input_0.bl_idname, text="0")
            row.operator(CALC_OT_Input_dot.bl_idname, text=".")
            row.operator(CALC_OT_Input_percent.bl_idname, text="%")
            row.operator(CALC_OT_Input_plus.bl_idname, text="+")

            col = _row.column(align=True)
            col.enabled = not scene.calc_is_live
            col.scale_x = 1.44 #XXX: I don't know where this comes from...
            col.operator(CALC_OT_Input_equal.bl_idname, text="=")
        elif scene.calc_mode == "ADVANCED":
            _row = layout.row(align=True)
            col = _row.column()
            row = col.row(align=True)
            row.prop(scene, "calc_is_subscript_input", text="↓n", toggle=True)
            row.prop(scene, "calc_is_superscript_input", text="↑n", toggle=True)
            row.operator(CALC_OT_Input_sexp.bl_idname, text="×10ʸ")
            row.operator(CALC_OT_Input_mod.bl_idname, text="mod")
            row.operator("ed.undo", text="Undo")
            row.operator(CALC_OT_ExpClear.bl_idname, text="C")
            col = _row.column()
            col.scale_x = 1.33 #XXX: I don't know where this comes from...
            row = col.row(align=True)
            row.operator(CALC_OT_Input_cos.bl_idname, text="cos")
            row.operator(CALC_OT_Input_sin.bl_idname, text="sin")
            row.operator(CALC_OT_Input_tan.bl_idname, text="tan")
            _row = layout.row(align=True)
            col = _row.column()
            row = col.row(align=True)
            row.operator(CALC_OT_Input_7.bl_idname, text="7")
            row.operator(CALC_OT_Input_8.bl_idname, text="8")
            row.operator(CALC_OT_Input_9.bl_idname, text="9")
            row.operator(CALC_OT_Input_div.bl_idname, text="÷")
            row.operator(CALC_OT_Input_lp.bl_idname, text="(")
            row.operator(CALC_OT_Input_rp.bl_idname, text=")")
            col = _row.column()
            col.scale_x = 1.33 #XXX: I don't know where this comes from...
            row = col.row(align=True)
            row.operator(CALC_OT_Input_sinh.bl_idname, text="sinh")
            row.operator(CALC_OT_Input_cosh.bl_idname, text="cosh")
            row.operator(CALC_OT_Input_tanh.bl_idname, text="tanh")
            _row = layout.row(align=True)
            col = _row.column()
            row = col.row(align=True)
            row.operator(CALC_OT_Input_4.bl_idname, text="4")
            row.operator(CALC_OT_Input_5.bl_idname, text="5")
            row.operator(CALC_OT_Input_6.bl_idname, text="6")
            row.operator(CALC_OT_Input_mul.bl_idname, text="×")
            col = _row.column()
            col.scale_x = 1.44 #XXX: I don't know where this comes from...
            col.menu(CALC_MT_Variables.bl_idname, text="x")
            col = _row.column()
            row = col.row(align=True)
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
            _row = layout.row(align=True)
            col = _row.column()
            row = col.row(align=True)
            row.operator(CALC_OT_Input_0.bl_idname, text="0")
            row.operator(CALC_OT_Input_dot.bl_idname, text=".")
            row.operator(CALC_OT_Input_imag.bl_idname, text="i")
            row.operator(CALC_OT_Input_plus.bl_idname, text="+")
            col = _row.column()
            col.enabled = not scene.calc_is_live
            col.scale_x = 1.42 #XXX: I don't know where this comes from...
            col.operator(CALC_OT_Input_equal.bl_idname, text="=")
            col = _row.column()
            row = col.row(align=True)
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

    # area, space, and region have no custom properties...
    screen = bpy.types.Screen
    screen.is_calc_screen = BoolProperty(name="Is Calculator Screen")

def clear_props():
    scene = bpy.types.Scene
    screen = bpy.types.Screen
    if hasattr(scene, "calc_exp"):
        del scene.calc_exp
    if hasattr(scene, "calc_hist"):
        del scene.calc_hist
    if hasattr(scene, "active_calc_hist_index"):
        del scene.active_calc_hist_index
    if hasattr(scene, "calc_vars"):
        del scene.calc_vars
    if hasattr(scene, "active_calc_vars_index"):
        del scene.active_calc_vars_index
    if hasattr(scene, "calc_funcs"):
        del scene.calc_funcs
    if hasattr(scene, "active_calc_funcs_index"):
        del scene.active_calc_funcs_index
    if hasattr(scene, "calc_mode"):
        del scene.calc_mode
    if hasattr(scene, "calc_is_live"):
        del scene.calc_is_live
    if hasattr(scene, "calc_is_inited"):
        del scene.calc_is_inited
    if hasattr(screen, "is_calc_screen"):
        del screen.is_calc_screen

def calc_inner_poll(self, context, pref_cls):
    if context.screen.is_calc_screen == True:
        return False

    if hasattr(pref_cls, "poll"):
        return pref_cls.poll(context)

    return True

def perf_overrides():
    import os, sys
    p = os.path.join(bpy.utils.system_resource('SCRIPTS'), 'startup', 'bl_ui')

    if p not in sys.path:
        sys.path.append(p)

    import importlib
    perf_mod = importlib.import_module("space_userpref")

    def calc_pref_override(cls_name, orig_cls):
        return type(cls_name, (orig_cls, bpy.types.Panel), {
            "poll": classmethod(lambda self, context: calc_inner_poll(self, context, orig_cls) ),
        })

    for perf_cls in perf_mod.classes:
        if bpy.types.Panel in perf_cls.__mro__:# and hasattr(perf_cls, "bl_context"):
            exec(perf_cls.__name__ + ' = calc_pref_override("' + perf_cls.__name__ + '", perf_cls)')
            exec("bpy.utils.register_class(" + perf_cls.__name__ + ")")


class CALC_PT_PrefPanel(bpy.types.Panel):
    bl_label = "Calculator"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_category = "Calculator"
    bl_context = ""
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        if context.screen.is_calc_screen == True:
            return True
        return False

#    def draw_header(self, context):
#        layout = self.layout
#        layout.label(text="", icon='PLUGIN')

    def draw(self, context):
        CALC_PT_CustomPanel.draw(self, context)

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
    CALC_OT_Input_sub0,
    CALC_OT_Input_sub1,
    CALC_OT_Input_sub2,
    CALC_OT_Input_sub3,
    CALC_OT_Input_sub4,
    CALC_OT_Input_sub5,
    CALC_OT_Input_sub6,
    CALC_OT_Input_sub7,
    CALC_OT_Input_sub8,
    CALC_OT_Input_sub9,
    CALC_OT_Input_super0,
    CALC_OT_Input_super1,
    CALC_OT_Input_super2,
    CALC_OT_Input_super3,
    CALC_OT_Input_super4,
    CALC_OT_Input_super5,
    CALC_OT_Input_super6,
    CALC_OT_Input_super7,
    CALC_OT_Input_super8,
    CALC_OT_Input_super9,
    CALC_OT_Input_a,
    CALC_OT_Input_b,
    CALC_OT_Input_c,
    CALC_OT_Input_d,
    CALC_OT_Input_e,
    CALC_OT_Input_f,
    CALC_OT_Input_g,
    CALC_OT_Input_h,
    CALC_OT_Input_i,
    CALC_OT_Input_j,
    CALC_OT_Input_k,
    CALC_OT_Input_l,
    CALC_OT_Input_m,
    CALC_OT_Input_n,
    CALC_OT_Input_o,
    CALC_OT_Input_p,
    CALC_OT_Input_q,
    CALC_OT_Input_r,
    CALC_OT_Input_s,
    CALC_OT_Input_t,
    CALC_OT_Input_u,
    CALC_OT_Input_v,
    CALC_OT_Input_w,
    CALC_OT_Input_x,
    CALC_OT_Input_y,
    CALC_OT_Input_z,
    CALC_OT_Input_A,
    CALC_OT_Input_B,
    CALC_OT_Input_C,
    CALC_OT_Input_D,
    CALC_OT_Input_E,
    CALC_OT_Input_F,
    CALC_OT_Input_G,
    CALC_OT_Input_H,
    CALC_OT_Input_I,
    CALC_OT_Input_J,
    CALC_OT_Input_K,
    CALC_OT_Input_L,
    CALC_OT_Input_M,
    CALC_OT_Input_N,
    CALC_OT_Input_O,
    CALC_OT_Input_P,
    CALC_OT_Input_Q,
    CALC_OT_Input_R,
    CALC_OT_Input_S,
    CALC_OT_Input_T,
    CALC_OT_Input_U,
    CALC_OT_Input_V,
    CALC_OT_Input_W,
    CALC_OT_Input_X,
    CALC_OT_Input_Y,
    CALC_OT_Input_Z,
    CALC_OT_Input_underbar,
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
    CALC_OT_Input_sexp,
    CALC_OT_Input_equal,
    CALC_OT_Input_backspace,
    CALC_PT_PrefPanel,
]

addon_keymaps = []

def calc_prefmenu(self, context):
    layout = self.layout
    screen = context.screen
    layout.prop(screen, "is_calc_screen")

def register():
    for c in classes:
        bpy.utils.register_class(c)
    perf_overrides()
    init_props()
    try:
        bpy.app.translations.register("blender_calculator", translation_dict)
    except: pass

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if not kc:
        return
#    km = wm.keyconfigs.addon.keymaps.new(name='Preferences', space_type='PREFERENCES')
#    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D', region_type="UI")
#    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    km = wm.keyconfigs.addon.keymaps.new(name='Window')
    kmi = km.keymap_items.new(CALC_OT_Input_0.bl_idname, type='ZERO', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_1.bl_idname, type='ONE', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_2.bl_idname, type='TWO', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_3.bl_idname, type='THREE', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_4.bl_idname, type='FOUR', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_5.bl_idname, type='FIVE', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_6.bl_idname, type='SIX', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_7.bl_idname, type='SEVEN', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_8.bl_idname, type='EIGHT', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_9.bl_idname, type='NINE', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_dot.bl_idname, type='PERIOD', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_dot.bl_idname, type='COMMA', value='PRESS') # for europe
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_percent.bl_idname, type='FIVE', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_div.bl_idname, type='SLASH', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_minus.bl_idname, type='MINUS', value='PRESS')
    addon_keymaps.append((km, kmi))

# XXX: mul: shift+colon in jis keyboard, shift+8 in us
#      NO WAY TO ADD THIS SHORTCUT IN JIS KEYBOARD!!!
#    kmi = km.keymap_items.new(CALC_OT_Input_mul.bl_idname, type='EIGHT', shift=True, value='PRESS') # us
#    addon_keymaps.append((km, kmi))

#    kmi = km.keymap_items.new(CALC_OT_Input_plus.bl_idname, type='SEMI_COLON', shift=True, value='PRESS') #jis (not working)
#    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_plus.bl_idname, type='PLUS', shift=True, value='PRESS') #jis (hmm...)
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(CALC_OT_Input_lp.bl_idname, type='EIGHT', shift=True, value='PRESS') # jis
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_rp.bl_idname, type='NINE', shift=True, value='PRESS') # jis
    addon_keymaps.append((km, kmi))

#    kmi = km.keymap_items.new(CALC_OT_Input_equal.bl_idname, type='MINUS', shift=True, value='PRESS') #jis (not working)
#    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_equal.bl_idname, type='EQUAL', shift=True, value='PRESS') #jis (hmm...)
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(CALC_OT_Input_equal.bl_idname, type='RET', value='PRESS')
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(CALC_OT_Input_sq.bl_idname, type='TWO', ctrl=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_sqrt.bl_idname, type='R', ctrl=True, value='PRESS')
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(CALC_OT_ExpClear.bl_idname, type='ESC', value='PRESS')
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(CALC_OT_Input_sexp.bl_idname, type='E', ctrl=True, value='PRESS')
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(CALC_OT_Input_inv.bl_idname, type='I', ctrl=True, value='PRESS')
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(CALC_OT_Input_factorial.bl_idname, type='ONE', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(CALC_OT_Input_abs.bl_idname, type='BACK_SLASH', shift=True, value='PRESS') # jis
    addon_keymaps.append((km, kmi))

    # CALC_OT_Input_pow -> ^ @jis, shift+6 @us

    kmi = km.keymap_items.new(CALC_OT_Input_pi.bl_idname, type='P', ctrl=True, value='PRESS')
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(CALC_OT_Input_sub0.bl_idname, type='ZERO', alt=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_sub1.bl_idname, type='ONE', alt=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_sub2.bl_idname, type='TWO', alt=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_sub3.bl_idname, type='THREE', alt=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_sub4.bl_idname, type='FOUR', alt=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_sub5.bl_idname, type='FIVE', alt=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_sub6.bl_idname, type='SIX', alt=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_sub7.bl_idname, type='SEVEN', alt=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_sub8.bl_idname, type='EIGHT', alt=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_sub9.bl_idname, type='NINE', alt=True, value='PRESS')
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(CALC_OT_Input_super0.bl_idname, type='ZERO', ctrl=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_super1.bl_idname, type='ONE', ctrl=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_super2.bl_idname, type='TWO', ctrl=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_super3.bl_idname, type='THREE', ctrl=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_super4.bl_idname, type='FOUR', ctrl=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_super5.bl_idname, type='FIVE', ctrl=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_super6.bl_idname, type='SIX', ctrl=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_super7.bl_idname, type='SEVEN', ctrl=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_super8.bl_idname, type='EIGHT', ctrl=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_super9.bl_idname, type='NINE', ctrl=True, value='PRESS')
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(CALC_OT_Input_a.bl_idname, type='A', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_b.bl_idname, type='B', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_c.bl_idname, type='C', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_d.bl_idname, type='D', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_e.bl_idname, type='E', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_f.bl_idname, type='F', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_g.bl_idname, type='G', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_h.bl_idname, type='H', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_i.bl_idname, type='I', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_j.bl_idname, type='J', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_k.bl_idname, type='K', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_l.bl_idname, type='L', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_m.bl_idname, type='M', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_n.bl_idname, type='N', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_o.bl_idname, type='O', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_p.bl_idname, type='P', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_q.bl_idname, type='Q', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_r.bl_idname, type='R', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_s.bl_idname, type='S', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_t.bl_idname, type='T', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_u.bl_idname, type='U', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_v.bl_idname, type='V', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_w.bl_idname, type='W', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_x.bl_idname, type='X', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_y.bl_idname, type='Y', value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_z.bl_idname, type='Z', value='PRESS')
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(CALC_OT_Input_A.bl_idname, type='A', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_B.bl_idname, type='B', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_C.bl_idname, type='C', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_D.bl_idname, type='D', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_E.bl_idname, type='E', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_F.bl_idname, type='F', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_G.bl_idname, type='G', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_H.bl_idname, type='H', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_I.bl_idname, type='I', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_J.bl_idname, type='J', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_K.bl_idname, type='K', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_L.bl_idname, type='L', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_M.bl_idname, type='M', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_N.bl_idname, type='N', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_O.bl_idname, type='O', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_P.bl_idname, type='P', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_Q.bl_idname, type='Q', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_R.bl_idname, type='R', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_S.bl_idname, type='S', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_T.bl_idname, type='T', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_U.bl_idname, type='U', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_V.bl_idname, type='V', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_W.bl_idname, type='W', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_X.bl_idname, type='X', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_Y.bl_idname, type='Y', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(CALC_OT_Input_Z.bl_idname, type='Z', shift=True, value='PRESS')
    addon_keymaps.append((km, kmi))

#   conflict with "|"
#    kmi = km.keymap_items.new(CALC_OT_Input_underbar.bl_idname, type='BACK_SLASH', shift=True, value='PRESS') # jis
#    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(CALC_OT_Input_backspace.bl_idname, type='BACK_SPACE', value='PRESS', repeat=True)
    addon_keymaps.append((km, kmi))
    # TODO: del / left / right

    bpy.types.USERPREF_MT_view.append(calc_prefmenu)

def unregister():
    try:
        bpy.types.USERPREF_MT_view.remove(calc_prefmenu)
    except: pass

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    clear_props()
    for c in classes:
        bpy.utils.unregister_class(c)
    try:
        bpy.app.translations.unregister("blender_calculator")
    except: pass



if __name__ == "__main__":
    register()

