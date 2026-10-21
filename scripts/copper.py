"""Power zones, hand-routed QFN fan-out, keepouts and GND fills for swift-usbc-3a.

Run: copper.py <board> --routing  (before Freerouting: keepouts over power copper, no GND fills)
     copper.py <board>            (after Freerouting: GND fills on all layers, island stitching)
"""
import sys
import pcbnew

MM = pcbnew.FromMM
BOARD = [(99, 100), (151, 100), (151, 140), (99, 140)]

# (net, layer, priority, polygon)
ZONES = [
    ("SW", "F.Cu", 3, [(124.0, 117.62), (125.35, 117.62), (125.35, 116.0), (128.3, 116.0), (128.3, 113.0), (133.4, 113.0),
                       (133.4, 119.4), (130.8, 119.4), (130.8, 117.95), (124.0, 117.95)]),
    ("VIN1", "F.Cu", 3, [(124.0, 118.12), (125.6, 118.12), (126.5, 119.0), (126.5, 120.5), (127.15, 120.5), (127.15, 122.7),
                         (132.6, 122.7), (132.6, 124.9), (126.0, 124.9), (126.0, 120.55), (125.4, 120.55), (125.4, 118.4),
                         (124.0, 118.4)]),
    ("VOUT", "F.Cu", 2, [(121.0, 107.9), (138.0, 107.9), (138.0, 119.6), (135.9, 119.6), (135.9, 110.3), (133.0, 110.3),
                         (133.0, 111.6), (131.5, 111.6), (131.5, 110.3), (124.6, 110.3), (124.6, 112.75), (123.35, 112.75),
                         (123.35, 110.3), (121.0, 110.3), (121.0, 111.3), (119.75, 111.3), (119.75, 109.45), (121.0, 109.45)]),
    ("VBUS", "F.Cu", 2, [(114.8, 116.5), (118.35, 116.5), (118.35, 117.88), (114.8, 117.88)]),
    ("VOUT", "F.Cu", 2, [(116.4, 118.12), (118.35, 118.12), (118.35, 119.45), (116.4, 119.45)]),
    ("VBAT_IN", "F.Cu", 2, [(145.0, 103.6), (150.6, 103.6), (150.6, 115.7), (142.8, 115.7), (142.8, 112.9), (145.0, 112.9)]),
    # Bends round the C11-C14 GND pads, which sit between D2 and the VIN_F cap row.
    ("VIN_F", "F.Cu", 2, [(143.1, 117.0), (145.3, 117.0), (145.3, 119.6), (146.4, 119.6), (146.4, 122.75), (148.8, 122.75),
                          (148.8, 125.0), (144.1, 125.0), (144.1, 129.0), (141.5, 129.0), (141.5, 125.0), (139.8, 125.0),
                          (139.8, 122.75), (145.0, 122.75), (145.0, 119.9), (143.1, 119.9)]),
    ("VIN1", "F.Cu", 2, [(144.4, 125.6), (146.8, 125.6), (146.8, 131.0), (142.8, 131.0), (142.8, 136.2), (137.7, 136.2),
                         (137.7, 129.4), (144.4, 129.4)]),
    ("VOUT", "In2.Cu", 2, [(116.4, 107.9), (138.0, 107.9), (138.0, 119.6), (135.9, 119.6), (135.9, 110.3), (118.4, 110.3),
                           (118.4, 119.45), (116.4, 119.45)]),
    ("VIN1", "In2.Cu", 2, [(125.6, 118.5), (127.0, 118.5), (127.0, 120.6), (134.4, 120.6), (134.4, 129.0), (143.4, 129.0),
                           (143.4, 132.2), (125.6, 132.2)]),
    # Parallels the 0.5 oz In2 VOUT strip to U1 USB_IN with 1 oz outer copper.
    ("VOUT", "B.Cu", 2, [(116.6, 110.9), (118.4, 110.9), (118.4, 119.3), (117.25, 119.3), (117.25, 116.35), (116.6, 116.35)]),
    ("VBUS", "B.Cu", 2, [(114.6, 116.6), (117.0, 116.6), (117.0, 117.8), (116.4, 117.8), (116.4, 128.6), (118.6, 128.6),
                         (118.6, 129.8), (108.2, 129.8), (108.2, 128.6), (114.6, 128.6)]),
]

