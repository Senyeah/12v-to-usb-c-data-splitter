"""Copy symbol fields, DNP and BOM flags and no-connect nets from a kicad-cli XML netlist onto the board."""
import sys
import xml.etree.ElementTree as ET
import pcbnew

board_path, netlist_path = sys.argv[1], sys.argv[2]
board = pcbnew.LoadBoard(board_path)
root = ET.parse(netlist_path).getroot()
fps = {fp.GetReference(): fp for fp in board.GetFootprints()}

for comp in root.find('components').findall('comp'):
    fp = fps.get(comp.get('ref'))
    if fp is None:
        continue
    fp.SetValue(comp.findtext('value') or '')
    for f in comp.find('fields').findall('field'):
        name = f.get('name')
        if name == 'Footprint':
            continue
        fp.SetField(name, f.text or '')
        if name not in ('Reference', 'Value'):
            field = fp.GetField(name)
            field.SetVisible(False)
            field.SetLayer(pcbnew.F_Fab)
    props = {p.get('name') for p in comp.findall('property')}
    fp.SetDNP('dnp' in props)
    fp.SetExcludedFromBOM('exclude_from_bom' in props)

for net in root.find('nets').findall('net'):
    name = net.get('name')
    info = board.FindNet(name)
    if info is None:
        info = pcbnew.NETINFO_ITEM(board, name)
        board.Add(info)
    for node in net.findall('node'):
        fp = fps.get(node.get('ref'))
        if fp is None:
            continue
        for pad in fp.Pads():
            if pad.GetNumber() == node.get('pin') and pad.GetNetname() != name:
                pad.SetNet(info)

board.Save(board_path)
print("synced", len(fps), "footprints")
