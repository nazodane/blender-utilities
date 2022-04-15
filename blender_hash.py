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
# TODO: HMAC support

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

        layout.label(text="Calculated:")
        if scene.show_hash_md5:
            layout.prop(scene, "hash_calculated_md5", text="MD5",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_md5 else "NONE")
        if scene.show_hash_sha1:
            layout.prop(scene, "hash_calculated_sha1", text="SHA1",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_sha1 else "NONE")
        if scene.show_hash_sha224:
            layout.prop(scene, "hash_calculated_sha224", text="SHA224",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_sha224 else "NONE")
        if scene.show_hash_sha256:
            layout.prop(scene, "hash_calculated_sha256", text="SHA256",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_sha256 else "NONE")
        if scene.show_hash_sha384:
            layout.prop(scene, "hash_calculated_sha384", text="SHA384",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_sha384 else "NONE")
        if scene.show_hash_sha512:
            layout.prop(scene, "hash_calculated_sha512", text="SHA512",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_sha512 else "NONE")
        if scene.show_hash_sha3_224:
            layout.prop(scene, "hash_calculated_sha3_224", text="SHA3_224",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_sha3_224 else "NONE")
        if scene.show_hash_sha3_256:
            layout.prop(scene, "hash_calculated_sha3_256", text="SHA3_256",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_sha3_256 else "NONE")
        if scene.show_hash_sha3_384:
            layout.prop(scene, "hash_calculated_sha3_384", text="SHA3_384",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_sha3_384 else "NONE")
        if scene.show_hash_sha3_512:
            layout.prop(scene, "hash_calculated_sha3_512", text="SHA3_512",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_sha3_512 else "NONE")
        if scene.show_hash_blake2b:
            layout.prop(scene, "hash_calculated_blake2b", text="Blake2b",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_blake2b else "NONE")
        if scene.show_hash_blake2s:
            layout.prop(scene, "hash_calculated_blake2s", text="Blake2s",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_blake2s else "NONE")
#        if scene.show_hash_shake_128:
#            layout.prop(scene, "hash_calculated_shake_128", text="Shake_128",
#                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_shake_128 else "NONE")
#        if scene.show_hash_shake_256:
#            layout.prop(scene, "hash_calculated_shake_256", text="Shake_256",
#                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_shake_256 else "NONE")
        if scene.show_hash_crc32:
            layout.prop(scene, "hash_calculated_crc32", text="CRC32",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_crc32 else "NONE")
        if scene.show_hash_adler32:
            layout.prop(scene, "hash_calculated_adler32", text="Adler32",
                        icon="CHECKMARK" if scene.hash_check_text == scene.hash_calculated_adler32 else "NONE")

from hashlib import md5, sha1, sha224, sha256, sha384, sha512, sha3_224, sha3_256, sha3_384, sha3_512, blake2b, blake2s #, shake_128, shake_256
# import hmac
from binascii import crc32
from zlib import adler32
from base64 import b64encode

def hex_to_format(self, hex_val):
    return hex_val if self.hash_digest_format == "LOWERCASE" else \
           hex_val.upper() if self.hash_digest_format == "UPPERCASE" else \
           b64encode(bytes.fromhex(hex_val)).decode('utf-8')

def hash_update(self, context):
    if self.hash_input_type == "TEXT":
        bin = self.hash_base_text.encode()
    else:
        bin = open(bpy.path.abspath(self.hash_base_file), "rb").read()
    self["hash_calculated_md5"] = hex_to_format(self, md5(bin).hexdigest())
    self["hash_calculated_sha1"] = hex_to_format(self, sha1(bin).hexdigest())
    self["hash_calculated_sha224"] = hex_to_format(self, sha224(bin).hexdigest())
    self["hash_calculated_sha256"] = hex_to_format(self, sha256(bin).hexdigest())
    self["hash_calculated_sha384"] = hex_to_format(self, sha384(bin).hexdigest())
    self["hash_calculated_sha512"] = hex_to_format(self, sha512(bin).hexdigest())
    self["hash_calculated_sha3_224"] = hex_to_format(self, sha3_224(bin).hexdigest())
    self["hash_calculated_sha3_256"] = hex_to_format(self, sha3_256(bin).hexdigest())
    self["hash_calculated_sha3_384"] = hex_to_format(self, sha3_384(bin).hexdigest())
    self["hash_calculated_sha3_512"] = hex_to_format(self, sha3_512(bin).hexdigest())
    self["hash_calculated_blake2b"] = hex_to_format(self, blake2b(bin).hexdigest())
    self["hash_calculated_blake2s"] = hex_to_format(self, blake2s(bin).hexdigest())
#    self["hash_calculated_shake_128"] = hex_to_format(self, shake_128(bin).hexdigest()) # length?
#    self["hash_calculated_shake_256"] = hex_to_format(self, shake_256(bin).hexdigest()) # length?
    self["hash_calculated_crc32"] = hex_to_format(self, format(crc32(bin), "08x"))
    self["hash_calculated_adler32"] = hex_to_format(self, format(adler32(bin), "08x"))

