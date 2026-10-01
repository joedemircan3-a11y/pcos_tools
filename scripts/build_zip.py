"""Build dist/pcos_tools_v<major.minor>.zip from this checkout. Standard library only.

Usage: python scripts/build_zip.py
"""
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INCLUDE = ["README.md", "CHANGELOG.md", "pyproject.toml", "pcos_tools", "tests", "scripts", "agents", "skills"]
SKIP_DIRS = {"__pycache__", ".pytest_cache", "out", "dist", ".git"}


def main():
    init = (ROOT / "pcos_tools" / "__init__.py").read_text(encoding="utf-8")
    version = re.search(r'__version__ = "([^"]+)"', init).group(1)
    short = ".".join(version.split(".")[:2])
    top = f"pcos_tools_v{short}"
    target = ROOT / "dist" / f"{top}.zip"
    target.parent.mkdir(exist_ok=True)
    if target.exists():
        target.unlink()
    count = 0
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in INCLUDE:
            path = ROOT / name
            if not path.exists():
                continue
            files = [path] if path.is_file() else sorted(p for p in path.rglob("*") if p.is_file())
            for file in files:
                relative = file.relative_to(ROOT)
                if SKIP_DIRS & set(relative.parts) or file.suffix == ".pyc":
                    continue
                archive.write(file, f"{top}/{relative.as_posix()}")
                count += 1
    print(f"wrote {target} ({count} files, {target.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
