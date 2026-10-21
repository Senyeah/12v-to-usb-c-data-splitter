"""Swap parts to JLC basic/preferred types (no $3 extended fee): cost_parts.py <sch>"""
import re
import sys

# ref: (value or None, LCSC, MPN or None)
SWAPS = {
    "R2": (None, "C23147", None), "R5": (None, "C22859", None), "R9": (None, "C21189", None),
    "C7": (None, "C21120", None), "C25": (None, "C21120", None), "D6": (None, "C2286", None),
    "D5": ("White LED", "C2290", None),
    "C21": (None, "C12891", None), "C22": (None, "C12891", None), "C23": (None, "C12891", None), "C24": (None, "C12891", None),
    "C14": (None, "C13585", None), "C27": (None, "C13585", None),
    # 0.792 V x (1 + 30/5.6) = 5.03 V; 47 pF keeps the feed-forward zero near 110 kHz.
    "R7": ("30k 1%", "C22984", None), "R8": ("5.6k 1%", "C23189", None), "C26": ("47pF C0G", "C1671", None),
    # Optional eye-diagram tuning parts in the MPQ4228 reference design.
    "L3": ("0R", "C21189", None), "L4": ("0R", "C21189", None),
    "R4": (None, "C23164", "0603WAF470KT5E"),
    # 100 V: ISO 7637-2 pulse 1 puts about 76 V across D2 (ngspice, sim/input_sim.py).
    "D2": ("SS510", "C18199171", None),
}
DNP = {"C29"}


def sexpr_end(text, i):
    depth, j, in_str = 0, i, False
    while True:
        c = text[j]
        if in_str:
            if c == "\\":
                j += 1
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1


def set_prop(blk, name, value):
    m = re.search(r'\(property "%s" "[^"]*"' % name, blk)
    if m:
        return blk[:m.start()] + f'(property "{name}" "{value}"' + blk[m.end():]
    m = re.search(r'\(property "Reference" ', blk)
    end = sexpr_end(blk, m.start())
    return blk[:end] + f'\n\t\t(property "{name}" "{value}" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))' + blk[end:]


path = sys.argv[1]
s = open(path).read()
done = 0
for ref in list(SWAPS) + sorted(DNP):
    i = s.find(f'(property "Reference" "{ref}"')
    start = s.rfind("\n\t(symbol", 0, i) + 1
    end = sexpr_end(s, start + 1)
    blk = s[start:end]
    if ref in SWAPS:
        value, lcsc, mpn = SWAPS[ref]
        if value:
            blk = set_prop(blk, "Value", value)
        blk = set_prop(blk, "LCSC", lcsc)
        if mpn:
            blk = set_prop(blk, "MPN", mpn)
        else:
            blk = re.sub(r'\n\t\t\(property "MPN" "[^"]*" \(at 0 0 0\) \(effects \(font \(size 1\.27 1\.27\)\) \(hide yes\)\)\)', "", blk)
    if ref in DNP:
        blk = blk.replace("(dnp no)", "(dnp yes)", 1)
    s = s[:start] + blk + s[end:]
    done += 1
open(path, "w").write(s)
print("updated", done)