# (net, layer, width, points)
TRACKS = [
    ("SW", "F.Cu", 0.25, [(123.6, 117.75), (124.6, 117.75)]),
    ("VIN1", "F.Cu", 0.25, [(123.6, 118.25), (124.6, 118.25)]),
    ("BST", "F.Cu", 0.2, [(124.2, 117.25), (124.95, 117.25), (124.95, 115.4), (125.78, 114.6)]),
    ("BST_C", "F.Cu", 0.25, [(127.42, 114.6), (128.1, 114.6), (128.88, 115.38), (129.4, 115.38)]),
    ("OUT_F", "F.Cu", 0.2, [(124.2, 116.75), (124.45, 116.5), (124.45, 113.4), (125.62, 113.0), (125.62, 112.2)]),
    ("OUT_F", "F.Cu", 0.25, [(125.62, 112.2), (127.33, 112.2)]),
    ("VCC2", "F.Cu", 0.25, [(122.0, 115.8), (122.0, 115.2), (122.4, 114.8), (122.4, 113.97)]),
    ("GND", "F.Cu", 0.2, [(122.5, 115.8), (123.1, 115.0)]),
    ("GND", "F.Cu", 0.2, [(123.0, 115.8), (123.1, 115.0)]),
    ("GND", "F.Cu", 0.2, [(121.5, 115.8), (121.3, 115.0)]),
    ("CC2", "F.Cu", 0.2, [(121.0, 115.8), (120.35, 115.0)]),
    ("CC1", "F.Cu", 0.2, [(119.8, 116.75), (119.3, 116.75), (119.3, 116.0)]),
    ("FLT", "F.Cu", 0.2, [(119.8, 117.25), (118.75, 117.25), (118.75, 116.3), (118.3, 115.85)]),
    ("VBUS", "F.Cu", 0.25, [(119.8, 117.75), (118.2, 117.75)]),
    ("VOUT", "F.Cu", 0.25, [(119.8, 118.25), (118.2, 118.25)]),
    ("DP_H", "F.Cu", 0.2, [(119.8, 118.75), (118.75, 118.75), (118.75, 119.85), (114.2, 119.85), (114.2, 120.61)]),
    ("DM_H", "F.Cu", 0.2, [(119.8, 119.25), (119.25, 119.25), (119.25, 120.61), (116.0, 120.61)]),
    ("EN", "F.Cu", 0.2, [(124.2, 118.75), (124.95, 118.95)]),
    ("EN", "B.Cu", 0.25, [(124.95, 118.95), (125.6, 119.6), (132.0, 120.7)]),
    ("EN", "F.Cu", 0.2, [(132.0, 120.7), (132.0, 121.58), (133.8, 123.22)]),
    ("FB", "F.Cu", 0.2, [(124.2, 119.25), (124.85, 119.75)]),
    ("FB", "B.Cu", 0.2, [(124.85, 119.75), (125.17, 124.85)]),
    ("FB", "F.Cu", 0.2, [(125.17, 124.85), (125.17, 125.8)]),
    # Divider top senses VOUT at the output caps, not at R10.
    ("VOUT", "F.Cu", 0.3, [(130.38, 127.6), (130.43, 125.8), (135.0, 125.8)]),
    ("VOUT", "B.Cu", 0.3, [(135.0, 125.8), (135.0, 110.0)]),
    ("VBUS", "F.Cu", 0.5, [(108.55, 131.8), (108.55, 129.2)]),
    ("VBUS", "F.Cu", 0.5, [(113.45, 131.8), (113.45, 129.2)]),
    ("VBUS", "F.Cu", 0.5, [(117.8, 129.3), (117.8, 130.88)]),
    ("GND", "F.Cu", 0.4, [(127.38, 119.8), (128.0, 120.5), (128.0, 121.65), (130.0, 121.65)]),
    ("GND", "F.Cu", 0.4, [(133.78, 111.0), (133.78, 112.1)]),
    ("GND", "F.Cu", 0.4, [(128.88, 112.2), (129.9, 112.2)]),
    ("GND", "F.Cu", 0.4, [(117.8, 127.92), (119.1, 127.9)]),
    ("GND", "F.Cu", 0.4, [(127.38, 119.8), (127.53, 118.9)]),
    ("GND", "F.Cu", 0.3, [(109.6, 127.55), (109.0, 127.55)]),
    ("GND", "F.Cu", 0.3, [(112.4, 127.55), (111.8, 127.55)]),
    ("GND", "F.Cu", 0.4, [(148.4, 118.55), (147.9, 120.15), (147.6, 121.12)]),
    ("GND", "F.Cu", 0.5, [(146.6, 135.0), (146.6, 136.4)]),
    ("GND", "F.Cu", 0.5, [(148.8, 135.0), (148.8, 136.4)]),
] + [("GND", "F.Cu", 0.5, [(x, 106.12), (x, 104.9)]) for x in (122.2, 125.0, 127.8, 130.6)] \
  + [("GND", "F.Cu", 0.4, [(x, 121.83), (x, 120.8)]) for x in (140.6, 142.4, 144.2)]

