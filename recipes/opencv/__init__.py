import os
# pure-python package, this can be removed when we'll support any python package
from toolchain import Recipe,shprint
from os.path import join
import sh
import fnmatch
from distutils.dir_util import copy_tree

class OpenCVRecipe(Recipe):
    version = '2.4.10.1'
    url = 'https://github.com/Itseez/opencv/archive/{version}.zip'
    depends = ['numpy']
    #patches = ['patches/p4a_build-2.4.10.1.patch']
    # libraries  =  ['lib/libopencv_features2d.a','lib/libopencv_flann.a','lib/libopencv_highgui.a',\
    #           'lib/libopencv_imgproc.a','lib/libopencv_ml.a','lib/libopencv_nonfree.a',\
    #           'lib/libopencv_objdetect.a','lib/libopencv_photo.a','lib/libopencv_video.a','lib/libopencv_videostab.a']
    library = 'lib/libopencv_highgui.a'

    def prebuild_arch(self, arch):
        if self.has_marker("patched"):
            return
        self.apply_patch("ios_build-2.4.10.1.patch")
        self.set_marker("patched")
        raw_input()

    def get_recipe_env(self, arch):
        env = super(OpenCVRecipe, self).get_recipe_env(arch)
        #HON_ROOT'] = self.ctx.hostpython
        #env['ANDROID_NDK'] = self.ctx.ndk_dir
        env["IOSSDKROOT"]  = arch.sysroot
        #env['SITEPACKAGES_PATH'] = join(self.ctx.dist_dir(),'root','python','lib','python2.7','site-packages')
        #raw_input()
        return env

    def build_arch(self, arch):
        build_env = arch.get_env()
        build_framework = sh.Command(join(self.build_dir,"platforms","ios","build_framework.py"))
        if arch.arch in ['armv7','arm64']:
            target = 'iPhoneOS'
        if arch.arch in ['i386','x86_64']:
            target = 'iPhoneSimulator'
        #shprint(build_framework,'build',target,arch.arch)
        #self.copyLib(target+'-'+arch.arch)

    def copyLib(self,target):
        arch = list(self.filtered_archs)[0]
        build_dir = self.get_build_dir(arch.arch)
        os.mkdir('lib')
        copy_tree(join(build_dir,'Release'),'lib')

    def biglink(self):
        dirs = []
        print self.build_dir
        raw_input()
        for root, dirnames, filenames in os.walk(self.build_dir):
            if fnmatch.filter(filenames, "*.a"):
                dirs.append(root)
        cmd = sh.Command(join(self.ctx.root_dir, "tools", "biglink"))
        shprint(cmd, join(self.build_dir, "cv2.a"), *dirs)

recipe = OpenCVRecipe()

