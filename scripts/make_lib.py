"""Writes lib/swift.kicad_sym (MPQ4228-C) and the QFN-22 footprint from datasheet Rev 1.0 land pattern."""
import uuid

# (number, name, type, side, slot) side: L/R/B; slot counts down from the top
PINS = [
    ("14", "IN", "power_in", "L", 0), ("13", "EN/SYNC", "input", "L", 2), ("10", "FREQ", "input", "L", 4),
    ("11", "VCC1", "power_out", "L", 6), ("20", "VCC2", "power_out", "L", 7), ("2", "FLT", "open_collector", "L", 9),
    ("5", "DP_OUT", "bidirectional", "L", 11), ("6", "DM_OUT", "bidirectional", "L", 12),
    ("16", "BST", "passive", "R", 0), ("15", "SW", "power_out", "R", 1), ("17", "OUT", "power_in", "R", 3),
    ("12", "FB", "input", "R", 4), ("7", "ADJ", "passive", "R", 5), ("4", "USB_IN", "power_in", "R", 6),
    ("3", "USB_OUT", "power_out", "R", 7), ("9", "DP", "bidirectional", "R", 9), ("8", "DM", "bidirectional", "R", 10),
    ("1", "CC1", "bidirectional", "R", 11), ("22", "CC2/EN1", "bidirectional", "R", 12),
    ("18", "GND", "power_in", "B", 0), ("19", "GND", "passive", "B", 1), ("21", "GND", "passive", "B", 2),
]
TOP = 15.24


def pin(num, name, typ, side, slot):
    if side == "L":
        x, y, a = -15.24, TOP - 2.54 * slot, 0
    elif side == "R":
        x, y, a = 15.24, TOP - 2.54 * slot, 180
    else:
        x, y, a = -2.54 + 2.54 * slot, -(TOP + 5.08), 90
    hide = " (hide yes)" if side == "B" and slot > 0 else ""
    return f'''      (pin {typ} line (at {x} {y} {a}) (length 2.54){hide}
        (name "{name}" (effects (font (size 1.27 1.27))))
        (number "{num}" (effects (font (size 1.27 1.27))))
      )'''


def prop(k, v, y, hide=False):
    return f'''    (property "{k}" "{v}" (at 0 {y} 0) (effects (font (size 1.27 1.27))){" (hide yes)" if hide else ""})'''


sym = f'''(kicad_symbol_lib
  (version 20241209)
  (generator "kicad_symbol_editor")
  (generator_version "9.0")
  (symbol "MPQ4228-C"
    (exclude_from_sim no) (in_bom yes) (on_board yes)
{prop("Reference", "U", 20.32)}
{prop("Value", "MPQ4228GRE-C-AEC1", 17.78)}
{prop("Footprint", "swift:MPS_QFN-22_4x4mm_P0.5mm", -25.4, True)}
{prop("Datasheet", "https://www.monolithicpower.com/en/mpq4228.html", -27.94, True)}
{prop("Description", "36 V 3 A buck with USB Type-C 5 V 3 A DFP, BC1.2 CDP and USB 2.0 data switch, AEC-Q100, QFN-22 4x4", -30.48, True)}
    (symbol "MPQ4228-C_0_1"
      (rectangle (start -12.7 17.78) (end 12.7 -17.78) (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "MPQ4228-C_1_1"
''' + "\n".join(pin(*p) for p in PINS) + '''
    )
  )
)
'''
open("lib/swift.kicad_sym", "w").write(sym)

# Land pattern (top view, mm). Short pads 0.25 x 0.85 from the 2.30 line inward; long pads 0.25 x 1.55.
pads = []
def side_pad(num, x_sign, y, long):
    length = 1.55 if long else 0.85
    cx = x_sign * (2.30 - length / 2)
    pads.append((num, cx, y, length, 0.25))
def row_pad(num, x, y_sign, long):
    length = 1.55 if long else 0.85
    cy = y_sign * (2.30 - length / 2)
    pads.append((num, x, cy, 0.25, length))
for i, y in enumerate([-1.25, -0.75, -0.25, 0.25, 0.75, 1.25]):          # pins 1-6, left, top to bottom
    side_pad(str(1 + i), -1, y, i in (2, 3))
for i, x in enumerate([-1.0, -0.5, 0.0, 0.5, 1.0]):                      # pins 7-11, bottom, left to right
    row_pad(str(7 + i), x, 1, i == 2)
for i, y in enumerate([1.25, 0.75, 0.25, -0.25, -0.75, -1.25]):          # pins 12-17, right, bottom to top
    side_pad(str(12 + i), 1, y, i in (2, 3))
for i, x in enumerate([1.0, 0.5, 0.0, -0.5, -1.0]):                      # pins 18-22, top, right to left
    row_pad(str(18 + i), x, -1, i == 2)
u = lambda: str(uuid.uuid4())
pad_txt = "\n".join(
    f'  (pad "{n}" smd roundrect (at {x:.4f} {y:.4f}) (size {w} {h}) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.25) (uuid "{u()}"))'
    for n, x, y, w, h in pads)
fp = f'''(footprint "MPS_QFN-22_4x4mm_P0.5mm"
  (version 20241229)
  (generator "pcbnew")
  (generator_version "9.0")
  (layer "F.Cu")
  (descr "MPS QFN-22 4x4 mm flip-chip (MPQ4228-C), recommended land pattern from datasheet Rev 1.0 p29")
  (tags "QFN-22 MPS MPQ4228")
  (attr smd)
  (property "Reference" "REF**" (at 0 -3.3 0) (layer "F.SilkS") (uuid "{u()}") (effects (font (size 1 1) (thickness 0.15))))
  (property "Value" "MPS_QFN-22_4x4mm_P0.5mm" (at 0 3.3 0) (layer "F.Fab") (uuid "{u()}") (effects (font (size 1 1) (thickness 0.15))))
  (fp_rect (start -2 -2) (end 2 2) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab") (uuid "{u()}"))
  (fp_line (start -2.1 -2.1) (end -1.5 -2.1) (stroke (width 0.12) (type default)) (layer "F.SilkS") (uuid "{u()}"))
  (fp_line (start 2.1 2.1) (end 1.5 2.1) (stroke (width 0.12) (type default)) (layer "F.SilkS") (uuid "{u()}"))
  (fp_circle (center -2.55 -1.8) (end -2.45 -1.8) (stroke (width 0.2) (type default)) (fill solid) (layer "F.SilkS") (uuid "{u()}"))
  (fp_rect (start -2.6 -2.6) (end 2.6 2.6) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd") (uuid "{u()}"))
{pad_txt}
  (model "${{KICAD10_3DMODEL_DIR}}/Package_DFN_QFN.3dshapes/QFN-24_4x4mm_P0.5mm.step"
    (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))
)
'''
# The QFN-24 model is a visual stand-in: same 4x4 mm body and 0.5 mm pitch, no exposed pad.
open("lib/swift.pretty/MPS_QFN-22_4x4mm_P0.5mm.kicad_mod", "w").write(fp)
print(len(pads), "pads")
