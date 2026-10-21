"""Rename board nets to the schematic's sheet-local names (VIN1 -> /VIN1) so parity passes."""
import sys
import xml.etree.ElementTree as ET
import pcbnew

board = pcbnew.LoadBoard(sys.argv[1])
names = {n.get('name') for n in ET.parse(sys.argv[2]).getroot().find('nets').findall('net')}
done = 0
for name, net in list(board.GetNetsByName().items()):
    name = str(name)
    if name and '/' + name in names and board.FindNet('/' + name) is None:
        net.SetNetname('/' + name)
        done += 1
board.Save(sys.argv[1])
print('renamed', done)
