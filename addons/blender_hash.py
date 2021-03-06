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
# Hash Addon for Blender
#
# Copyright (C) 2022 Toshimitsu Kimura <lovesyao@gmail.com>
#
# Note: The UI is heavily inspired from GtkHash
# TODO: File List support

import bpy
from bpy.props import (
    BoolProperty,
    StringProperty,
    EnumProperty,
)

bl_info = {
    "name": "Hash",
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
        ("*", "Hash"): "ハッシュ",

        ("*", "Show MD5 Hash"): "MD5 ハッシュを表示",
        ("*", "Show SHA1 Hash"): "SHA1 ハッシュを表示",
        ("*", "Show SHA224 Hash"): "SHA224 ハッシュを表示",
        ("*", "Show SHA256 Hash"): "SHA256 ハッシュを表示",
        ("*", "Show SHA384 Hash"): "SHA384 ハッシュを表示",
        ("*", "Show SHA512 Hash"): "SHA512 ハッシュを表示",
        ("*", "Show SHA3_224 Hash"): "SHA3_224 ハッシュを表示",
        ("*", "Show SHA3_256 Hash"): "SHA3_256 ハッシュを表示",
        ("*", "Show SHA3_384 Hash"): "SHA3_384 ハッシュを表示",
        ("*", "Show SHA3_512 Hash"): "SHA3_512 ハッシュを表示",
        ("*", "Show Blake2b Hash"): "Blake2b ハッシュを表示",
        ("*", "Show Blake2s Hash"): "Blake2s ハッシュを表示",
#        ("*", "Show Shake_128 Hash"): "Shake_128 ハッシュを表示",
#        ("*", "Show Shake_256 Hash"): "Shake_256 ハッシュを表示",
        ("*", "Show CRC32 Hash"): "CRC32 ハッシュを表示",
        ("*", "Show Adler32 Hash"): "Adler32 ハッシュを表示",

        ("*", "Digest Format"): "ダイジェスト形式",
        ("*", "Lowercase Hexadecimal"): "小文字16進数",
        ("*", "Uppercase Hexadecimal"): "大文字16進数",

        ("*", "Input:"): "入力:",
        ("*", "Calculated:"): "結果:",
        ("*", "Check"): "チェック",

        ("*", "Calculated MD5 Hash"): "算出した MD5 ハッシュ",
        ("*", "Calculated SHA1 Hash"): "算出した SHA1 ハッシュ",
        ("*", "Calculated SHA224 Hash"): "算出した SHA224 ハッシュ",
        ("*", "Calculated SHA256 Hash"): "算出した SHA256 ハッシュ",
        ("*", "Calculated SHA384 Hash"): "算出した SHA384 ハッシュ",
        ("*", "Calculated SHA512 Hash"): "算出した SHA512 ハッシュ",
        ("*", "Calculated SHA3_224 Hash"): "算出した SHA3_224 ハッシュ",
        ("*", "Calculated SHA3_256 Hash"): "算出した SHA3_256 ハッシュ",
        ("*", "Calculated SHA3_384 Hash"): "算出した SHA3_384 ハッシュ",
        ("*", "Calculated SHA3_512 Hash"): "算出した SHA3_512 ハッシュ",
        ("*", "Calculated Blake2b Hash"): "算出した Blake2b ハッシュ",
        ("*", "Calculated Blake2s Hash"): "算出した Blake2s ハッシュ",
#        ("*", "Calculated Shake_128 Hash"): "算出した Shake_128 ハッシュ",
#        ("*", "Calculated Shake_256 Hash"): "算出した Shake_256 ハッシュ",
        ("*", "Calculated CRC32 Hash"): "算出した CRC32 ハッシュ",
        ("*", "Calculated Adler32 Hash"): "算出した Adler32 ハッシュ",
    }
}

class HASH_MT_Default(bpy.types.Menu):
    bl_idname="HASH_MT_default"
    bl_label="Menu"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "show_hash_md5")
        layout.prop(scene, "show_hash_sha1")
        layout.prop(scene, "show_hash_sha224")
        layout.prop(scene, "show_hash_sha256")
        layout.prop(scene, "show_hash_sha384")
        layout.prop(scene, "show_hash_sha512")
        layout.prop(scene, "show_hash_sha3_224")
        layout.prop(scene, "show_hash_sha3_256")
        layout.prop(scene, "show_hash_sha3_384")
        layout.prop(scene, "show_hash_sha3_512")
        layout.prop(scene, "show_hash_blake2b")
        layout.prop(scene, "show_hash_blake2s")
