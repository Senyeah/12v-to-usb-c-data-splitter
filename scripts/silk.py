"""Move reference designators to F.Fab and add user-facing silk labels."""
import sys
import pcbnew

MM = pcbnew.FromMM
# (text, x, y, size)
LABELS = [
    ("SWIFT USB-C 3A v1", 123.2, 138.5, 0.8),
    ("12V IN", 136.4, 102.0, 1.0),
    ("GND", 143.1, 111.9, 0.9),
    ("+12V", 148.2, 111.9, 0.9),
    ("TO STEREO", 105.0, 119.2, 0.9),
    ("TO PHONE", 103.2, 128.6, 0.9),
    ("WHT=ON RED=FAULT", 122.9, 137.1, 0.8),
]

board = pcbnew.LoadBoard(sys.argv[1])
for fp in board.GetFootprints():
    ref = fp.Reference()
    ref.SetLayer(pcbnew.F_Fab)
    ref.SetTextSize(pcbnew.VECTOR2I(MM(0.6), MM(0.6)))
    ref.SetTextThickness(MM(0.09))
    ref.SetPosition(fp.GetPosition())
for d in [d for d in board.GetDrawings() if d.GetClass() == "PCB_TEXT" and d.GetLayer() == pcbnew.F_SilkS]:
    board.Remove(d)
for text, x, y, size in LABELS:
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetLayer(pcbnew.F_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    t.SetTextThickness(MM(0.15))
    t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    board.Add(t)
board.Save(sys.argv[1])
print("labels", len(LABELS))
