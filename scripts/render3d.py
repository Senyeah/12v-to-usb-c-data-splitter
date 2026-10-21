"""3D renders into docs/, with stand-in models for parts KiCad ships no model for.

Run with KiCad's Python: render3d.py
The board file is not changed; stand-ins go on a temporary copy.
"""
import os
import shutil
import subprocess
import tempfile
import pcbnew

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
N = "swift-usbc-3a"
USB_B = os.path.join(ROOT, "lib", "3d", "USB_B_standin.wrl")
# Same 16P top-mount body and shield-pin positions as the HRO TYPE-C-31-M-12 (within 0.03 mm).
USB_C = "${KICAD10_3DMODEL_DIR}/Connector_USB.3dshapes/USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal.step"


def box(cx, cy, cz, sx, sy, sz, rgb):
    # KiCad reads VRML in 0.1 inch units; model Y points opposite to footprint Y.
    u = 2.54
    return (f"Transform {{ translation {cx/u:.4f} {-cy/u:.4f} {cz/u:.4f} children Shape {{ "
            f"appearance Appearance {{ material Material {{ diffuseColor {rgb} specularColor 0.6 0.6 0.6 shininess 0.4 }} }} "
            f"geometry Box {{ size {sx/u:.4f} {sy/u:.4f} {sz/u:.4f} }} }} }}\n")


def write_usb_b():
    # Footprint F.Fab outline: x -1.49..15.01, y -4.8..7.3; opening faces +x.
    body = box(6.76, 1.25, 5.45, 16.5, 12.1, 10.9, "0.78 0.79 0.80")
    mouth = box(14.62, 1.25, 5.6, 0.8, 8.0, 7.3, "0.08 0.08 0.09")
    tongue = box(14.3, 1.25, 5.6, 1.6, 4.4, 3.0, "0.95 0.95 0.93")
    open(USB_B, "w").write("#VRML V2.0 utf8\n" + body + mouth + tongue)


def main():
    write_usb_b()
    out = os.path.join(ROOT, "docs")
    os.makedirs(out, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for ext in ("kicad_pcb", "kicad_pro"):
            shutil.copy(os.path.join(ROOT, f"{N}.{ext}"), os.path.join(tmp, f"{N}.{ext}"))
        board_path = os.path.join(tmp, f"{N}.kicad_pcb")
        board = pcbnew.LoadBoard(board_path)
        for ref, path in (("J2", USB_B), ("J3", USB_C)):
            fp = board.FindFootprintByReference(ref)
            fp.Models().clear()
            m = pcbnew.FP_3DMODEL()
            m.m_Filename = path
            fp.Models().push_back(m)
        board.Save(board_path)
        views = {
            "iso": ["--rotate", "-50,0,-35", "--zoom", "0.8", "--perspective", "--floor"],
            "iso-back": ["--rotate", "-50,0,145", "--zoom", "0.8", "--perspective", "--floor"],
            "top": ["--side", "top", "--zoom", "0.95"],
        }
        for name, args in views.items():
            subprocess.run([CLI, "pcb", "render", "--quality", "high", "-w", "2000", "-h", "1400",
                            "--background", "opaque", *args, "-o", os.path.join(out, f"{N}-{name}.png"), board_path],
                           check=True, capture_output=True)
            print("wrote", f"docs/{N}-{name}.png")


main()
