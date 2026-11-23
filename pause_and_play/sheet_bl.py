"""Character sheet rendered with the Blender backend (run with the bpy Python)."""
import os
import sys

import bl_backend  # noqa: F401  (must come before sheet / engine.Scene users)
import sheet

if __name__ == "__main__":
    sheet.main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "out", "character_sheet.png"))
