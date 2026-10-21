# /// script
# requires-python = ">=3.11"
# dependencies = ["schemdraw>=0.23", "matplotlib"]
# ///
"""Printable A5 schematic + BOM for swift-usbc-3a: uv run scripts/print_schematic.py

Hand-placed redraw of the KiCad netlist for a box label; the KiCad schematic stays the source of truth.
"""
import csv
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
import schemdraw
import schemdraw.elements as elm

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "docs", "swift-usbc-3a-schematic-A5.pdf")
A5 = (210 / 25.4, 148 / 25.4)
FONT = "Arial"
plt.rcParams.update({"font.family": FONT, "pdf.fonttype": 42})

C_IN, C_SW, C_5V, C_DATA, C_CC, C_CTL, C_GND = "#c62828", "#6a1b9a", "#e65100", "#1565c0", "#00838f", "#2e7d32", "#222222"
FS = 5.2      # part labels
FSN = 4.6     # pin names / net tags


def wire(d, pts, color):
    for a, b in zip(pts, pts[1:]):
        d += elm.Line().at(a).to(b).color(color).linewidth(0.9)


def dot(d, p, color):
    d += elm.Dot(radius=0.07).at(p).color(color)


def gnd(d, p):
    d += elm.Ground().at(p).color(C_GND).linewidth(0.8)


def shunt(d, kind, top, length, ref, val, color, ground=True, lab="right"):
    """Vertical part from top downward, optional ground at the bottom."""
    e = kind().at(top).down(length).color(C_GND).linewidth(0.8)
    e = e.label(f"{ref}\n{val}", loc="bottom" if lab == "right" else "top", fontsize=FS, ofst=0.12)
    d += e
    if ground:
        gnd(d, e.end)
    return e


def series(d, kind, start, length, ref, val, direction="right"):
    e = kind().at(start).color(C_GND).linewidth(0.8)
    e = getattr(e, direction)(length)
    d += e.label(ref, loc="top", fontsize=FS, ofst=0.08).label(val, loc="bottom", fontsize=FS, ofst=0.08)
    return e


def tag(d, p, text, color, side="right"):
    d += elm.Tag(width=1.7, height=0.42).at(p).color(color).linewidth(0.7).label(text, fontsize=FSN, color=color)
    return d


def text(d, p, s, size=FSN, color=C_GND, halign="center", valign="center", **kw):
    d += elm.Label().at(p).label(s, fontsize=size, color=color, halign=halign, valign=valign, **kw)


def box(d, x0, y0, x1, y1, color=C_GND, lw=1.0):
    wire(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], color)


def netlabel(d, p, name, color, direction="right"):
    """Net label: short stub then a tag pointing away from the pin."""
    e = elm.Tag(width=1.9, height=0.5).at(p).color(color).linewidth(0.7)
    e = e.left() if direction == "left" else e.right()
    d += e.label(name, fontsize=FSN, color=color)


def vpart(d, kind, top, length, lines, ground=True, side="right", dx=0.35, **kw):
    e = kind(**kw).at(top).down(length).color(C_GND).linewidth(0.8)
    d += e
    mid = (top[0] + (dx if side == "right" else -dx), top[1] - length / 2)
    text(d, mid, "\n".join(lines), FS, halign="left" if side == "right" else "right")
    if ground:
        gnd(d, e.end)
    return e


def hpart(d, kind, start, length, ref, val, **kw):
    e = kind(**kw).at(start).right(length).color(C_GND).linewidth(0.8)
    d += e.label(ref, loc="top", fontsize=FS, ofst=0.08).label(val, loc="bottom", fontsize=FS, ofst=0.08)
    return e


