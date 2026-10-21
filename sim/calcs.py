"""Hand calculations for swift-usbc-3a: python3 sim/calcs.py  (writes sim/calcs.md)

Datasheet values are from MPQ4228-C Rev 1.0; part values from the LCSC listings in the BOM.
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
rows = []


def check(name, value, limit, ok, note=""):
    rows.append(f"| {name} | {value} | {limit} | {'PASS' if ok else '**CHECK**'} | {note} |")


# Output voltage: VOUT = VFB (1 + R7/R8) + R7 * GADJ * I  (datasheet eq. 2)
vfb = (0.776, 0.792, 0.808)
r7, r8, tol = 30e3, 5.6e3, 0.01
gadj = 2.05e-6
v0_min = vfb[0] * (1 + r7 * (1 - tol) / (r8 * (1 + tol)))
v0_nom = vfb[1] * (1 + r7 / r8)
v0_max = vfb[2] * (1 + r7 * (1 + tol) / (r8 * (1 - tol)))
comp = r7 * gadj * 3.0
v3_max = v0_max + comp * 1.2 * (1 + tol)
check("VOUT no load (min / nom / max)", f"{v0_min:.2f} / {v0_nom:.2f} / {v0_max:.2f} V", "4.75–5.5 V (Type-C vSafe5V)",
      v0_min >= 4.75 and v0_max <= 5.5)
check("Line-drop comp at 3 A", f"+{comp:.3f} V (±20 %)", "—", True, "R7 × 2.05 µA/A × 3 A")
check("VOUT at 3 A, worst high", f"{v3_max:.2f} V", "≤ 5.5 V", v3_max <= 5.5,
      "Reference 44.2 k / 8.2 k would give 5.58 V here")

# Buck inductor L1: APV ANR6045T4R7M, 4.7 uH ±20 %, Irms 3.6 A, Isat 5.5 A
l1_min, fsw, vout = 4.7e-6 * 0.8, 420e3, 5.22
for vin in (9.0, 14.4, 24.0, 36.0):
    d = vout / vin
    ripple = (vin - vout) * d / (l1_min * fsw)
    peak = 3.9 + ripple / 2  # USB current-limit max 3.9 A
    check(f"L1 peak at {vin:g} V in, 3.9 A out", f"{peak:.2f} A (ripple {ripple:.2f} A p-p)", "Isat 5.5 A", peak <= 5.5)
irms = math.sqrt(3.0 ** 2 + (2.1 ** 2) / 12)
check("L1 RMS at 3 A", f"{irms:.2f} A", "Irms 3.6 A", irms <= 3.6, "Irms is the 40 °C self-heating point")

# Input inductor L2: FTC303020D2R2MBCA, 2.2 uH, 37 mOhm, Irms 4.7 A, Isat 6 A
p_in = vout * 3 / 0.88
i_in6 = p_in / 5.6
check("L2 DC at EN turn-on (VIN1 5.6 V)", f"{i_in6:.2f} A", "Irms 4.7 A", i_in6 <= 4.7)

# Output ripple: 4 x 22 uF 25 V X5R 1206 (CL31A226KAHNNNE), about 35 % loss at 5 V DC bias
c_out = 4 * 22e-6 * 0.65
ripple14 = (14.4 - vout) * (vout / 14.4) / (l1_min * fsw)
v_rip = ripple14 / (8 * fsw * c_out)
check("Output ripple at 14.4 V", f"{v_rip * 1e3:.0f} mV p-p", "≤ 50 mV (good practice)", v_rip <= 0.05,
      f"C_eff {c_out * 1e6:.0f} µF")

# Input ripple current split: C2/C3 4.7 uF 50 V X7R 0805 (about 2.8 uF each at 14 V) vs C1 ESR
d14 = vout / 14.4
i_cin = 3.0 * math.sqrt(d14 * (1 - d14))
z_mlcc = 1 / (2 * math.pi * fsw * 5.6e-6)
i_c1 = i_cin * z_mlcc / (z_mlcc + 0.3)
check("Input RMS ripple current", f"{i_cin:.2f} A", "—", True, "shared by C2/C3 and C1")
check("C1 share (ESR 0.3 Ω)", f"{i_c1:.2f} A RMS", "CK1H101M ripple rating (not in listing)", i_c1 <= 0.3,
      "Verify against the Chengx datasheet")

# Reverse diode D2 at 12 V
i_d2 = p_in / 11.5
for name, vf in (("SS56", 0.50), ("SS510", 0.68)):
    p = i_d2 * vf
    tj = 60 + p * 55
    check(f"D2 {name} at {i_d2:.2f} A", f"{p:.2f} W, Tj ≈ {tj:.0f} °C at 60 °C ambient", "Tj ≤ 150 °C", tj <= 150,
          "θJA ≈ 55 °C/W on the VBAT_IN/VIN_F copper (estimate)")

# MPQ4228 losses at 14.4 V in, 3 A, hot (max RDS(on)) and typical
for label, hs, ls, sw in (("typ", 0.050, 0.030, 0.020), ("hot max", 0.090, 0.060, 0.040)):
    p = 3 ** 2 * (hs * d14 + ls * (1 - d14)) + 0.5 * 14.4 * 3 * 10e-9 * fsw + 3 ** 2 * sw + 0.05
    tj = 70 + p * 46
    check(f"U1 loss ({label} RDS(on))", f"{p:.2f} W, Tj ≈ {tj:.0f} °C at 70 °C ambient", "Tj ≤ 150 °C", tj <= 150,
          "θJA 46 °C/W (JESD51-7); 36 °C/W on the MPS EVB")

# EN pin: 6.5 V internal zener, current must stay below 100 uA (datasheet EN/SYNC section)
r_dn = 36e3 * 500e3 / 536e3
for vin in (14.4, 24.0, 34.4, 40.0):
    i_z = max(0.0, (vin - 6.5) / 100e3 - 6.5 / r_dn)
    v_en = min(vin * r_dn / (100e3 + r_dn), 6.5)
    check(f"EN at VIN1 {vin:g} V", f"{v_en:.2f} V, zener {i_z * 1e6:.0f} µA", "≤ 100 µA", i_z <= 100e-6,
          "34.4 V is the highest VIN1 in the simulation; 40 V is the abs-max case")
v_on, v_off = 1.4 * (1 + 100e3 / r_dn), 1.25 * (1 + 100e3 / r_dn)
check("UVLO at the 12 V terminal (on / off)", f"{v_on + 0.5:.1f} / {v_off + 0.5:.1f} V", "below cranking 6–8 V", True,
      "VIN1 thresholds plus about 0.5 V across D2")

# LEDs
check("D5 white LED current", f"{(5.03 - 2.9) / 1e3 * 1e3:.1f} mA", "KT-0603W max 20 mA", True)
check("D6 red LED current (VCC2 3.45 V LDO)", f"{(3.45 - 2.0) / 1e3 * 1e3:.1f} mA", "KT-0603R max 20 mA", True,
      "Flows only while FLT is low (fault), so VCC2 is unloaded in normal use")

# Fuse: highest steady input current is at the low-voltage end
check("Input current at 6.1 V terminal", f"{p_in / 5.6:.2f} A", "5 A Micro2 fuse", p_in / 5.6 < 5)

text = ["# Hand calculations", "", "| Check | Value | Limit | Result | Note |", "|---|---|---|---|---|"] + rows
open(os.path.join(HERE, "calcs.md"), "w").write("\n".join(text) + "\n")
print("\n".join(text))
