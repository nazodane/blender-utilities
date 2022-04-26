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

from gpu.types import (
    GPUBatch,
    GPUIndexBuf,
    GPUVertBuf,
)

from bpy.props import (
    StringProperty,
    EnumProperty,
#    IntProperty,
)

from urllib import request
import ssl
import json
# https://www.shadertoy.com/howto

from bpy.app import driver_namespace

import time
from math import modf

def shadertoy_inputmenu(self, context):
    layout = self.layout
    scene = context.scene
    layout.label(text="Shadertoy ID:")
    layout.prop(scene, "shadertoy_id", text="")

import bpy.utils.previews
class SHADERTOY_PT_TexPanel(bpy.types.Panel):

    bl_label = "Shadertoy Texture"
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Shadertoy"
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
        layout.template_icon_view(scene, "shadertoy_tex1")
        layout.template_icon_view(scene, "shadertoy_tex2")
        layout.template_icon_view(scene, "shadertoy_tex3")
        layout.template_icon_view(scene, "shadertoy_tex4")

# media filename, preview checksum and data checksum
shadertoy_medias = [
# texture
("52d2a8f514c4fd2d9866587f4d7b2a5bfa1a11a0e772077d7682deb8b3b517e5.jpg", "feba0035840a060868bb527c1896748d143caa80", "6e18d74efb6050c93aacab6564b2d573417fc0ba"),
("bd6464771e47eed832c5eb2cd85cdc0bfc697786b903bfd30f890f9d4fc36657.jpg", "702e2a362c16854572c4fde348aed65d07957850", "433d6f95ab2a9849f2962789048a8aa189dfda06"),
("8979352a182bde7c3c651ba2b2f4e0615de819585cc37b7175bcefbca15a6683.jpg", "384799acf6f1e23b906d330361e80c13a2f288ec", "62289143fbfc8dfd1d147afafe4a36793be85cae"),
("85a6d68622b36995ccb98a89bbb119edf167c914660e4450d313de049320005c.png", "e64c60e4cdef91a0f40c088dfee5882e314e90a0", "fd139c755e23d41c9dfb4c386b2e794c98c45f5e"),
("cb49c003b454385aa9975733aff4571c62182ccdda480aaba9a8d250014f00ec.png", "a274d45973ec51eee97b649835c134cbda467491", "3da6177f75c41d6f44bb5c079c473506032688ef"),
("08b42b43ae9d3c0605da11d0eac86618ea888e62cdd9518ee8b9097488b31560.png", "c3e740b19c509e4b9ba30bd1f956180269209270", "21420cd0efcc5f9dc169f9bd292b1895bb69042e"),
("0c7bf5fe9462d5bffbd11126e82908e39be3ce56220d900f633d58fb432e56f5.png", "4cc472440edb8cf093d863a9345301f5373ec00c", "ed6317ba2093cb0e04d433e09ea73b38b089a195"),
("0a40562379b63dfb89227e6d172f39fdce9022cba76623f1054a2c83d6c0ba5d.png", "37dcec1273c42dd99e57453858b6df819b16bd2b", "065edcb7b547a505ecfb4449b8fad43d1fbb6369"),
("fb918796edc3d2221218db0811e240e72e340350008338b0c07a52bd353666a6.jpg", "232779cf22652224db7b60857be2d9b936fcc229", "6dd40833b0863dbb30291bf06ea24f8915ca9973"),
("8de3a3924cb95bd0e95a443fff0326c869f9d4979cd1d5b6e94e2a01f5be53e9.jpg", "7e5436c3623245c53f66aea7f209c0720686cc9a", "ddbc44932ba1eda04f01efd632c1743a15eec518"),
("cbcbb5a6cfb55c36f8f021fbb0e3f69ac96339a39fa85cd96f2017a2192821b5.png", "d74a2e4aac9d545b69992199c7b2a91d2c9683c0", "327768ef379c8d018d06c89a88a32f55e8635d13"),
("cd4c518bc6ef165c39d4405b347b51ba40f8d7a065ab0e8d2e4f422cbc1e8a43.jpg", "57cd620ed7ca3d169fdb68890dff9dd5e569fa32", "2fbe27e37d15d9e10a1504d6e53884ac285e4285"),
("92d7758c402f0927011ca8d0a7e40251439fba3a1dac26f5b8b62026323501aa.jpg", "110f671c9f3a8a32d439ac8a8b15bc86c1492ee0", "bf933f910083b2f6f04e77e5a02cb141b411237f"),
("79520a3d3a0f4d3caa440802ef4362e99d54e12b1392973e4ea321840970a88a.jpg", "7c4ca37d3fc8651f4fc937568095fbb38755a725", "cefe652b1dfd926a2ecfee762878d31efb95a06b"),
("3871e838723dd6b166e490664eead8ec60aedd6b8d95bc8e2fe3f882f0fd90f0.jpg", "6af1b7f3b970061b2f4f2be1181328dbce9125f2", "921079a6c5c01c26ff0bca75ab894ce861b62c86"),
("ad56fba948dfba9ae698198c109e71f118a54d209c0ea50d77ea546abad89c57.png", "acba02a8f7f84a824c2ef824a8f3d3cbf22ed468", "4ec9a78d1ead6cec81309e6b60eb3543f2b66343"),
("f735bee5b64ef98879dc618b016ecf7939a5756040c2cde21ccb15e69a6e1cfb.png", "3c94f2d0a0227d31415d142c1159fa554e64add4", "14ac970e0608033757fd81705ecd799fbb080599"),
("3083c722c0c738cad0f468383167a0d246f91af2bfa373e9c5c094fb8c8413e0.png", "7628fb944777db0f6676302982e45fb56eb263b9", "bd71e88e0d105326a6425965590ad31a821f6c91"),
("10eb4fe0ac8a7dc348a2cc282ca5df1759ab8bf680117e4047728100969e7b43.jpg", "fe8c83f588a94ce1f336a79e6a029ad007d53add", "b10070aea811437ce156b7b1ffd0d072e4c5edeb"),
("95b90082f799f48677b4f206d856ad572f1d178c676269eac6347631d4447258.jpg", "6018f06c14113c2f6e88732ce2f4938c372df934", "0d49d5392dc97c6bdca1636fc8fe1c415ec0c204"),
("e6e5631ce1237ae4c05b3563eda686400a401df4548d0f9fad40ecac1659c46c.jpg", "849b5c69e89b457e2621ad9983e410e9b5ecb458", "c447b6b18f33492f327f01f2ac65fcec94533e6e"),
("1f7dca9c22f324751f2a5a59c9b181dfe3b5564a04b724c657732d0bf09c99db.jpg", "75cd3d6b29da7fe97b98dec1dd288be68fec04dd", "29287430c8687394f0daf8d76e403e4f4c9283a8"),
("27012b4eadd0c3ce12498b867058e4f717ce79e10a99568cca461682d84a4b04.bin", "9c195cd7b8c83dd8c0404b57b1e04f4e752fa646", "f6cd4eac56a460709993106dbb017b4cd320fff0"),
("aea6b99da1d53055107966b59ac5444fc8bc7b3ce2d0bbb6a4a3cbae1d97f3aa.bin", "e1adf1709574e569444f68e4510013a17bc5ba41", "6718edc728d2ae794ca63de8ca9ed36bc120ff4a"),
("3405e48f74815c7baa49133bdc835142948381fbe003ad2f12f5087715731153.ogv", "c537cb181825779c62a596ea4a4465aa6be0724a", "8172eeb303e01af721c6cfa64e290e5d43ecaebe"),
("e81e818ac76a8983d746784b423178ee9f6cdcdf7f8e8d719341a6fe2d2ab303.webm", "67b16aa862dea839c2cdb3664cc1895c5ee2d2fa", "c61fb6861bd51336f89a8467f0b250c9e86c4125"),
("35c87bcb8d7af24c54d41122dadb619dd920646a0bd0e477e7bdc6d12876df17.webm", "3d9242d23d492218df25b5c3533d5288d317e8c6", "02d6e8db26b682f7b1c780f26e6746e8ed49daca"),
("c3a071ecf273428bc72fc72b2dd972671de8da420a2d4f917b75d20e1c24b34c.ogv", "78ecfcd48322be97b3cbbaf95f9b9e3acd8a8f61", "172d36a5f85b884fb90db22e7b9fce8c1efe4088"),
("a6a1cf7a09adfed8c362492c88c30d74fb3d2f4f7ba180ba34b98556660fada1.mp3", "5c96ed052d21d99a1d2a0dde200c9ccc365d0d02", "8cc881af6e09d2747fb94fdde9024c407612210f"),
("3c33c415862bb7964d256f4749408247da6596f2167dca2c86cc38f83c244aa6.mp3", "5c96ed052d21d99a1d2a0dde200c9ccc365d0d02", "1d38eb9ec902de534415f4cdbba2d87254a0125d"),
("29de534ed5e4a6a224d2dfffab240f2e19a9d95f5e39de8898e850efdb2a99de.mp3", "5c96ed052d21d99a1d2a0dde200c9ccc365d0d02", "00c86b7abf071149fd2e86d2b8bafde813486925"),
("48e2d9ef22ca6673330b8c38a260c87694d2bbc94c19fec9dfa4a1222c364a99.mp3", "5c96ed052d21d99a1d2a0dde200c9ccc365d0d02", "4f7433a1fd9e87846c1bc0b36eac1f5352c46ef7"),
("d96b229eeb7a08d53adfcf1ff89e54c9ffeebed193d317d1a01cc8125c0f5cca.mp3", "5c96ed052d21d99a1d2a0dde200c9ccc365d0d02", "6a836fabc00f51f26de68798acf7232fe5731787"),
("894a09f482fb9b2822c093630fc37f0ce6cfec02b652e4e341323e4b6e4a4543.mp3", "5c96ed052d21d99a1d2a0dde200c9ccc365d0d02", "dd8c8d19dc37ba6065d922365f2dc4d0a5b15d6e"),
("ec8a6ea755d34600547a5353f21f0a453f9f55ff95514383b2d80b8d71283eda.mp3", "5c96ed052d21d99a1d2a0dde200c9ccc365d0d02", "23800132939b5271a6c9f7c46f1970321e0133e5"),
]