def schematic(ax):
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(unit=2.0, fontsize=FS, font=FONT, lw=0.8)

    # ---- Input: J1, TVS, reverse diode, LC filter, EN divider ------------------------------------
    y = 25.0
    box(d, -0.4, 22.4, 1.3, 25.6)
    text(d, (0.45, 26.25), "J1  12 V IN", FS + 0.2)
    text(d, (0.45, 25.0), "1 +12V", FSN)
    text(d, (0.45, 23.0), "2 GND", FSN)
    wire(d, [(1.3, y), (3.0, y)], C_IN)
    # D1 sits at x 2.2 so D2's labels clear it
    wire(d, [(1.3, 23.0), (1.8, 23.0), (1.8, 22.6)], C_GND)
    gnd(d, (1.8, 22.6))
    dot(d, (2.2, y), C_IN)
    vpart(d, elm.DiodeTVS, (2.2, y), 2.2, [], side="left")
    text(d, (3.1, 21.3), "D1 SMBJ33CA\nTVS 33 V", FS - 0.2)
    text(d, (1.45, 25.4), "VBAT_IN", 4.2, C_IN, halign="left")
    d += elm.Schottky().at((3.0, y)).right(2.6).color(C_GND).linewidth(0.8).label("D2 SS510", loc="top", fontsize=FS, ofst=0.12).label("100 V 5 A", loc="bottom", fontsize=FS, ofst=0.12)
    wire(d, [(5.6, y), (14.0, y)], C_IN)
    text(d, (6.2, 26.0), "VIN_F", FSN, C_IN, halign="left")
    for i, (ref, val, v) in enumerate([("C11", "22n", "50V"), ("C12", "22n", "50V"), ("C13", "100n", "50V"), ("C14", "10µ", "50V")]):
        x = 6.4 + 2.0 * i
        dot(d, (x, y), C_IN)
        vpart(d, elm.Capacitor, (x, y), 2.2, [ref, val, v])
    d += elm.Inductor2(loops=3).at((14.0, y)).right(2.4).color(C_GND).linewidth(0.8).label("L2", loc="top", fontsize=FS, ofst=0.1).label("2.2µH", loc="bottom", fontsize=FS, ofst=0.1)
    wire(d, [(16.4, y), (29.0, y)], C_IN)
    text(d, (16.8, 26.0), "VIN1", FSN, C_IN, halign="left")
    for i, (ref, val, v) in enumerate([("C1", "100µ", "50V"), ("C2", "4.7µ", "50V"), ("C3", "4.7µ", "50V"), ("C4", "100n", "50V")]):
        x = 17.4 + 2.0 * i
        dot(d, (x, y), C_IN)
        kw = {"polar": True} if ref == "C1" else {}
        vpart(d, elm.Capacitor2 if ref == "C1" else elm.Capacitor, (x, y), 2.2, [ref, val, v], **kw)
    dot(d, (25.6, y), C_IN)
    vpart(d, elm.Resistor, (25.6, y), 1.6, ["R1", "100k"], ground=False)
    dot(d, (25.6, 23.4), C_CTL)
    wire(d, [(25.6, 23.4), (27.2, 23.4), (27.2, 23.0), (29.0, 23.0)], C_CTL)
    vpart(d, elm.Resistor, (25.6, 23.4), 1.4, ["R2", "36k"])
    text(d, (27.9, 23.35), "EN", FSN, C_CTL)

    # ---- U1 ---------------------------------------------------------------------------------------
    x0, x1, yt, yb = 29.0, 35.0, 26.0, 8.2
    box(d, x0, yb, x1, yt)
    text(d, (32.0, 26.5), "U1  MPQ4228GRE-C-AEC1", FS + 0.5)
    text(d, (32.0, 27.1), "36 V 3 A buck · USB switch · Type-C 3 A source · BC1.2 CDP", 3.9, color="#555555")
    left = [("IN", 14, 25.0), ("EN/SYNC", 13, 23.0), ("FREQ", 10, 21.0), ("VCC1", 11, 19.5), ("VCC2", 20, 18.0),
            ("FLT", 2, 16.5), ("DP_OUT", 5, 11.0), ("DM_OUT", 6, 9.5)]
    right = [("BST", 16, 25.0), ("SW", 15, 23.0), ("OUT", 17, 21.0), ("FB", 12, 19.5), ("ADJ", 7, 18.0),
             ("USB_IN", 4, 16.5), ("USB_OUT", 3, 15.0), ("CC1", 1, 13.5), ("CC2", 22, 12.3), ("DP", 9, 11.0), ("DM", 8, 9.5)]
    for name, num, py in left:
        text(d, (x0 + 0.15, py), name, FSN, halign="left")
        text(d, (x0 - 0.35, py + 0.3), str(num), 3.6, color="#777777")
    for name, num, py in right:
        text(d, (x1 - 0.15, py), name, FSN, halign="right")
        text(d, (x1 + 0.35, py + 0.3), str(num), 3.6, color="#777777")
    text(d, (32.0, yb + 0.4), "GND", FSN)
    text(d, (33.3, yb - 0.3), "18 19 21", 3.6, color="#777777")
    wire(d, [(32.0, yb), (32.0, yb - 0.8)], C_GND)
    gnd(d, (32.0, yb - 0.8))
    # Pin stubs with net labels (parts grouped below)
    for name, py in [("FREQ", 21.0), ("VCC1", 19.5), ("VCC2", 18.0), ("FLT", 16.5)]:
        wire(d, [(x0, py), (28.2, py)], C_CTL)
        netlabel(d, (28.2, py), name, C_CTL, "left")
    for name, py, col in [("OUT_F", 21.0, C_CTL), ("FB", 19.5, C_CTL), ("FBT", 18.0, C_CTL), ("VOUT", 16.5, C_5V)]:
        wire(d, [(x1, py), (35.8, py)], col)
        netlabel(d, (35.8, py), name, col)

    # ---- U1 support parts (left) -----------------------------------------------------------------
    cy = 20.4
    text(d, (14.5, 21.15), "U1 support", 4.4, color="#777777")
    netlabel(d, (10.0, cy), "FREQ", C_CTL, "left")
    wire(d, [(10.0, cy), (11.0, cy)], C_CTL)
    vpart(d, elm.Resistor, (11.0, cy), 1.4, ["R9 0R", "420 kHz"])
    netlabel(d, (14.0, cy), "VCC1", C_CTL, "left")
    wire(d, [(14.0, cy), (15.0, cy)], C_CTL)
    vpart(d, elm.Capacitor, (15.0, cy), 1.4, ["C5", "1µ"])
    netlabel(d, (18.0, cy), "VCC2", C_CTL, "left")
    wire(d, [(18.0, cy), (24.0, cy)], C_CTL)
    text(d, (21.0, cy + 0.35), "3.45 V (internal LDO)", 3.9, C_CTL)
    dot(d, (19.0, cy), C_CTL)
    vpart(d, elm.Capacitor, (19.0, cy), 1.4, ["C6", "4.7µ"])
    dot(d, (21.6, cy), C_CTL)
    vpart(d, elm.Resistor, (21.6, cy), 1.6, ["R3", "10k"], ground=False)
    vpart(d, elm.Resistor, (24.0, cy), 1.2, ["R11 1k"], ground=False)
    d += elm.LED().at((24.0, cy - 1.2)).down(1.2).color(C_GND).linewidth(0.8)
    text(d, (24.75, cy - 1.8), "D6 red", FS, halign="left", color=C_IN)
    wire(d, [(21.6, cy - 1.6), (21.6, 17.0), (24.0, 17.0), (24.0, cy - 2.4)], C_CTL)
    dot(d, (21.6, 17.0), C_CTL)
    wire(d, [(21.6, 17.0), (20.6, 17.0)], C_CTL)
    netlabel(d, (20.6, 17.0), "FLT", C_CTL, "left")
    text(d, (22.8, 16.5), "red LED on = fault", 3.9, color="#666666")

    # ---- Output: bootstrap, L1, caps, power LED --------------------------------------------------
    wire(d, [(x1, 25.0), (35.6, 25.0)], C_SW)
    hpart(d, elm.Resistor, (35.6, 25.0), 1.4, "R4", "4.7R")
    wire(d, [(37.0, 25.0), (37.4, 25.0)], C_SW)
    d += elm.Capacitor().at((37.4, 25.0)).down(2.0).color(C_GND).linewidth(0.8)
    text(d, (37.75, 24.0), "C7\n220n", FS, halign="left")
    wire(d, [(x1, 23.0), (39.2, 23.0)], C_SW)
    dot(d, (37.4, 23.0), C_SW)
    text(d, (36.1, 23.35), "SW", FSN, C_SW)
    d += elm.Inductor2(loops=4).at((39.2, 23.0)).right(2.6).color(C_GND).linewidth(0.8).label("L1", loc="top", fontsize=FS, ofst=0.1).label("4.7µH 5.5A", loc="bottom", fontsize=FS, ofst=0.1)
    wire(d, [(41.8, 23.0), (54.0, 23.0)], C_5V)
    text(d, (42.2, 23.4), "VOUT 5.03 V", FSN, C_5V, halign="left")
    for i, (ref, val, v) in enumerate([("C20", "100n", ""), ("C21", "22µ", "25V"), ("C22", "22µ", "25V"), ("C23", "22µ", "25V"), ("C24", "22µ", "25V")]):
        x = 42.8 + 1.9 * i
        dot(d, (x, 23.0), C_5V)
        vpart(d, elm.Capacitor, (x, 23.0), 1.8, [ref, val, v] if v else [ref, val])
    dot(d, (52.4, 23.0), C_5V)
    vpart(d, elm.Resistor, (52.4, 23.0), 1.2, ["R10 1k"], ground=False)
    d += elm.LED().at((52.4, 21.8)).down(1.2).color(C_GND).linewidth(0.8)
    text(d, (53.15, 21.2), "D5 white", FS, halign="left", color=C_5V)
    gnd(d, (52.4, 20.6))
    netlabel(d, (54.0, 23.0), "VOUT", C_5V)

    # ---- Feedback and OUT sense (right) ----------------------------------------------------------
    fy = 18.8
    netlabel(d, (38.8, fy), "FB", C_CTL, "left")
    wire(d, [(38.8, fy), (39.0, fy)], C_CTL)
    hpart(d, elm.Resistor, (39.0, fy), 1.4, "R6", "20k")
    wire(d, [(40.4, fy), (42.2, fy)], C_CTL)
    dot(d, (41.4, fy), C_CTL)
    d += elm.Resistor().at((42.2, fy)).right(1.6).color(C_GND).linewidth(0.8).label("R7 30k 1%", loc="bottom", fontsize=FS, ofst=0.08)
    wire(d, [(43.8, fy), (44.6, fy)], C_CTL)
    netlabel(d, (44.6, fy), "VOUT", C_5V)
    wire(d, [(41.4, fy), (41.4, fy + 0.9), (42.5, fy + 0.9)], C_CTL)
    d += elm.Capacitor().at((42.5, fy + 0.9)).right(0.7).color(C_GND).linewidth(0.8)
    wire(d, [(43.2, fy + 0.9), (44.2, fy + 0.9), (44.2, fy)], C_CTL)
    dot(d, (44.2, fy), C_CTL)
    text(d, (42.85, fy + 1.4), "C26 47p", FS - 0.3)
    wire(d, [(41.4, fy), (41.4, fy - 0.6)], C_CTL)
    vpart(d, elm.Resistor, (41.4, fy - 0.6), 1.4, ["R8", "5.6k 1%"])
    text(d, (40.85, fy - 1.25), "FBT\n(ADJ)", FSN, C_CTL, halign="right")
    netlabel(d, (48.8, fy), "VOUT", C_5V, "left")
    wire(d, [(48.8, fy), (49.0, fy)], C_5V)
    hpart(d, elm.Resistor, (49.0, fy), 1.4, "R5", "10R")
    wire(d, [(50.4, fy), (51.4, fy)], C_CTL)
    dot(d, (51.0, fy), C_CTL)
    vpart(d, elm.Capacitor, (51.0, fy), 1.3, ["C25", "220n"])
    netlabel(d, (51.4, fy), "OUT_F", C_CTL)

    # ---- USB-C side: fan-out to J3 ---------------------------------------------------------------
    jx, jy0, jy1 = 49.0, 3.4, 16.5
    box(d, jx, jy0, jx + 4.6, jy1)
    text(d, (jx + 2.3, 16.05), "J3  USB-C", FS + 0.2, halign="center")
    wire(d, [(x1, 15.0), (jx, 15.0)], C_5V)
    text(d, (38.0, 15.35), "VBUS (on only when a phone is attached)", FSN, C_5V, halign="left")
    dot(d, (46.2, 15.0), C_5V)
    vpart(d, elm.Capacitor, (46.2, 15.0), 1.2, ["C27", "10µ 50V"])
    wire(d, [(x1, 13.5), (40.0, 13.5), (40.0, 12.6), (jx, 12.6)], C_CC)
    dot(d, (44.6, 12.6), C_CC)
    vpart(d, elm.Capacitor, (44.6, 12.6), 1.0, ["C28 2.2n"])
    wire(d, [(x1, 12.3), (39.4, 12.3), (39.4, 10.2), (jx, 10.2)], C_CC)
    wire(d, [(x1, 11.0), (38.8, 11.0), (38.8, 8.0), (jx, 8.0)], C_DATA)
    wire(d, [(x1, 9.5), (38.2, 9.5), (38.2, 5.6), (jx, 5.6)], C_DATA)
    dot(d, (45.4, 8.0), C_DATA)
    # Unidirectional ESD diodes: cathode on the data line
    e = elm.Zener().at((45.4, 8.0)).down(1.2).reverse().color(C_GND).linewidth(0.8)
    d += e
    gnd(d, e.end)
    text(d, (45.8, 7.4), "D3 ESD", FS, halign="left")
    dot(d, (44.2, 5.6), C_DATA)
    e = elm.Zener().at((44.2, 5.6)).down(1.2).reverse().color(C_GND).linewidth(0.8)
    d += e
    gnd(d, e.end)
    text(d, (44.6, 4.9), "D4 ESD", FS, halign="left")
    text(d, (40.6, 3.6), "D3/D4 PESD5V0U1UA", 3.8, color="#666666")
    for name, py in [("VBUS  A4 B4 A9 B9", 15.0), ("CC1  A5", 12.6), ("CC2  B5", 10.2), ("D+  A6 B6", 8.0), ("D−  A7 B7", 5.6)]:
        text(d, (jx + 0.2, py), name, FSN - 0.2, halign="left")
    text(d, (jx + 2.3, 4.0), "GND, SHIELD", FSN - 0.2)
    wire(d, [(jx + 2.3, jy0), (jx + 2.3, 2.9)], C_GND)
    gnd(d, (jx + 2.3, 2.9))
    text(d, (39.6, 12.95), "CC1", FSN, C_CC, halign="left")
    text(d, (39.6, 10.55), "CC2", FSN, C_CC, halign="left")
    text(d, (40.4, 8.35), "D+ (DP_C)", FSN, C_DATA, halign="left")
    text(d, (40.4, 5.95), "D− (DM_C)", FSN, C_DATA, halign="left")

    # ---- USB-B side from the stereo --------------------------------------------------------------
    bx0, bx1, by0, by1 = 3.0, 8.0, 6.4, 13.4
    box(d, bx0, by0, bx1, by1)
    text(d, (5.5, 14.5), "J2  USB-B ← stereo console\nUSB-A (A–B cable, USB 2.0)", FS, halign="center")
    for name, py in [("1 VBUS n.c.", 12.6), ("3 D+", 11.0), ("2 D−", 9.5), ("4 GND", 8.0), ("SHIELD", 7.0)]:
        text(d, (bx1 - 0.2, py), name, FSN - 0.2, halign="right")
    wire(d, [(bx1, 12.6), (8.5, 12.6)], C_GND)
    text(d, (8.85, 12.6), "×", 6.5)
    wire(d, [(bx1, 11.0), (12.0, 11.0)], C_DATA)
    hpart(d, elm.Resistor, (12.0, 11.0), 1.4, "L4", "0R")
    wire(d, [(13.4, 11.0), (x0, 11.0)], C_DATA)
    wire(d, [(bx1, 9.5), (15.0, 9.5)], C_DATA)
    hpart(d, elm.Resistor, (15.0, 9.5), 1.4, "L3", "0R")
    wire(d, [(16.4, 9.5), (x0, 9.5)], C_DATA)
    text(d, (22.5, 11.35), "D+ (DP_S → DP_H)", FSN, C_DATA)
    text(d, (22.5, 9.15), "D− (DM_S → DM_H)", FSN, C_DATA)
    dot(d, (9.4, 11.0), C_DATA)
    dot(d, (10.4, 9.5), C_DATA)
    wire(d, [(9.4, 11.0), (9.4, 10.65)], "#999999")
    d += elm.Capacitor().at((9.4, 10.65)).down(0.5).color("#999999").linestyle("--").linewidth(0.7)
    wire(d, [(9.4, 10.15), (9.4, 9.95), (10.4, 9.95), (10.4, 9.5)], "#999999")
    text(d, (9.0, 11.45), "C29 3.3p DNP", 3.6, color="#888888", halign="left")
    wire(d, [(bx1, 8.0), (8.8, 8.0), (8.8, 7.0), (bx1, 7.0)], C_GND)
    wire(d, [(8.8, 7.0), (8.8, 6.4)], C_GND)
    gnd(d, (8.8, 6.4))
    text(d, (19.0, 7.2), "The stereo is the USB host. U1 passes D+/D− through as a BC1.2 CDP port\n"
                         "and closes its switch only after a phone is detected on CC1/CC2.", 4.1, color="#555555")
    d.draw(show=False)
    return d