#        layout.prop(scene, "show_hash_shake_128")
#        layout.prop(scene, "show_hash_shake_256")
        layout.prop(scene, "show_hash_crc32")
        layout.prop(scene, "show_hash_adler32")

        layout.separator()
        layout.prop(scene, "hash_digest_format")

class HASH_PT_CustomPanel(bpy.types.Panel):

    bl_label = "Hash"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Hash"
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

        layout.menu(HASH_MT_Default.bl_idname)

        layout.label(text="Input:")
        layout.prop(scene, "hash_input_type")
        if scene.hash_input_type == "TEXT":
            layout.prop(scene, "hash_base_text", text="Text")
        else:
            layout.prop(scene, "hash_base_file", text="File")
        layout.prop(scene, "hash_check_text", text="Check")

        layout.prop(scene, "hash_is_hmac", text="HMAC")
        row = layout.row()
        row.enabled = scene.hash_is_hmac
        row.prop(scene, "hash_hmac_salt", text="Key")

        prefix = ""
        if scene.hash_is_hmac:
            prefix = "HMAC-"

        layout.label(text="Calculated:")
        if scene.show_hash_md5:
            layout.prop(scene, "hash_calculated_md5", text=prefix+"MD5",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_md5 else "NONE")
        if scene.show_hash_sha1:
            layout.prop(scene, "hash_calculated_sha1", text=prefix+"SHA1",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_sha1 else "NONE")
        if scene.show_hash_sha224:
            layout.prop(scene, "hash_calculated_sha224", text=prefix+"SHA224",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_sha224 else "NONE")
        if scene.show_hash_sha256:
            layout.prop(scene, "hash_calculated_sha256", text=prefix+"SHA256",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_sha256 else "NONE")
        if scene.show_hash_sha384:
            layout.prop(scene, "hash_calculated_sha384", text=prefix+"SHA384",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_sha384 else "NONE")
        if scene.show_hash_sha512:
            layout.prop(scene, "hash_calculated_sha512", text=prefix+"SHA512",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_sha512 else "NONE")
        if scene.show_hash_sha3_224:
            layout.prop(scene, "hash_calculated_sha3_224", text=prefix+"SHA3_224",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_sha3_224 else "NONE")
        if scene.show_hash_sha3_256:
            layout.prop(scene, "hash_calculated_sha3_256", text=prefix+"SHA3_256",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_sha3_256 else "NONE")
        if scene.show_hash_sha3_384:
            layout.prop(scene, "hash_calculated_sha3_384", text=prefix+"SHA3_384",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_sha3_384 else "NONE")
        if scene.show_hash_sha3_512:
            layout.prop(scene, "hash_calculated_sha3_512", text=prefix+"SHA3_512",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_sha3_512 else "NONE")
        if scene.show_hash_blake2b:
            layout.prop(scene, "hash_calculated_blake2b", text=prefix+"Blake2b",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_blake2b else "NONE")
        if scene.show_hash_blake2s:
            layout.prop(scene, "hash_calculated_blake2s", text=prefix+"Blake2s",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_blake2s else "NONE")
#        if scene.show_hash_shake_128:
#            layout.prop(scene, "hash_calculated_shake_128", text=prefix+"Shake_128",
#                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_shake_128 else "NONE")
#        if scene.show_hash_shake_256:
#            layout.prop(scene, "hash_calculated_shake_256", text=prefix+"Shake_256",
#                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_shake_256 else "NONE")
        if scene.show_hash_crc32:
            layout.prop(scene, "hash_calculated_crc32", text="CRC32",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_crc32 else "NONE")
        if scene.show_hash_adler32:
            layout.prop(scene, "hash_calculated_adler32", text="Adler32",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_adler32 else "NONE")

from hashlib import md5, sha1, sha224, sha256, sha384, sha512, sha3_224, sha3_256, sha3_384, sha3_512, blake2b, blake2s #, shake_128, shake_256
import hmac
from binascii import crc32
from zlib import adler32
from base64 import b64encode