# cubemap filename, preview checksum, xxx.png checksum, xxx_1.png 〜xxx_5.png checksum
shadertoy_cubemaps = [
("94284d43be78f00eb6b298e6d78656a1b34e2b91b34940d02f1ca8b22310e8a0.png", "cd24123f0331ed7f462398587445c8e40a3dbdb1", "3528e2e717106bf1906c759a1e2cb823e36e6c82", "2a2f0d6a9ae71308458fa863a8c8a6d996849b8b", "23d7436a44eb696eea73e2e0ac3522557ec93789", "bf294bd9da0c0171815d2de36efbe179a7a4ec52", "9ea9a1599905f0e4c4f85711b6124b1abf13bf6e", "67ee89c55ac40b3ab0e174a9ec086062e8bafb2f"),
("0681c014f6c88c356cf9c0394ffe015acc94ec1474924855f45d22c3e70b5785.png", "e7cd4eb10c7a712a63837bcdb10283eb6af63936", "fd3197b0d8b9e3920d882e889e45be47efddd2bd", "90e8d901e548e26647656e2e2185de9939198a2d", "2d5b8984e0e136accc951ecf105c6edee3c56e53", "4c0cbc8f016c5f5e7c5e0e40a3b54ebbafe5128d", "c9aeab855654ae4cbd9fb55d4397b00951f3f05d", "8d52bcf21b53cf2152a1a50966ced90f267bb31f"),
("488bd40303a2e2b9a71987e48c66ef41f5e937174bf316d3ed0e86410784b919.jpg", "2586d01575f57007c7da928d6491bf1bfb3e8081", "480b6f30c82e2252de8f337221763492a148475c", "19c5d38e4c54dfd813eaca4b668d68eef8a29a76", "5f3702668013fd4d90a3c695f2d297b7b7740aae", "1989f467694e249482ae6614054fad7bc5ec36da", "a998b2294e66754cc93f534d5fc86a6ce67c14b6", "a59957a766df19f722d96551bf7c43abac9abe8b"),
("550a8cce1bf403869fde66dddf6028dd171f1852f4a704a465e1b80d23955663.png", "92cde0b3c06c38a04474c9e7f26fd3569f118ba5", "9c4bbf4a999b6b2bbbe92102ead359555c28cf9a", "c67730876f9d50f83dd99d75f59533af0a964f5c", "a1402426a4d88376b2a2c1fd8ed6c33ce045f06a", "ae00d5cb416b32850d4c2018f72e684d76a9d1e5", "afb903df5b136dd1145e36f17b73759262ac72ae", "5cda4f171375a3be9fff549e9f303a86c1b2400c"),
("585f9546c092f53ded45332b343144396c0b2d70d9965f585ebc172080d8aa58.jpg", "6ab59386dc11d063cbbc825a9931a6b089ec6b8f", "d5253b87ecf5b0d0a447200d05f9b6eb1cfc8c51", "a80dae9d3f4e06cc1089e2b6f5ccb653688a318f", "bdffdc034cd21c3835bfcf6b158c92ad7304cb03", "d8dbd8401fe5030892db1080a8c0f0221d30c6dc", "4d5007ece14b7a8369c36495f03768c864306041", "3989a34c6f49ebc676cc9222072872008e9a4250"),
("793a105653fbdadabdc1325ca08675e1ce48ae5f12e37973829c87bea4be3232.png", "b74fa0c9cefa481ea1ca807438eb4bd06f43b7f5", "dea4c5372038c867a8dc1a16679ec14fdeb3607d", "356c86aebf7a39dc3eaafc099930ce54f757af9c", "9762d36ff4a4b7e72a955329fb758876b73328eb", "dffe0e2c1bc992d8584c35f71bfa0bfc52366b7b", "2d48a429c2b16d11b990450f6d4efe60c2d33c6e", "31b0ced51990bc0b92b5adabc6d55c6124c0a6b6"),
]