def page1(pdf):
    fig = plt.figure(figsize=A5)
    ax = fig.add_axes([0.012, 0.29, 0.976, 0.69])
    schematic(ax)
    ax.set_xlim(-1.0, 57.0)
    ax.set_ylim(1.6, 27.3)
    ax.set_aspect("equal")
    ax.axis("off")
    # Frame
    fig.add_artist(Rectangle((0.008, 0.012), 0.984, 0.976, transform=fig.transFigure, fill=False, lw=0.9, color=C_GND))
    # Notes, ratings, title block
    y0 = 0.025
    def boxed(x, w, h, title, lines, size=5.0):
        fig.add_artist(Rectangle((x, y0), w, h, transform=fig.transFigure, fill=False, lw=0.6, color=C_GND))
        fig.text(x + 0.006, y0 + h - 0.022, title, fontsize=5.8, fontweight="bold", va="top")
        fig.text(x + 0.006, y0 + h - 0.05, "\n".join(lines), fontsize=size, va="top", linespacing=1.32)
    boxed(0.016, 0.395, 0.255, "IN THE CAR — CONNECTIONS", [
        "J1 +12V  ← fuse tap on an ACC (switched) fuse, 5 A fuse. Swift: fuse 9 ACC-2 or 15 ACC.",
        "J1 GND   → body ground at the stereo's ground point (solid, short).",
        "J2 USB-B ← stereo console USB-A socket, USB 2.0 A–B cable (stereo 5 V unused).",
        "J3 USB-C → full-featured USB-C extension (CC1/CC2 separate) → phone.",
        "LEDs: WHITE = 5 V output on.   RED = fault (overload, short, over-voltage,",
        "          over-temperature); clears itself when the fault goes.",
        "VBUS on J3 reads 0 V until a phone is attached (normal Type-C behaviour).",
    ], 4.75)
    boxed(0.418, 0.27, 0.255, "RATINGS", [
        "Input: 12 V car supply; on above ≈6.1 V, off below ≈5.5 V",
        "Max input 36 V continuous (U1 40 V abs.)",
        "Protection: D1 TVS 33 V bidirectional,",
        "   D2 reverse-polarity block, 5 A fuse",
        "Output: 5.03 V, 3 A (15 W), Type-C Rp 3 A,",
        "   BC1.2 CDP, cable-drop comp. +0.18 V at 3 A",
        "   VOUT = 0.792 V × (1 + R7/R8) + R7 × 2.05 µA/A × I",
        "Switching 420 kHz, spread spectrum; no USB PD",
        "Wire colours: red 12 V, purple SW, orange 5 V,",
        "   blue USB data, teal CC, green control",
    ], 4.75)
    tx, tw, th = 0.695, 0.289, 0.255
    fig.add_artist(Rectangle((tx, y0), tw, th, transform=fig.transFigure, fill=False, lw=0.9, color=C_GND))
    fig.text(tx + 0.008, y0 + th - 0.02, "SWIFT USB-C 3A", fontsize=10.5, fontweight="bold", va="top")
    fig.text(tx + 0.008, y0 + th - 0.075, "Car 12 V → USB-C 5 V 3 A charger with\nstereo USB data pass-through (iPod protocol)",
             fontsize=5.2, va="top", linespacing=1.3)
    rows = [("Vehicle", "2011 Suzuki Swift"), ("Board", "swift-usbc-3a, 4-layer, 52 × 40 mm"), ("Rev", "v1"),
            ("Date", "07/10/2026"), ("Sheet", "1 of 2 (schematic)"), ("Source", "KiCad: ~/kicad/swift-usbc-3a")]
    for i, (k, v) in enumerate(rows):
        yy = y0 + th - 0.135 - i * 0.02
        fig.text(tx + 0.008, yy, k, fontsize=4.9, color="#555555", va="top")
        fig.text(tx + 0.06, yy, v, fontsize=4.9, va="top")
    pdf.savefig(fig)
    plt.close(fig)


