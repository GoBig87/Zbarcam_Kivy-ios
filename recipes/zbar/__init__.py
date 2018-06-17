import os
from toolchain import PythonRecipe,shprint
from os.path import join
import sh
import fnmatch

class ZBarRecipe(PythonRecipe):

    version = '0.10'

    # For some reason the version 0.10 on PyPI is not the same as the ones
    # in sourceforge and GitHub. The one in PyPI has a setup.py.
    # url = 'https://github.com/ZBar/ZBar/archive/{version}.zip'
    url = 'https://pypi.python.org/packages/e0/5c/' + \
        'bd2a96a9f2adacffceb4482cdd56831735ab5a67ea6a60c0a8757c17b62e' + \
        '/zbar-{version}.tar.gz'
    library = "zbar.a"
    depends = ['hostpython','python', 'host_setuptools', 'libzbar','pil']
    pbx_libraries = ["libz","libbz2",'libc++','libsqlite3','CoreMotion']
    include_per_arch = True

    def prebuild_arch(self, arch):
        if self.has_marker("patched"):
            return
        self.apply_patch("zbar-0.10-python-crash.patch")
        self.set_marker("patched")

    def get_zbar_env(self, arch):
        build_env = arch.get_env()
        dest_dir = join(self.ctx.dist_dir, "root", "python")
        build_env["IOSROOT"] = self.ctx.root_dir
        build_env["IOSSDKROOT"] = arch.sysroot
        build_env["LDSHARED"] = join(self.ctx.root_dir, "tools", "liblink")
        build_env["ARM_LD"] = build_env["LD"]
        build_env["ARCH"] = arch.arch
        build_env["C_INCLUDE_PATH"] = join(arch.sysroot, "usr", "include")
        build_env["LIBRARY_PATH"] = join(arch.sysroot, "usr", "lib")
        build_env['PYTHONPATH'] = join(dest_dir, 'lib', 'python2.7', 'site-packages')
        # build_env['CFLAGS'] += ' -I' + join('build','python',arch.arch,'Python-2.7.1', 'Modules')
        # build_env['CFLAGS'] += ' -I' + join(self.ctx.dist_dir,'lib')
        # build_env['CFLAGS'] += ' -I' + join(self.ctx.dist_dir,'include', arch.arch,'libzbar')
        # build_env['CFLAGS'] += ' -I' + join(self.ctx.dist_dir,'include', arch.arch,'libzbar','zbar')
        # build_env['CFLAGS'] += " -arch {}".format(arch.arch)
        #" -I{}".format(join(self.ctx.dist_dir, "root", 'python', 'lib', 'python2.7', "site-packeges")) +
        build_env["CFLAGS"] = " ".join([
            " -I{}".format(join(self.ctx.dist_dir, "include", arch.arch, "libzbar")) +
            " -I{}".format(join(self.ctx.dist_dir, "include", arch.arch, "libzbar",'zbar')) +
            " -I{}".format(join(self.ctx.dist_dir, "include", arch.arch, "lib")) +
            " -arch {}".format(arch.arch)
            ])
        return build_env

    def build_arch(self, arch):
        build_env = self.get_zbar_env(arch)
        #build_dir = self.get_build_dir(arch.arch)
        hostpython = sh.Command(self.ctx.hostpython)
        #build_env["PYTHONHOME"] = hostpython
        # first try to generate .h
        shprint(hostpython, "setup.py", "build",
                _env=build_env)
        # print os.getcwd()
        # raw_input()
        # os.chdir(join('build','temp.macosx-10.13-x86_64-2.7'))
        # archive = sh.Command('ar')
        # shprint(archive,'rcs','zbar.a','image.o','enum.o')
        self.biglink()

    def install(self):
        pass
    #     arch = list(self.filtered_archs)[0]
    #     build_dir = self.get_build_dir(arch.arch)
    #     os.chdir(build_dir)
    #     hostpython = sh.Command(self.ctx.hostpython)
    #     build_env = self.get_zbar_env(arch)
    #     dest_dir = join(self.ctx.dist_dir, "root", "python")
    #     #build_env['PYTHONHOME'] = join(self.ctx.dist_dir,'dist','hostpython')
    #     build_env['PYTHONPATH'] = join(dest_dir, 'lib', 'python2.7', 'site-packages')
    #     # es = self.ctx.dist_dir + '/hostpython/bin/easy_install'
    #     # easy_install = sh.Command(es)
    #     # shprint(easy_install,
    #     #         "--prefix", dest_dir, "-Z", "./",
    #     #         _env=build_env)
    #     print build_dir
    #     raw_input()
    #     shprint(hostpython, "setup.py", "install",'-O2' ,"--prefix", dest_dir, _env=build_env)
    #     raw_input()

    def biglink(self):
        dirs = []
        for root, dirnames, filenames in os.walk(self.build_dir):
            if fnmatch.filter(filenames, "*.o"):
                dirs.append(root)
        cmd = sh.Command(join(self.ctx.root_dir, "tools", "biglink"))
        shprint(cmd, join(self.build_dir, "zbar.a"), *dirs)

recipe = ZBarRecipe()