# previs filename, preview checksum
shadertoy_previs = [
("keyboard.png", "5d57aa7871f3233b4b8542c21db73124edccf034"),
("webcam.png", "afa80b933a80c3aa051100c2e6851d0a37b882ef"),
("mic.png", "df82838278c75ee607b9163897a33545e57c601c"),
("soundcloud.png", "c804eab4ba93ee131bdcccf1450497256ae0214b"),
("buffer00.png", "7a9922a6957e528276c18b9ebd5c7b3a370bad4b"),
("buffer01.png", "8165f4fe1efcfbd932bb101008a1b97d6f4fa937"),
("buffer02.png", "5afae206e253fa76b638b73337e792051b5eebc6"),
("buffer03.png", "57d00ce69ce309667029bfa8f9f85228a63d38f1"),
("cubemap00.png", "4c9099700bf050f4af20e8e0a4ea449a8ce6f819"),
]

import addon_utils
import os
def shadertoy_addon_directory():
    for mod in addon_utils.modules():
        if mod.bl_info['name'] == "Shadertoy Viewer":
            d = os.path.dirname(mod.__file__)
            d = os.path.join(d, "blender_shadertoy_media")
            if not os.path.exists(d):
                os.mkdir(d)
            return d

    print("ERROR: shadertoy_addon_directory: addon directory not found")
    return