def page2(pdf):
    rows = list(csv.DictReader(open(os.path.join(ROOT, "fab", "assembly", "swift-usbc-3a-with-tht-bom-jlc.csv"))))
    role = {"C1": "input bulk", "C2": "input, at U1", "C4": "decoupling", "C5": "VCC1", "C6": "VCC2",
            "C7": "bootstrap / OUT filter", "C11": "input filter", "C14": "input filter / VBUS", "C21": "output",
            "C26": "feed-forward", "C28": "CC1 filter", "D1": "TVS 33 V bidirectional", "D2": "reverse block",
            "D3": "ESD on D+/D−", "D5": "power LED", "D6": "fault LED", "J1": "12 V input", "J2": "from stereo",
            "J3": "to phone", "L1": "buck inductor", "L2": "input filter", "L3": "0 Ω links (D+/D−, FREQ)",
            "R1": "EN divider", "R2": "EN divider", "R3": "FLT pull-up", "R4": "bootstrap", "R5": "OUT filter",
            "R6": "FB (RT)", "R7": "VOUT set", "R8": "VOUT set", "R10": "LED resistors", "U1": "buck + USB switch"}
    pkg = {"CP_Elec_8x10.5": "Ø8 × 10.5 mm SMD", "L_APV_ANR6045": "6 × 6 mm", "L_Changjiang_FTC303020D": "3 × 3 mm",
           "MPS_QFN-22_4x4mm_P0.5mm": "QFN-22 4 × 4 mm", "D_SMB": "SMB", "D_SMA": "SMA", "D_SOD-323": "SOD-323",
           "USB_B_OST_USB-B1HSxx_Horizontal": "USB-B, through-hole",
           "USB_C_Receptacle_HRO_TYPE-C-31-M-12": "USB-C 16-pin SMD",
           "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal": "5.08 mm 2-pin, through-hole"}
    table = []
    for r in rows:
        refs = r["Designator"].split(",")
        fp = r["Footprint"]
        p = pkg.get(fp, fp.split("_")[1] if fp.startswith(("C_", "R_", "L_", "LED_")) else fp)
        val = r["Comment"].replace("uF", "µF").replace("uH", "µH").replace("MPQ4228GRE-C-AEC1", "MPQ4228-C")
        table.append((", ".join(refs), val, p, r["LCSC Part #"], role.get(refs[0], "")))
    table.sort(key=lambda t: (t[0][0], int("".join(c for c in t[0].split(",")[0][1:] if c.isdigit()) or 0)))
    fig = plt.figure(figsize=A5)
    fig.add_artist(Rectangle((0.008, 0.012), 0.984, 0.976, transform=fig.transFigure, fill=False, lw=0.9, color=C_GND))
    fig.text(0.02, 0.965, "SWIFT USB-C 3A — PARTS LIST (as assembled by JLCPCB, 07/10/2026)", fontsize=8, fontweight="bold", va="top")
    fig.text(0.98, 0.965, "Sheet 2 of 2", fontsize=5.5, va="top", ha="right", color="#555555")
    fig.text(0.02, 0.93, "C29 (3.3 pF) not fitted.  L3/L4 fitted as 0 Ω links (18 nH optional).  J1/J2 hand-soldered by JLCPCB.  "
             "Parts from LCSC (lcsc.com/product-detail/<LCSC>.html).", fontsize=5, va="top", color="#444444")
    cols = [("Ref", 0.0), ("Value", 0.17), ("Package", 0.36), ("LCSC", 0.62), ("Role", 0.75)]
    half = (len(table) + 1) // 2
    for c, (x_off, chunk) in enumerate([(0.02, table[:half]), (0.51, table[half:])]):
        top = 0.89
        for name, cx in cols:
            fig.text(x_off + cx * 0.47, top, name, fontsize=5.3, fontweight="bold", va="top")
        fig.add_artist(plt.Line2D([x_off, x_off + 0.465], [top - 0.027, top - 0.027], transform=fig.transFigure, lw=0.5, color=C_GND))
        for i, row in enumerate(chunk):
            yy = top - 0.04 - i * 0.0505
            if i % 2 == 0:
                fig.add_artist(Rectangle((x_off - 0.003, yy - 0.04), 0.47, 0.05, transform=fig.transFigure, color="#f1f1f1", lw=0))
            for (name, cx), val in zip(cols, row):
                fig.text(x_off + cx * 0.47, yy - 0.012, val[:34], fontsize=4.9, va="top")
    pdf.savefig(fig)
    plt.close(fig)


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with PdfPages(OUT) as pdf:
        page1(pdf)
        page2(pdf)
        info = pdf.infodict()
        info["Title"] = "Swift USB-C 3A schematic (A5)"
        info["Subject"] = "swift-usbc-3a rev v1"
    print("wrote", OUT)


main()
