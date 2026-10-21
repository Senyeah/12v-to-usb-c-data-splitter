"""Adds hidden LCSC / MPN fields to the schematic symbols: add_fields.py <sch>"""
import re
import sys

LCSC = {
    "J1": "C7509570", "D1": "C19077587", "D2": "C18199169", "C11": "C21122", "C12": "C21122", "C13": "C14663",
    "C14": "C7432781", "L2": "C7423318", "C1": "C19184158", "C2": "C20416422", "C3": "C20416422", "C4": "C14663",
    "R1": "C25803", "R2": "C7468664", "U1": "C17638787", "R9": "C7468418", "C5": "C15849", "C6": "C19666",
    "R3": "C25804", "R11": "C21190", "D6": "C7371900", "C7": "C6903803", "L1": "C6808109", "C20": "C14663",
    "C21": "C7432785", "C22": "C7432785", "C23": "C7432785", "C24": "C7432785", "R5": "C7468682", "C25": "C6903803",
    "R6": "C4184", "C26": "C1663", "R8": "C25981", "R10": "C21190", "D5": "C7496818", "J2": "C19944605",
    "L3": "C6807995", "L4": "C6807995", "C29": "C7227538", "J3": "C165948", "C27": "C7432781", "C28": "C1604",
    "D3": "C19829579", "D4": "C19829579",
}
MPN = {"R4": "0603WAF470KT5E", "R7": "0603WAF4422T5E", "U1": "MPQ4228GRE-C-AEC1-Z"}

def sexpr_end(text, i):
    """Index just past the s-expression that starts at text[i] == '('."""
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


path = sys.argv[1]
s = open(path).read()
out, pos, n = [], 0, 0
for m in re.finditer(r'\(property "Reference" "([^"]+)"', s):
    ref = m.group(1)
    if ref not in LCSC and ref not in MPN:
        continue
    if "(lib_id" not in s[s.rfind("(symbol", 0, m.start()):m.start()]:
        continue  # library definition, not a placed instance
    end = sexpr_end(s, m.start())
    indent = s[s.rfind("\n", 0, m.start()) + 1:m.start()]
    add = ""
    for key, table in (("LCSC", LCSC), ("MPN", MPN)):
        if ref in table:
            add += f'\n{indent}(property "{key}" "{table[ref]}" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))'
    out.append(s[pos:end] + add)
    pos = end
    n += 1
out.append(s[pos:])
open(path, "w").write("".join(out))
print("symbols updated:", n)