from hashlib import sha1
def shadertoy_media_download():
    d = shadertoy_addon_directory()
    prev_d = os.path.join(d, "preview")
    if not os.path.exists(prev_d):
        os.mkdir(prev_d)
    data_d = os.path.join(d, "data")
    if not os.path.exists(data_d):
        os.mkdir(data_d)

    for t in (shadertoy_medias + shadertoy_cubemaps + shadertoy_previs):
        # preview download
        fpath = os.path.join(prev_d, re.sub("(\\.ogv|\\.webm)$", "\\1.gif", t[0]))
        if not os.path.exists(fpath): 
            print("shadertoy_media_download: preview downloading: " + t[0])
            if len(t) > 2:
                req = request.Request('https://www.shadertoy.com/media/ap/' + t[0])
            else:
                req = request.Request('https://www.shadertoy.com/media/previz/' + t[0])
            req.add_header('Referer', 'https://www.shadertoy.com/view/')
            req.add_header('User-Agent', 'Mozilla/5.0')
            res = request.urlopen(req, context = ssl._create_unverified_context()).read()
            if t[1] != "" and sha1(res).hexdigest() != t[1]:
                print("ERROR: shadertoy_media_download: SHA1 checksum is not same: " + t[0])
                continue
            open(fpath, 'wb').write(res)

        for i, h in enumerate(t[2:]):
            # data download
            fn = t[0]
            if i > 0:
                fn = re.sub("(\\.[^\\.]*)$", "_" + str(i) + "\\1", fn)
            fpath = os.path.join(data_d, fn)
            if not os.path.exists(fpath):
                print("shadertoy_media_download: data downloading: " + fn)
                req = request.Request('https://www.shadertoy.com/media/a/' + fn)
                req.add_header('Referer', 'https://www.shadertoy.com/view/')
                req.add_header('User-Agent', 'Mozilla/5.0')
                res = request.urlopen(req, context = ssl._create_unverified_context()).read()
                if h != "" and sha1(res).hexdigest() != h:
                    print("ERROR: shadertoy_media_download: SHA1 checksum is not same: " + fn)
                    continue
                open(fpath, 'wb').write(res)

