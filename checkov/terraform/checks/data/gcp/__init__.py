from pathlib import Path

modules = Path(__file__).parent.glob("*.py")
__all__ = [f.stem for f in modules if f.is_file() and not f.stem == "__init__"]
