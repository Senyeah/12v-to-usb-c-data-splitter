"""Prints courtyard overlaps and extents: overlaps.py <board>"""
import itertools, sys
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); M = pcbnew.ToMM
cys = {}
for fp in b.GetFootprints():
    c = fp.GetCourtyard(pcbnew.F_CrtYd); bb = c.BBox() if c.OutlineCount() else fp.GetBoundingBox(False)
    cys[fp.GetReference()] = (M(bb.GetLeft()), M(bb.GetTop()), M(bb.GetRight()), M(bb.GetBottom()))
ov = [(a, c, round(min(A[2], B[2]) - max(A[0], B[0]), 2), round(min(A[3], B[3]) - max(A[1], B[1]), 2))
      for (a, A), (c, B) in itertools.combinations(cys.items(), 2) if A[0] < B[2] and B[0] < A[2] and A[1] < B[3] and B[1] < A[3]]
print("overlaps:", ov)
xs = [v for r in cys.values() for v in (r[0], r[2])]; ys = [v for r in cys.values() for v in (r[1], r[3])]
print("extent x %.1f..%.1f y %.1f..%.1f" % (min(xs), max(xs), min(ys), max(ys)))