#    checksum_generator()

def checksum_generator():
    d = shadertoy_addon_directory()
    prev_d = os.path.join(d, "preview")
    if not os.path.exists(prev_d):
        print("no preview directory found")
        return
    data_d = os.path.join(d, "data")
    if not os.path.exists(data_d):
        os.mkdir(data_d)
    for t in (shadertoy_medias + shadertoy_cubemaps + shadertoy_previs):
        p_fpath = os.path.join(prev_d, re.sub("(\\.ogv|\\.webm)$", "\\1.gif", t[0]))
        p_data = open(p_fpath, 'rb').read()
        line = '("' + t[0] + '", "' + sha1(p_data).hexdigest()
        for i, h in enumerate(t[2:]):
            fn = t[0]
            if i > 0:
                fn = re.sub("(\\.[^\\.]*)$", "_" + str(i) + "\\1", fn)
            d_fpath = os.path.join(data_d, fn)
            d_data = open(d_fpath, 'rb').read()
            line += '", "' + sha1(d_data).hexdigest()

        line += '"),'
        print(line)


import threading
class shadertoy_async_thread(threading.Thread):
    def run(self):
        shadertoy_media_download()

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
    rpass =(db[0]["renderpass"] if "renderpass" in db[0] else []) if len(db) else []
    print(rpass)

    intputs = (rpass[0]["inputs"] if "inputs" in rpass[0] else []) if len(rpass) else []
    for i in intputs:
        if "type" in i and i["type"] == "texture" and "filepath" in i:
            if "channel" in i and i["channel"] == 0:
                scene.shadertoy_tex1 = os.path.basename(i["filepath"])
            if "channel" in i and i["channel"] == 1:
                scene.shadertoy_tex2 = os.path.basename(i["filepath"])
            if "channel" in i and i["channel"] == 2:
                scene.shadertoy_tex3 = os.path.basename(i["filepath"])
            if "channel" in i and i["channel"] == 3:
                scene.shadertoy_tex4 = os.path.basename(i["filepath"])

    code = (rpass[0]["code"] if "code" in rpass[0] else "") if len(rpass) else ""

    if code == "":
        print("ERROR: shadertoy_shader_update: shadertoy_id: %s"%shadertoy_id)
        return

    txt = bpy.data.texts.new(shadertoy_id)
    txt.write(code)
    context.space_data.text = txt

    # https://www.shadertoy.com/view/XsjGDt -> ok
    # https://www.shadertoy.com/view/3sySRK -> ok
    # https://www.shadertoy.com/view/MdX3zr -> ok
    # https://www.shadertoy.com/view/Mss3zH (iMouse) -> ok
    # https://www.shadertoy.com/view/lsKGWV (iTimeDelta/iFrameRate) -> ok
    # https://www.shadertoy.com/view/WdtyRs (iDate) -> ok
    # https://www.shadertoy.com/view/tdSSzV (2d texture) -> ok

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
uniform sampler2D iChannel0;
uniform sampler2D iChannel1;
uniform sampler2D iChannel2;
uniform sampler2D iChannel3;