# (net, x, y, diameter, drill)
VIAS = [
    ("GND", 123.1, 115.0, 0.5, 0.3), ("GND", 121.3, 115.0, 0.5, 0.3),
    ("CC2", 120.35, 115.0, 0.5, 0.3), ("CC1", 119.3, 116.0, 0.5, 0.3),
    ("EN", 124.95, 118.95, 0.5, 0.3), ("EN", 132.0, 120.7, 0.5, 0.3),
    ("FB", 124.85, 119.75, 0.5, 0.3), ("FB", 125.17, 124.85, 0.5, 0.3),
    ("VOUT", 135.0, 125.8, 0.6, 0.3), ("VOUT", 135.0, 110.0, 0.6, 0.3),
    ("VBUS", 115.2, 117.2, 0.6, 0.3), ("VBUS", 115.85, 117.2, 0.6, 0.3), ("VBUS", 116.5, 117.2, 0.6, 0.3),
    ("VBUS", 108.55, 129.2, 0.6, 0.3), ("VBUS", 113.45, 129.2, 0.6, 0.3), ("VBUS", 117.8, 129.3, 0.6, 0.3),
    ("VOUT", 117.95, 111.45, 0.6, 0.3), ("VOUT", 118.0, 112.4, 0.6, 0.3),
    ("VOUT", 116.8, 118.8, 0.6, 0.3), ("VOUT", 117.45, 118.8, 0.6, 0.3), ("VOUT", 118.05, 118.8, 0.6, 0.3),
    ("VOUT", 123.6, 109.95, 0.6, 0.3), ("VOUT", 126.4, 109.95, 0.6, 0.3), ("VOUT", 129.2, 109.95, 0.6, 0.3),
    ("VOUT", 132.0, 109.95, 0.6, 0.3), ("VOUT", 136.9, 111.5, 0.6, 0.3), ("VOUT", 136.9, 112.6, 0.6, 0.3),
    ("VIN1", 126.0, 118.95, 0.6, 0.3), ("VIN1", 126.6, 124.4, 0.6, 0.3), ("VIN1", 128.9, 124.5, 0.6, 0.3),
    ("VIN1", 131.0, 124.5, 0.6, 0.3),
    ("VIN1", 139.0, 131.0, 0.6, 0.3), ("VIN1", 140.6, 131.0, 0.6, 0.3), ("VIN1", 142.2, 131.0, 0.6, 0.3),
    ("GND", 128.9, 121.65, 0.5, 0.3), ("GND", 133.78, 112.1, 0.6, 0.3), ("GND", 129.9, 112.2, 0.6, 0.3),
    ("GND", 119.1, 127.9, 0.6, 0.3), ("GND", 147.9, 120.15, 0.6, 0.3),
    ("GND", 146.6, 136.4, 0.6, 0.3), ("GND", 148.8, 136.4, 0.6, 0.3),
    ("GND", 120.16, 121.97, 0.5, 0.3), ("GND", 123.86, 125.17, 0.5, 0.3),
    # Review fixes: C4 hot-loop return, ESD diode returns, U1 heat path to In1.
    ("GND", 127.53, 118.9, 0.6, 0.3), ("GND", 109.0, 127.55, 0.5, 0.3), ("GND", 111.8, 127.55, 0.5, 0.3),
    ("GND", 123.35, 114.4, 0.5, 0.3), ("GND", 123.6, 115.3, 0.5, 0.3),
    ("GND", 123.65, 120.65, 0.6, 0.3), ("GND", 119.65, 115.3, 0.6, 0.3), ("GND", 120.2, 121.3, 0.6, 0.3),
    ("GND", 118.95, 114.65, 0.6, 0.3), ("GND", 123.4, 113.55, 0.6, 0.3),
] + [("GND", x, 104.9, 0.6, 0.3) for x in (122.2, 125.0, 127.8, 130.6)] \
  + [("GND", x, 120.8, 0.6, 0.3) for x in (140.6, 142.4, 144.2)]