def hex_to_format(self, hex_val):
    return hex_val if self.hash_digest_format == "LOWERCASE" else \
           hex_val.upper() if self.hash_digest_format == "UPPERCASE" else \
           b64encode(bytes.fromhex(hex_val)).decode('utf-8')

def hash_calc(self, bin, func):
    return func(bin).hexdigest() if not self.hash_is_hmac else \
           hmac.new(self.hash_hmac_salt.encode(), bin, func).hexdigest()

def hash_reset(self):
    self["hash_calculated_md5"] = \
    self["hash_calculated_sha1"] = \
    self["hash_calculated_sha224"] = \
    self["hash_calculated_sha256"] = \
    self["hash_calculated_sha384"] = \
    self["hash_calculated_sha512"] = \
    self["hash_calculated_sha3_224"] = \
    self["hash_calculated_sha3_256"] = \
    self["hash_calculated_sha3_384"] = \
    self["hash_calculated_sha3_512"] = \
    self["hash_calculated_blake2b"] = \
    self["hash_calculated_blake2s"] = \
    self["hash_calculated_crc32"] = \
    self["hash_calculated_adler32"] = ""

import os
def hash_update(self, context):
    hash_reset(self)
    if self.hash_input_type == "TEXT":
        bin = self.hash_base_text.encode()
    else:
        p = bpy.path.abspath(self.hash_base_file)
        if not os.path.exists(p):
            return
        bin = open(p, "rb").read()
    if self.show_hash_md5:
        self["hash_calculated_md5"] = hex_to_format(self, hash_calc(self, bin, md5))
    if self.show_hash_sha1:
        self["hash_calculated_sha1"] = hex_to_format(self, hash_calc(self, bin, sha1))
    if self.show_hash_sha224:
        self["hash_calculated_sha224"] = hex_to_format(self, hash_calc(self, bin, sha224))
    if self.show_hash_sha256:
        self["hash_calculated_sha256"] = hex_to_format(self, hash_calc(self, bin, sha256))
    if self.show_hash_sha256:
        self["hash_calculated_sha384"] = hex_to_format(self, hash_calc(self, bin, sha384))
    if self.show_hash_sha512:
        self["hash_calculated_sha512"] = hex_to_format(self, hash_calc(self, bin, sha512))
    if self.show_hash_sha3_224:
        self["hash_calculated_sha3_224"] = hex_to_format(self, hash_calc(self, bin, sha3_224))
    if self.show_hash_sha3_256:
        self["hash_calculated_sha3_256"] = hex_to_format(self, hash_calc(self, bin, sha3_256))
    if self.show_hash_sha3_384:
        self["hash_calculated_sha3_384"] = hex_to_format(self, hash_calc(self, bin, sha3_384))
    if self.show_hash_sha3_512:
        self["hash_calculated_sha3_512"] = hex_to_format(self, hash_calc(self, bin, sha3_512))
    if self.show_hash_blake2b:
        self["hash_calculated_blake2b"] = hex_to_format(self, hash_calc(self, bin, blake2b))
    if self.show_hash_blake2s:
        self["hash_calculated_blake2s"] = hex_to_format(self, hash_calc(self, bin, blake2s))
#    if self.show_hash_shake_128:
#        self["hash_calculated_shake_128"] = hex_to_format(self, hash_calc(self, bin, shake_128)) # length?
#    if self.show_hash_shake_256:
#        self["hash_calculated_shake_256"] = hex_to_format(self, hash_calc(self, bin, shake_256)) # length?
    if self.show_hash_crc32:
        self["hash_calculated_crc32"] = hex_to_format(self, format(crc32(bin), "08x"))
    if self.show_hash_adler32:
        self["hash_calculated_adler32"] = hex_to_format(self, format(adler32(bin), "08x"))