uniform vec4 iDate;
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

    driver_namespace["shadertoy_shader_param"] = (shader, batch)

    scene.render.engine = "SHADERTOY_ENGINE"
    scene.display_settings.display_device = 'None'
    scene.frame_end = 1048574
    scene.render.fps = 240
    scene.sync_mode = "FRAME_DROP"

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

    driver_namespace["shadertoy_clock"] = 0.0
    driver_namespace["shadertoy_framecount"] = 0
    driver_namespace["shadertoy_startclock"] = 0.0

    shadertoy_tex_update(self, context)

    bpy.ops.screen.animation_play()

import datetime

class ShadertoyRenderEngine(bpy.types.RenderEngine):
    bl_idname = 'SHADERTOY_ENGINE'
    bl_label = 'Shadertoy Engine'

    bl_use_image_save = False

    def view_update(self, context, depsgraph):
        pass

    def view_draw(self, context, depsgraph):
        scene = context.scene
        region = context.region
        screen = context.screen

        param = driver_namespace["shadertoy_shader_param"]
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
            shader.uniform_float("iMouse", driver_namespace["shadertoy_mouse"])
        except: pass
        try:
            shader.uniform_int("iFrame", int(modf(scene.frame_float)[1]))
        except: pass

        now = datetime.datetime.now()
        try:
            shader.uniform_float("iDate", (now.year, now.month-1, \
                now.day, now.hour * 60 * 60 +  now.minute * 60 + now.second + now.microsecond*0.000001))
        except: pass

        t = time.perf_counter()
        tdelta = t - driver_namespace["shadertoy_clock"]
        if tdelta >= 1.0 or driver_namespace["shadertoy_framecount"] == 0:
            driver_namespace["shadertoy_framecount"] = 0
            driver_namespace["shadertoy_startclock"] = time.perf_counter()
        try:
            shader.uniform_float("iTimeDelta", tdelta)
        except: pass
        try:
            shader.uniform_float("iFrameRate", driver_namespace["shadertoy_framecount"] / \
                (t - driver_namespace["shadertoy_startclock"]))
        except: pass
        driver_namespace["shadertoy_clock"] = time.perf_counter()
        driver_namespace["shadertoy_framecount"] += 1

        tex1 = driver_namespace["shadertoy_tex1"]
        if tex1:
            shader.uniform_sampler("iChannel0", tex1)
        tex2 = driver_namespace["shadertoy_tex2"]
        if tex2:
            shader.uniform_sampler("iChannel1", tex2)
        tex3 = driver_namespace["shadertoy_tex3"]
        if tex3:
            shader.uniform_sampler("iChannel2", tex3)
        tex4 = driver_namespace["shadertoy_tex4"]
        if tex4:
            shader.uniform_sampler("iChannel3", tex4)


        # 描画
        batch.draw(shader)
        gpu.state.blend_set('NONE')