# Tracks/vias made here use widths ending in this many nanometres, so re-runs can find them.
MANUAL_TAG = 7


def find_net(board, name):
    # Schematic local labels give sheet-scoped names ("/VIN1").
    return board.FindNet("/" + name) or board.FindNet(name)


def short(item):
    return item.GetNetname().lstrip("/")


def pt(x, y):
    return pcbnew.VECTOR2I(MM(x), MM(y))


def tagged(mm):
    return MM(mm) + MANUAL_TAG


def outline(z, poly):
    o = z.Outline()
    o.NewOutline()
    for x, y in poly:
        o.Append(MM(x), MM(y))


def add_zone(board, net, layer, priority, poly, connection, min_w=0.2, clearance=0.15):
    z = pcbnew.ZONE(board)
    z.SetLayer(board.GetLayerID(layer))
    z.SetNetCode(find_net(board, net).GetNetCode())
    z.SetAssignedPriority(priority)
    z.SetPadConnection(connection)
    z.SetMinThickness(MM(min_w))
    z.SetLocalClearance(MM(clearance))
    z.SetThermalReliefGap(MM(0.3))
    z.SetThermalReliefSpokeWidth(MM(0.4))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    outline(z, poly)
    board.Add(z)


def add_keepout(board, layer, poly):
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetLayer(board.GetLayerID(layer))
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowZoneFills(False)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    outline(z, poly)
    board.Add(z)


