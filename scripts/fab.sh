#!/usr/bin/env bash
# JLCPCB outputs into fab/.
set -euo pipefail
cd "$(dirname "$0")/.."
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
N=swift-usbc-3a
T=$(mktemp -d)

rm -rf fab && mkdir -p fab/gerber fab/assembly fab/docs
$KC pcb export gerbers --subtract-soldermask \
  --layers F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  -o fab/gerber/ $N.kicad_pcb >/dev/null
$KC pcb export drill --format excellon --drill-origin absolute --excellon-units mm \
  --excellon-zeros-format decimal --excellon-oval-format route --excellon-separate-th \
  --generate-map --map-format gerberx2 -o fab/gerber/ $N.kicad_pcb >/dev/null
(cd fab/gerber && zip -q -r ../$N-gerbers.zip .)

$KC sch export bom --exclude-dnp --fields "Reference,Value,Footprint,LCSC" --labels "Ref,Value,Footprint,LCSC" \
  --group-by "Value,Footprint,LCSC" --ref-range-delimiter "" -o $T/bom.csv $N.kicad_sch >/dev/null
$KC pcb export pos --side front --format csv --units mm --exclude-dnp --use-drill-file-origin -o $T/pos.csv $N.kicad_pcb >/dev/null
python3 scripts/jlc_files.py $T/bom.csv $T/pos.csv fab/assembly $N
python3 scripts/jlc_files.py $T/bom.csv $T/pos.csv fab/assembly $N --with-tht

$KC sch export pdf -o fab/docs/$N-schematic.pdf $N.kicad_sch >/dev/null
$KC pcb export pdf --mode-single --ibt --sp --cdnp --layers F.Fab,F.SilkS,Edge.Cuts -o fab/docs/$N-assembly.pdf $N.kicad_pcb >/dev/null
$KC pcb export pdf --mode-multipage --ibt --cl Edge.Cuts --layers F.Cu,In1.Cu,In2.Cu,B.Cu,F.SilkS -o fab/docs/$N-layers.pdf $N.kicad_pcb >/dev/null
rm -rf $T
find fab -type f | sort