class ShadertoyModalOperator(bpy.types.Operator):
    bl_idname = "shadertoy.modal_operator"
    bl_label = "Shadertoy Modal Operator"

    def invoke(self, context, event):
        scene = context.scene
#        print("click");
        driver_namespace["shadertoy_mouse"][0] = \
        driver_namespace["shadertoy_mouse"][2] = event.mouse_region_x
        driver_namespace["shadertoy_mouse"][1] = \
        driver_namespace["shadertoy_mouse"][3] = event.mouse_region_y
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def execute(self, context):
        return {'FINISHED'}

    def modal(self, context, event):
#        print("modal");
        driver_namespace["shadertoy_mouse"][0] = event.mouse_region_x
        driver_namespace["shadertoy_mouse"][1] = event.mouse_region_y
        if driver_namespace["shadertoy_mouse"][3] > 0:
            driver_namespace["shadertoy_mouse"][3] = -driver_namespace["shadertoy_mouse"][3]
        if event.value == 'RELEASE':
            driver_namespace["shadertoy_mouse"][2] = \
                -driver_namespace["shadertoy_mouse"][2];
#            print("released");
            return {'FINISHED'}

        return {'RUNNING_MODAL'}


def shadertoy_generate_tex_preview():
    p = driver_namespace["shadertoy_tex_preview"]
    image_location = p.images_location
    enum_items = []

    for i, img in enumerate([("none.png",)] + shadertoy_previs + shadertoy_cubemaps + shadertoy_medias):
        fpath = os.path.join(image_location, re.sub("(\\.ogv|\\.webm)$", "\\1.gif", img[0]))
#        print(fpath)
        if not os.path.exists(fpath):
            continue
        thumb = None
        if fpath not in p:
            thumb = p.load(fpath, fpath, 'IMAGE')
        else:
            thumb = p[fpath]
        enum_items.append((img[0], img[0], "", thumb.icon_id, i))

    return enum_items

def shadertoy_tex_update(self, context):
    scene = self

    d = shadertoy_addon_directory()
    data_d = os.path.join(d, "data")

    fpath = os.path.join(data_d, str(scene.shadertoy_tex1))
    if os.path.exists(fpath):
        img = bpy.data.images.load(fpath)
        tex = gpu.texture.from_image(img)
        driver_namespace["shadertoy_tex1"] = tex

    fpath = os.path.join(data_d, str(scene.shadertoy_tex2))
    if os.path.exists(fpath):
        img = bpy.data.images.load(fpath)
        tex = gpu.texture.from_image(img)
        driver_namespace["shadertoy_tex2"] = tex

    fpath = os.path.join(data_d, str(scene.shadertoy_tex3))
    if os.path.exists(fpath):
        img = bpy.data.images.load(fpath)
        tex = gpu.texture.from_image(img)
        driver_namespace["shadertoy_tex3"] = tex

    fpath = os.path.join(data_d, str(scene.shadertoy_tex4))
    if os.path.exists(fpath):
        img = bpy.data.images.load(fpath)
        tex = gpu.texture.from_image(img)
        driver_namespace["shadertoy_tex4"] = tex

from pathlib import Path

