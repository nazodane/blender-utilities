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
# Perferences space override helper for Blender
#
# Copyright (C) 2022 Toshimitsu Kimura <lovesyao@gmail.com>

import bpy
from bpy.props import (
    StringProperty,
    CollectionProperty,
    EnumProperty,
)

def _perfoverride_menu(self, context):
    layout = self.layout
    screen = context.screen
#    layout.prop(screen, "pref_space_type") # XXX: why enum value is slightly wrong?

def _perfoverride_inner_poll(self, context, pref_cls):
    if hasattr(context.screen, "pref_space_type") and \
       not context.screen.pref_space_type == "Preferences":
        return False

    if hasattr(pref_cls, "poll"):
        return pref_cls.poll(context)

    return True

def _perfoverride_overrides():
    import os, sys
    p = os.path.join(bpy.utils.system_resource('SCRIPTS'), 'startup', 'bl_ui')

    if p not in sys.path:
        sys.path.append(p)

    import importlib
    perf_mod = importlib.import_module("space_userpref")

    def pref_override(cls_name, orig_cls):
        return type(cls_name, (orig_cls, bpy.types.Panel), {
            "poll": classmethod(lambda self, context: _perfoverride_inner_poll(self, context, orig_cls) ),
        })

    for perf_cls in perf_mod.classes:
        if bpy.types.Panel in perf_cls.__mro__:# and hasattr(perf_cls, "bl_context"):
            exec(perf_cls.__name__ + ' = pref_override("' + perf_cls.__name__ + '", perf_cls)')
            exec("bpy.utils.register_class(" + perf_cls.__name__ + ")")

import binascii
def _perfoverride_type_name2enum_item(space_type_id, space_type_name):
    return (space_type_id, space_type_name, space_type_name + " in Preferences spaces", \
            binascii.crc32(space_type_id.encode()))

def _perfoverride_pref_space_type_update(items):
    screen = bpy.types.Screen
    screen.pref_space_type = EnumProperty(name="Preferences space type", \
                                          items=items, default="Preferences")

def perfoverride_register(new_space_type_id, new_space_type_name):
    screen = bpy.types.Screen

    pref_enum_item = _perfoverride_type_name2enum_item(new_space_type_id, new_space_type_name)

    if hasattr(screen, "pref_space_type"):
        screen.pref_space_type.keywords["items"].add(pref_enum_item)
        _perfoverride_pref_space_type_update(screen.pref_space_type.keywords["items"])
#        print("registerXX: ")
#        print(screen.pref_space_type.keywords["items"])
        return

    # area, space, and region have no custom properties...
    _perfoverride_pref_space_type_update({("Preferences", "Preferences", "Preferences in Preferences spaces", 0), \
                                           pref_enum_item})
#    print("register: ")
#    print(screen.pref_space_type.keywords["items"])

    _perfoverride_overrides()
    bpy.types.USERPREF_MT_view.append(_perfoverride_menu)

def perfoverride_unregister(old_space_type_id, old_space_type_name):
    screen = bpy.types.Screen

    pref_enum_item = _perfoverride_type_name2enum_item(old_space_type_id, old_space_type_name)
    if not hasattr(screen, "pref_space_type"):
        return

    params = screen.pref_space_type.keywords
    if pref_enum_item in params["items"]:
        params["items"].remove(pref_enum_item)
        _perfoverride_pref_space_type_update(screen.pref_space_type.keywords["items"])

#    print("unregister: ")
#    print(params["items"])

    if len(params["items"]) > 1:
        return

    try:
        bpy.types.USERPREF_MT_view.remove(_perfoverride_menu)
    except: pass

    del screen.pref_space_type