def init_props():
    scene = bpy.types.Scene

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

    # hashlib.algorithms_guaranteed
    scene.hash_calculated_md5 = StringProperty(name="Calculated MD5", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_md5"]
                                                    if "hash_calculated_md5" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_sha1 = StringProperty(name="Calculated SHA1", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_sha1"]
                                                    if "hash_calculated_sha1" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_sha224 = StringProperty(name="Calculated SHA224", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_sha224"]
                                                    if "hash_calculated_sha224" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_sha256 = StringProperty(name="Calculated SHA256", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_sha256"]
                                                    if "hash_calculated_sha256" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_sha384 = StringProperty(name="Calculated SHA384", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_sha384"]
                                                    if "hash_calculated_sha384" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_sha512 = StringProperty(name="Calculated SHA512", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_sha512"]
                                                    if "hash_calculated_sha512" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_sha3_224 = StringProperty(name="Calculated SHA3_224", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_sha3_224"]
                                                    if "hash_calculated_sha3_224" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_sha3_256 = StringProperty(name="Calculated SHA3_256", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_sha3_256"]
                                                    if "hash_calculated_sha3_256" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_sha3_384 = StringProperty(name="Calculated SHA3_384", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_sha3_384"]
                                                    if "hash_calculated_sha3_384" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_sha3_512 = StringProperty(name="Calculated SHA3_512", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_sha3_512"]
                                                    if "hash_calculated_sha3_512" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_blake2b = StringProperty(name="Calculated Blake2b", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_blake2b"]
                                                    if "hash_calculated_blake2b" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_blake2s = StringProperty(name="Calculated Blake2s", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_blake2s"]
                                                    if "hash_calculated_blake2s" in t else "",
                                                set=lambda t, v: None)
#    scene.hash_calculated_shake_128 = StringProperty(name="Calculated Shake_128", 
#                                                default="", 
#                                                get=lambda t: t["hash_calculated_shake_128"]
#                                                    if "hash_calculated_shake_128" in t else "",
#                                                set=lambda t, v: None)
#    scene.hash_calculated_shake_256 = StringProperty(name="Calculated Shake_256", 
#                                                default="", 
#                                                get=lambda t: t["hash_calculated_shake_256"]
#                                                    if "hash_calculated_shake_256" in t else "",
#                                                set=lambda t, v: None)
    scene.hash_calculated_crc32 = StringProperty(name="Calculated CRC32", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_crc32"]
                                                    if "hash_calculated_crc32" in t else "",
                                                set=lambda t, v: None)
    scene.hash_calculated_adler32 = StringProperty(name="Calculated Adler32", 
                                                default="", 
                                                get=lambda t: t["hash_calculated_adler32"]
                                                    if "hash_calculated_adler32" in t else "",
                                                set=lambda t, v: None)

    scene.show_hash_md5 = BoolProperty(name="Show MD5 Hash", 
                                        default=True)
    scene.show_hash_sha1 = BoolProperty(name="Show SHA1 Hash", 
                                        default=True)
    scene.show_hash_sha224 = BoolProperty(name="Show SHA224 Hash", 
                                        default=False)
    scene.show_hash_sha256 = BoolProperty(name="Show SHA256 Hash", 
                                        default=True)
    scene.show_hash_sha384 = BoolProperty(name="Show SHA384 Hash", 
                                        default=False)
    scene.show_hash_sha512 = BoolProperty(name="Show SHA512 Hash", 
                                        default=False)
    scene.show_hash_sha3_224 = BoolProperty(name="Show SHA3_224 Hash", 
                                        default=False)
    scene.show_hash_sha3_256 = BoolProperty(name="Show SHA3_256 Hash", 
                                        default=False)
    scene.show_hash_sha3_384 = BoolProperty(name="Show SHA3_384 Hash", 
                                        default=False)
    scene.show_hash_sha3_512 = BoolProperty(name="Show SHA3_512 Hash", 
                                        default=False)
    scene.show_hash_blake2b = BoolProperty(name="Show Blake2b Hash", 
                                        default=False)
    scene.show_hash_blake2s = BoolProperty(name="Show Blake2s Hash", 
                                        default=False)
#    scene.show_hash_shake_128 = BoolProperty(name="Show Shake_128 Hash", 
#                                        default=False)
#    scene.show_hash_shake_256 = BoolProperty(name="Show Shake_256 Hash", 
#                                        default=False)
    scene.show_hash_crc32 = BoolProperty(name="Show CRC32 Hash", 
                                        default=True)
    scene.show_hash_adler32 = BoolProperty(name="Show Adler32 Hash", 
                                        default=False)

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


def clear_props():
    scene = bpy.types.Scene
    del scene.hash_input_type
    del scene.hash_base_text
    del scene.hash_check_text

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