def init_props():
    th = shadertoy_async_thread()
    th.start()

    clear_props()
    scene = bpy.types.Scene
    scene.shadertoy_id = StringProperty(name="Shadertoy ID", 
                                          default="",
                                          update=shadertoy_shader_update)
    driver_namespace["shadertoy_inputmenu_handle"] = shadertoy_inputmenu
    bpy.types.TEXT_HT_header.append(shadertoy_inputmenu)

    d = shadertoy_addon_directory()
    p = bpy.utils.previews.new()
    p.images_location = os.path.join(d, "preview")
    driver_namespace["shadertoy_tex_preview"] = p
    scene.shadertoy_tex1 = EnumProperty(items=shadertoy_generate_tex_preview(), default="none.png", \
                                        update=shadertoy_tex_update)
    scene.shadertoy_tex2 = EnumProperty(items=shadertoy_generate_tex_preview(), default="none.png", \
                                        update=shadertoy_tex_update)
    scene.shadertoy_tex3 = EnumProperty(items=shadertoy_generate_tex_preview(), default="none.png", \
                                        update=shadertoy_tex_update)
    scene.shadertoy_tex4 = EnumProperty(items=shadertoy_generate_tex_preview(), default="none.png", \
                                        update=shadertoy_tex_update)

    if not Path(bpy.utils.script_path_user() + "/startup/bl_app_templates_user/Shadertoy/startup.blend").exists():
        #self.report({"WARNING"}, 
        print("The Shadertoy Viewer addon will not work correctly: the application template is not installed. You should ensure to install the template to {BLENDER_USER_SCRIPTS}/startup/bl_app_templates_user directory.")
        # TODO: error reporting in GUI
    driver_namespace["shadertoy_shader_param"] = None
    driver_namespace["shadertoy_mouse"] = [0, 0, 0, 0]
    driver_namespace["shadertoy_clock"] = 0.0
    driver_namespace["shadertoy_framecount"] = 0
    driver_namespace["shadertoy_startclock"] = 0.0

    driver_namespace["shadertoy_tex1"] = None
    driver_namespace["shadertoy_tex2"] = None
    driver_namespace["shadertoy_tex3"] = None
    driver_namespace["shadertoy_tex4"] = None

def clear_props():
    scene = bpy.types.Scene
    if "shadertoy_inputmenu_handle" in driver_namespace:
        bpy.types.TEXT_HT_header.remove(driver_namespace["shadertoy_inputmenu_handle"])
        del driver_namespace["shadertoy_inputmenu_handle"]
    if hasattr(scene, "shadertoy_id"):
        del scene.shadertoy_id


    if "shadertoy_tex_preview" in driver_namespace:
        del driver_namespace["shadertoy_tex_preview"]
    if hasattr(scene, "shadertoy_tex1"):
        del scene.shadertoy_tex1
    if hasattr(scene, "shadertoy_tex2"):
        del scene.shadertoy_tex2
    if hasattr(scene, "shadertoy_tex3"):
        del scene.shadertoy_tex3
    if hasattr(scene, "shadertoy_tex4"):
        del scene.shadertoy_tex4

    if "shadertoy_shader_param" in driver_namespace:
        del driver_namespace["shadertoy_shader_param"]
    if "shadertoy_mouse" in driver_namespace:
        del driver_namespace["shadertoy_mouse"]
    if "shadertoy_clock" in driver_namespace:
        del driver_namespace["shadertoy_clock"]
    if "shadertoy_framecount" in driver_namespace:
        del driver_namespace["shadertoy_framecount"]
    if "shadertoy_startclock" in driver_namespace:
        del driver_namespace["shadertoy_startclock"]

    if "shadertoy_tex1" in driver_namespace:
        del driver_namespace["shadertoy_tex1"]
    if "shadertoy_tex2" in driver_namespace:
        del driver_namespace["shadertoy_tex2"]
    if "shadertoy_tex3" in driver_namespace:
        del driver_namespace["shadertoy_tex3"]
    if "shadertoy_tex4" in driver_namespace:
        del driver_namespace["shadertoy_tex4"]

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
    SHADERTOY_PT_TexPanel,
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
