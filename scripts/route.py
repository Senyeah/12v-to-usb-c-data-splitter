"""Export Specctra DSN, run Freerouting, import the SES back into the board."""
import os
import subprocess
import sys
import pcbnew

board_path, work = sys.argv[1], sys.argv[2]
passes = sys.argv[3] if len(sys.argv) > 3 else "40"
dsn, ses = f"{work}/board.dsn", f"{work}/board.ses"

board = pcbnew.LoadBoard(board_path)
assert pcbnew.ExportSpecctraDSN(board, dsn), "DSN export failed"
subprocess.run(["/opt/homebrew/opt/openjdk/bin/java", "-jar", os.path.expanduser("~/.kicad-mcp/freerouting.jar"), "-de", dsn, "-do", ses,
                "--gui.enabled=false", "-mp", passes, "--router.ignore_net_classes=Power"], check=True)
board = pcbnew.LoadBoard(board_path)
assert pcbnew.ImportSpecctraSES(board, ses), "SES import failed"
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
board.Save(board_path)
print("routed and saved")
