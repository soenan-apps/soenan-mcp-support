import shutil
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py


class BuildPy(build_py):
    def run(self):
        build_lib = Path(self.build_lib).resolve()
        build_root = Path(__file__).resolve().parent / "build"
        if build_lib.parent != build_root or not build_lib.name.startswith("lib"):
            raise ValueError("build_lib must be a lib directory directly under build/")
        if build_lib.exists() and not self.dry_run:
            shutil.rmtree(build_lib)
        super().run()


setup(cmdclass={"build_py": BuildPy})
