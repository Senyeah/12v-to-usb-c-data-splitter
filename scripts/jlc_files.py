"""JLCPCB BOM + CPL from kicad-cli exports: jlc_files.py <raw_bom.csv> <raw_pos.csv> <outdir> <name> [--with-tht]"""
import csv
import math
import sys

# JLC places its own (EasyEDA) footprint origin at Mid X/Y. Where that origin differs from KiCad's, shift it:
# (dx, dy) in the KiCad footprint frame (mm, y down) and extra rotation, from comparing the EasyEDA footprints.
CPL_FIX = {
    "J3": (0.0, -1.424, 0),     # TYPE-C-31-M-12: EasyEDA origin sits 1.42 mm toward the pad row
    "J2": (2.355, 1.25, 90),    # DS1099-WN0: EasyEDA origin at the pin-field centre, drawn mouth +y
    "J1": (2.54, 0.0, 0),       # 1729128: EasyEDA origin between the two pins
}

raw_bom, raw_pos, out, name = sys.argv[1:5]
# J1/J2 are THT: the owner solders them, unless JLC's hand-soldering service is used.
HAND_SOLDER = set() if "--with-tht" in sys.argv else {"J1", "J2"}
if not HAND_SOLDER:
    name += "-with-tht"
by_lcsc = {}
for r in csv.DictReader(open(raw_bom)):
    refs = [x for x in r["Ref"].split(",") if x and x not in HAND_SOLDER]
    if refs and r["LCSC"]:
        by_lcsc.setdefault(r["LCSC"], [r["Value"], [], r["Footprint"].split(":")[-1]])[1].extend(refs)
rows = [(v, ",".join(refs), fp, lcsc) for lcsc, (v, refs, fp) in by_lcsc.items()]
with open(f"{out}/{name}-bom-jlc.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    w.writerows(rows)
placed = {ref for row in rows for ref in row[1].split(",")}
with open(f"{out}/{name}-cpl-jlc.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    for r in csv.DictReader(open(raw_pos)):
        if r["Ref"] in placed:
            x, y, rot = float(r["PosX"]), float(r["PosY"]), float(r["Rot"])
            dx, dy, drot = CPL_FIX.get(r["Ref"], (0.0, 0.0, 0))
            a = math.radians(rot)
            # Rotate the footprint-frame offset to the board (y down), then flip y for the pos file's y-up frame.
            x += dx * math.cos(a) + dy * math.sin(a)
            y -= -dx * math.sin(a) + dy * math.cos(a)
            w.writerow([r["Ref"], f"{x:.3f}mm", f"{y:.3f}mm", "Top", f"{(rot + drot) % 360:.0f}"])
print(len(rows), "BOM lines,", len(placed), "placements")