def init_props():
    scene = bpy.types.Scene
    screen = bpy.types.Screen

    scene.hash_input_type = EnumProperty(
        name="Input Type",
        description="The type of input for hashing",
        items=[
            ('FILE', "File", "File"),
            ('TEXT', "Text", "Text"),
#            ('FILELIST', "File List", "File List"),
        ],
        default='FILE',
        update=hash_update
    )

    scene.hash_base_text = StringProperty(name="Text for Hashing", 
                                          default="",
                                          update=hash_update)
    scene.hash_base_file = StringProperty(name="File for Hashing",
                                          subtype="FILE_PATH",
                                          default="",
                                          update=hash_update)

    scene.hash_check_text = StringProperty(name="Hash for Checking", 
                                          default="")

    scene.hash_is_hmac = BoolProperty(name="Is HMAC", 
                                      default=False,
                                      update=hash_update)
    scene.hash_hmac_salt = StringProperty(name="Salt", 
                                          default="",
                                          update=hash_update)

    # hashlib.algorithms_guaranteed
    scene.hash_calculated_md5 = StringProperty(name="Calculated MD5 Hash", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_md5"]
                                                    if "hash_calculated_md5" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_sha1 = StringProperty(name="Calculated SHA1 Hash", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_sha1"]
                                                    if "hash_calculated_sha1" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_sha224 = StringProperty(name="Calculated SHA224 Hash", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_sha224"]
                                                    if "hash_calculated_sha224" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_sha256 = StringProperty(name="Calculated SHA256 Hash", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_sha256"]
                                                    if "hash_calculated_sha256" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_sha384 = StringProperty(name="Calculated SHA384 Hash", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_sha384"]
                                                    if "hash_calculated_sha384" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_sha512 = StringProperty(name="Calculated SHA512 Hash", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_sha512"]
                                                    if "hash_calculated_sha512" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_sha3_224 = StringProperty(name="Calculated SHA3_224 Hash", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_sha3_224"]
                                                    if "hash_calculated_sha3_224" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_sha3_256 = StringProperty(name="Calculated SHA3_256 Hash", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_sha3_256"]
                                                    if "hash_calculated_sha3_256" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_sha3_384 = StringProperty(name="Calculated SHA3_384 Hash", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_sha3_384"]
                                                    if "hash_calculated_sha3_384" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_sha3_512 = StringProperty(name="Calculated SHA3_512 Hash", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_sha3_512"]
                                                    if "hash_calculated_sha3_512" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_blake2b = StringProperty(name="Calculated Blake2b Hash", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_blake2b"]
                                                    if "hash_calculated_blake2b" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_blake2s = StringProperty(name="Calculated Blake2s Hash", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_blake2s"]
                                                    if "hash_calculated_blake2s" in t else "",
                                                set=lambda t, v: None)
#    scene.hash_calculated_shake_128 = StringProperty(name="Calculated Shake_128 Hash", 
#                                                default="", 
#                                                get=lambda t: t["hash_calculated_shake_128"]
#                                                    if "hash_calculated_shake_128" in t else "",
#                                                set=lambda t, v: None)
#    scene.hash_calculated_shake_256 = StringProperty(name="Calculated Shake_256 Hash", 
#                                                default="", 
#                                                get=lambda t: t["hash_calculated_shake_256"]
#                                                    if "hash_calculated_shake_256" in t else "",
#                                                set=lambda t, v: None)
    scene.hash_calculated_crc32 = StringProperty(name="Calculated CRC32 Hash", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_crc32"]
                                                    if "hash_calculated_crc32" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_adler32 = StringProperty(name="Calculated Adler32 Hash", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_adler32"]
                                                    if "hash_calculated_adler32" in t else "",
                                                set=lambda t, v: None)

    scene.show_hash_md5 = BoolProperty(name="Show MD5 Hash", 
                                        default=True,
                                        update=hash_update)
    scene.show_hash_sha1 = BoolProperty(name="Show SHA1 Hash", 
                                        default=True,
                                        update=hash_update)
    scene.show_hash_sha224 = BoolProperty(name="Show SHA224 Hash", 
                                        default=False,
                                        update=hash_update)
    scene.show_hash_sha256 = BoolProperty(name="Show SHA256 Hash", 
                                        default=True,
                                        update=hash_update)
    scene.show_hash_sha384 = BoolProperty(name="Show SHA384 Hash", 
                                        default=False,
                                        update=hash_update)
    scene.show_hash_sha512 = BoolProperty(name="Show SHA512 Hash", 
                                        default=False,
                                        update=hash_update)
    scene.show_hash_sha3_224 = BoolProperty(name="Show SHA3_224 Hash", 
                                        default=False,
                                        update=hash_update)
    scene.show_hash_sha3_256 = BoolProperty(name="Show SHA3_256 Hash", 
                                        default=False,
                                        update=hash_update)
    scene.show_hash_sha3_384 = BoolProperty(name="Show SHA3_384 Hash", 
                                        default=False,
                                        update=hash_update)
    scene.show_hash_sha3_512 = BoolProperty(name="Show SHA3_512 Hash", 
                                        default=False,
                                        update=hash_update)
    scene.show_hash_blake2b = BoolProperty(name="Show Blake2b Hash", 
                                        default=False,
                                        update=hash_update)
    scene.show_hash_blake2s = BoolProperty(name="Show Blake2s Hash", 
                                        default=False,
                                        update=hash_update)
#    scene.show_hash_shake_128 = BoolProperty(name="Show Shake_128 Hash", 
#                                        default=False,
#                                        update=hash_update)
#    scene.show_hash_shake_256 = BoolProperty(name="Show Shake_256 Hash", 
#                                        default=False,
#                                        update=hash_update)
    scene.show_hash_crc32 = BoolProperty(name="Show CRC32 Hash", 
                                        default=True,
                                        update=hash_update)
    scene.show_hash_adler32 = BoolProperty(name="Show Adler32 Hash", 
                                        default=False,
                                        update=hash_update)

    scene.hash_digest_format = EnumProperty(
        name="Digest Format",
        description="The string format of the calculated digest",
        items=[
            ('LOWERCASE', "Lowercase Hexadecimal", "Lowercase Hexadecimal"),
            ('UPPERCASE', "Uppercase Hexadecimal", "Uppercase Hexadecimal"),
            ('BASE64', "Base64", "Base64"),
        ],
        default='LOWERCASE',
        update=hash_update
    )


class HASH_PT_PrefPanel(bpy.types.Panel):
    bl_label = "Hash"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_category = "Hash"
    bl_context = ""
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        if context.screen.pref_space_type == "HASH":
            return True
        return False

#    def draw_header(self, context):
#        layout = self.layout
#        layout.label(text="", icon='PLUGIN')

    def draw(self, context):
        HASH_PT_CustomPanel.draw(self, context)

def clear_props():
    scene = bpy.types.Scene
    screen = bpy.types.Screen
    del scene.hash_input_type
    del scene.hash_base_text
    del scene.hash_check_text
    del scene.hash_is_hmac
    del scene.hash_hmac_salt

    del scene.hash_calculated_md5
    del scene.hash_calculated_sha1
    del scene.hash_calculated_sha224
    del scene.hash_calculated_sha256
    del scene.hash_calculated_sha384
    del scene.hash_calculated_sha512
    del scene.hash_calculated_sha3_224
    del scene.hash_calculated_sha3_256
    del scene.hash_calculated_sha3_384
    del scene.hash_calculated_sha3_512
    del scene.hash_calculated_blake2b
    del scene.hash_calculated_blake2s
#    del scene.hash_calculated_shake_128
#    del scene.hash_calculated_shake_256
    del scene.hash_calculated_crc32
    del scene.hash_calculated_adler32

    del scene.show_hash_md5
    del scene.show_hash_sha1
    del scene.show_hash_sha224
    del scene.show_hash_sha256
    del scene.show_hash_sha384
    del scene.show_hash_sha512
    del scene.show_hash_sha3_224
    del scene.show_hash_sha3_256
    del scene.show_hash_sha3_384
    del scene.show_hash_sha3_512
    del scene.show_hash_blake2b
    del scene.show_hash_blake2s
#    del scene.show_hash_shake_128
#    del scene.show_hash_shake_256
    del scene.show_hash_crc32
    del scene.show_hash_adler32

    del scene.hash_digest_format

classes = [
    HASH_PT_CustomPanel,
    HASH_MT_Default,
    HASH_PT_PrefPanel,
]

from blender_perf_overrides import perfoverride_register, perfoverride_unregister

def register():
    for c in classes:
        bpy.utils.register_class(c)
    perfoverride_register("HASH", "Hash")
    init_props()
    try:
        bpy.app.translations.register("blender_hash", translation_dict)
    except: pass

def unregister():
    perfoverride_unregister("HASH", "Hash")
    clear_props()
    for c in classes:
        bpy.utils.unregister_class(c)
    try:
        bpy.app.translations.unregister("blender_hash")
    except: pass

if __name__ == "__main__":
    register()
