<<<<<<< HEAD
from os.path import dirname, basename, isfile, join
import glob

modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith("__init__.py")]
=======
from pathlib import Path

modules = Path(__file__).parent.glob("*.py")
__all__ = [f.stem for f in modules if f.is_file() and not f.stem == "__init__"]
>>>>>>> 5afbd2498e97b3c13edb7fe3f2c58291f4c4a2b2