def stitch_islands(board, min_area_mm2=1.0, depth_mm=0.55, pitch_mm=2.0):
    """Add GND vias to fill islands on F.Cu/In2/B.Cu that have no via or THT pad to the plane.

    A candidate must sit depth_mm inside the GND fill on every copper layer, which keeps it
    clear of all other nets without a separate clearance check.
    """
    gnd = [z for z in board.Zones() if short(z) == "GND" and not z.GetIsRuleArea()]
    layers = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
    fills = {l: [z.GetFilledPolysList(l) for z in gnd if z.IsOnLayer(l)] for l in layers}
    depth2 = MM(depth_mm) ** 2

    def deep_in(layer, p):
        for f in fills[layer]:
            for i in range(f.OutlineCount()):
                if not f.Outline(i).PointInside(p):
                    continue
                if any(f.Hole(i, j).PointInside(p) for j in range(f.HoleCount(i))):
                    continue
                edges = [f.Outline(i)] + [f.Hole(i, j) for j in range(f.HoleCount(i))]
                return all(e.SquaredDistance(p, True) >= depth2 for e in edges)
        return False

    anchors = [t.GetPosition() for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and short(t) == "GND"]
    anchors += [p.GetPosition() for fp in board.GetFootprints() for p in fp.Pads()
                if short(p) == "GND" and p.HasHole()]
    added = []
    for layer in (pcbnew.F_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
        for f in fills[layer]:
            for i in range(f.OutlineCount()):
                island = pcbnew.SHAPE_POLY_SET()
                island.AddOutline(f.Outline(i))
                for j in range(f.HoleCount(i)):
                    island.AddHole(f.Hole(i, j))
                if island.Area() / 1e12 < min_area_mm2 or any(island.Contains(a) for a in anchors + added):
                    continue
                bb = f.Outline(i).BBox()
                want = max(1, min(6, int(island.Area() / 1e12 / 15)))
                placed = []
                step = MM(0.2)
                for y in range(bb.GetTop(), bb.GetBottom(), step):
                    for x in range(bb.GetLeft(), bb.GetRight(), step):
                        p = pcbnew.VECTOR2I(x, y)
                        if not island.Contains(p) or any((p - q).EuclideanNorm() < MM(pitch_mm) for q in placed):
                            continue
                        if all(deep_in(l, p) for l in layers):
                            placed.append(p)
                            if len(placed) >= want:
                                break
                    if len(placed) >= want:
                        break
                for p in placed:
                    v = pcbnew.PCB_VIA(board)
                    v.SetViaType(pcbnew.VIATYPE_THROUGH)
                    v.SetPosition(p)
                    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                    v.SetWidth(tagged(0.5))
                    v.SetDrill(MM(0.3))
                    v.SetNet(find_net(board, "GND"))
                    board.Add(v)
                added += placed
    return added


def main(path, routing):
    board = pcbnew.LoadBoard(path)
    board.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    # SES import brings back untagged copies of our items, so match on geometry as well as the tag
    via_keys = {(n, round(x, 3), round(y, 3)) for n, x, y, _, _ in VIAS}
    trk_keys = set()
    for n, layer, _, pts in TRACKS:
        for a, b in zip(pts, pts[1:]):
            trk_keys.add((n, layer, tuple(sorted([(round(a[0], 3), round(a[1], 3)), (round(b[0], 3), round(b[1], 3))]))))

    def is_manual(t):
        if t.GetWidth() % 1000 == MANUAL_TAG:
            return True
        p = lambda v: (round(pcbnew.ToMM(v.x), 3), round(pcbnew.ToMM(v.y), 3))
        if t.Type() == pcbnew.PCB_VIA_T:
            return (short(t),) + p(t.GetPosition()) in via_keys
        key = (short(t), board.GetLayerName(t.GetLayer()), tuple(sorted([p(t.GetStart()), p(t.GetEnd())])))
        return key in trk_keys

    # In2 traces leave J2 pin 4 too few thermal spokes.
    for p in board.FindFootprintByReference("J2").Pads():
        if p.GetNumber() == "4":
            p.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)

    stale = [t for t in board.GetTracks() if is_manual(t)]
    zones = [z for z in board.Zones()]
    for item in stale + zones:
        board.Remove(item)

    full = pcbnew.ZONE_CONNECTION_FULL
    tht = pcbnew.ZONE_CONNECTION_THT_THERMAL
    for net, layer, prio, poly in ZONES:
        add_zone(board, net, layer, prio, poly, full)
    add_zone(board, "GND", "In1.Cu", 0, BOARD, full, min_w=0.25, clearance=0.2)
    if routing:
        for _, layer, _, poly in ZONES:
            add_keepout(board, layer, poly)
    else:
        for layer in ("F.Cu", "In2.Cu", "B.Cu"):
            add_zone(board, "GND", layer, 0, BOARD, tht, min_w=0.25, clearance=0.2)

    for net, layer, width, pts in TRACKS:
        n = find_net(board, net)
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pt(x1, y1))
            t.SetEnd(pt(x2, y2))
            t.SetWidth(tagged(width))
            t.SetLayer(board.GetLayerID(layer))
            t.SetNet(n)
            t.SetLocked(True)
            board.Add(t)
    for net, x, y, dia, drill in VIAS:
        v = pcbnew.PCB_VIA(board)
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetPosition(pt(x, y))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetWidth(tagged(dia))
        v.SetDrill(MM(drill))
        v.SetNet(find_net(board, net))
        v.SetLocked(True)
        board.Add(v)

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    if not routing:
        stitched = stitch_islands(board)
        print(f"stitching vias added: {len(stitched)}")
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.Save(path)
    print(f"zones={len(list(board.Zones()))} tracks/vias={len(list(board.GetTracks()))} routing={routing}")


if __name__ == "__main__":
    main(sys.argv[1], "--routing" in sys.argv)
