# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "matplotlib"]
# ///
"""Input chain of swift-usbc-3a in KiCad's ngspice: car transients and input-filter stability.

J1 -> D1 SMBJ33CA -> D2 SS56 -> C11-C14 -> L2 -> C1/C2/C3/C4 (VIN1) -> MPQ4228 (constant-power load).
The MPQ4228 has no SPICE model, so it is a 17.7 W constant-power sink with the EN-divider UVLO.
uv run sim/input_sim.py   (writes sim/results.md and sim/zout.png)
"""
import ctypes as C
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = "/Applications/KiCad/KiCad.app/Contents/Frameworks/libngspice.0.dylib"

P_IN = 5.2 * 3.0 / 0.88  # 5.03 V + 0.18 V line-drop comp at 3 A, 88 % efficiency
# EN divider 100k / (36k || 500k internal), EN 1.4 V rising / 1.25 V falling
V_ON = 1.4 * (1 + 100 / (36 * 500 / 536))
V_OFF = 1.25 * (1 + 100 / (36 * 500 / 536))

# SMBJ33CA: VBR 36.7-40.6 V @ 1 mA, VC 53.3 V @ 11.3 A (10/1000 us). Low BV stresses the TVS, high BV the IC.
TVS = {"BV min": dict(bv=36.7, rs=(53.3 - 36.7) / 11.3), "BV max": dict(bv=40.6, rs=(53.3 - 40.6) / 11.3)}

# (name, battery source, Ri, tstop, tmax[, pulse]); 12 V system, ISO 7637-2:2011 / ISO 16750-2:2012, worst levels.
# A pulse is (generator waveform, Ri, window on, window off, battery disconnected during the window). The generator
# connects only in its window; the battery feeds through a 5 uH / 50 ohm artificial network, as in the test setup.
CASES = [
    ("Normal 14.4 V", "PWL(0 14.4)", 0.02, 20e-3, 20e-6),
    ("Hot plug 14.4 V (fuse tap fitted live)", "PWL(0 0 1n 14.4)", 0.02, 3e-3, 0.5e-6),
    ("Hot plug 16 V", "PWL(0 0 1n 16)", 0.02, 3e-3, 0.5e-6),
    ("Jump start 24 V", "PWL(0 14 10m 14 11m 24 200m 24 201m 14)", 0.02, 0.25, 20e-6),
    ("Load dump B, suppressed 35 V, Ri 0.5, 400 ms", "PWL(0 14 10m 14 15m 35 410m 35 600m 14)", 0.5, 0.65, 50e-6),
    ("Load dump A, unsuppressed 87 V, Ri 1, 200 ms", "PWL(0 14 10m 14 15m 87 210m 87 400m 14)", 1.0, 0.45, 20e-6),
    ("Pulse 1, -150 V, Ri 10, 2 ms", "PWL(0 14)", 0.02, 30e-3, 0.5e-6,
     ("PWL(0 0 10m 0 10.001m -150 10.5m -55 11m -20 12m 0)", 10.0, 10e-3, 12.2e-3, True)),
    ("Pulse 2a, +112 V, Ri 2, 50 us", "PWL(0 14)", 0.02, 15e-3, 0.2e-6,
     ("PWL(0 14 10m 14 10.001m 126 10.05m 14)", 2.0, 10e-3, 10.06e-3, False)),
    ("Pulse 2b, +10 V, Ri 0.05, 0.2 s", "PWL(0 14 10m 14 11m 24 211m 24 212m 14)", 0.05, 0.3, 20e-6),
    ("Pulse 3a, -220 V, Ri 50, 100 ns", "PWL(0 14)", 0.02, 1.2e-3, 1e-9,
     ("PWL(0 14 1m 14 1.000005m -206 1.0001m 14)", 50.0, 0.9999e-3, 1.0002e-3, False)),
    ("Pulse 3b, +150 V, Ri 50, 100 ns", "PWL(0 14)", 0.02, 1.2e-3, 1e-9,
     ("PWL(0 14 1m 14 1.000005m 164 1.0001m 14)", 50.0, 0.9999e-3, 1.0002e-3, False)),
    ("Cold crank to 6 V, then 8 V", "PWL(0 14 10m 14 15m 6 30m 6 35m 8 230m 8 330m 14)", 0.02, 0.4, 20e-6),
    ("Reverse battery -14 V", "PWL(0 0 1m -14)", 0.02, 20e-3, 20e-6),
]


def supply(src, ri, pulse):
    if not pulse:
        return [f"VSRC SRC 0 {src}", f"RSRC SRC H1 {ri}"]
    gen, rg, on, off, bat_open = pulse
    lines = [f"VSRC SRC 0 {src}", f"RSRC SRC B1 {ri}", "LLISN B1 H1 5u", "RLISN B1 H1 50",
             f"VG SG 0 {gen}", f"RG SG G1 {rg}", "SGEN G1 H1 CG 0 SWT",
             f"VCG CG 0 PWL(0 0 {on} 0 {on + 1e-9} 1 {off} 1 {off + 1e-9} 0)",
             ".model SWT SW(VT=0.5 VH=0.1 RON=1m ROFF=1e9)"]
    if bat_open:
        lines[1] = f"RSRC SRC B0 {ri}"
        lines += ["SBAT B0 B1 CB 0 SWT", f"VCB CB 0 PWL(0 1 {on} 1 {on + 1e-9} 0 {off} 0 {off + 1e-9} 1)"]
    return lines


def circuit(src, ri, tvs, esr_c1=0.3, ac=False, d2="SS510", pulse=None):
    t = TVS[tvs]
    lines = ["* swift-usbc-3a input"] + supply(src, ri, pulse) + [
        # 2 m of 0.75 mm2 harness loop from the fuse tap
        "RH H1 H2 50m", "LH H2 VBAT 1.5u", "RLHD H2 VBAT 10",
        # D1 bidirectional TVS
        "DTA VBAT NT DTVS", "DTB 0 NT DTVS",
        f".model DTVS D(IS=1e-12 N=1 BV={t['bv']} IBV=1m RS={t['rs']:.3f} CJO=1.5n)",
        # D2 SS510 100 V 5 A (850 mV at 5 A); SS56 (60 V) was the first choice
        f"D2 VBAT VINF D{d2}",
        ".model DSS510 D(IS=3e-6 N=1.3 RS=0.04 BV=100 IBV=1m CJO=400p)",
        ".model DSS56 D(IS=2e-5 N=1.2 RS=0.03 BV=60 IBV=1m CJO=500p)",
        # C11, C12 22 nF; C13 100 nF; C14 10 uF 50 V X5R 1206 (about 5 uF at 14 V)
        "C11 VINF 0 44n", "C13 VINF 0 100n",
        "C14 VINF N14 5u", "R14 N14 0 5m",
        # L2 FTC303020D 2.2 uH
        "L2 VINF NL2 2.2u", "RL2 NL2 VIN1 30m",
        # C1 100 uF 50 V electrolytic; C2/C3 4.7 uF 50 V X7R 0805 (about 3 uF each at 14 V); C4 100 nF
        "C1 VIN1 N1 100u", f"RC1 N1 0 {esr_c1}",
        "C23 VIN1 N23 6u", "R23 N23 0 3m", "C4 VIN1 0 100n",
        # EN UVLO with hysteresis
        "VREF REF 0 1", "SEN REF EN VIN1 0 SWEN OFF", "REN EN 0 1meg",
        f".model SWEN SW(VT={(V_ON + V_OFF) / 2:.3f} VH={(V_ON - V_OFF) / 2:.3f} RON=1 ROFF=1e9)",
    ]
    if ac:
        # filter output impedance at VIN1, biased at full load
        lines += [f"ILOAD VIN1 0 DC {P_IN / 11.5:.3f}", "IAC 0 VIN1 DC 0 AC 1",
                  ".ac dec 200 100 1meg"]
    else:
        lines += [f"BLOAD VIN1 0 I={P_IN:.2f}/max(v(VIN1),3)*v(EN)*min(max(v(VIN1)/3,0),1)",
                  ".options method=gear", ".save all @dta[id]"]
    lines.append(".end")
    return lines


class Ngspice:
    def __init__(self):
        self.lib = C.CDLL(LIB)
        out = C.CFUNCTYPE(C.c_int, C.c_char_p, C.c_int, C.c_void_p)
        ext = C.CFUNCTYPE(C.c_int, C.c_int, C.c_bool, C.c_bool, C.c_int, C.c_void_p)
        self.log = []
        self._o = out(lambda s, i, p: (self.log.append(s.decode(errors="replace")), 0)[1])
        self._s = out(lambda s, i, p: 0)
        self._e = ext(lambda *a: 0)
        self.lib.ngSpice_Init(self._o, self._s, self._e, None, None, None, None)

    def run(self, lines, analysis, vecs, dat):
        if os.path.exists(dat):
            os.remove(dat)
        self.lib.ngSpice_Command(b"destroy all")
        lines = lines[:-1] + [analysis, ".end"] if analysis else lines
        arr = (C.c_char_p * (len(lines) + 1))(*[l.encode() for l in lines], None)
        self.lib.ngSpice_Circ(arr)
        self.lib.ngSpice_Command(b"run")
        self.lib.ngSpice_Command(b"set wr_singlescale")
        self.lib.ngSpice_Command(f"wrdata {dat} {vecs}".encode())
        self.lib.ngSpice_Command(b"remcirc")
        d = np.loadtxt(dat)
        os.remove(dat)
        return d


def transients(ng, d2="SS510", only=None):
    rows = ["| Case | TVS | VIN1 max / min | VIN_F max | D2 reverse max | L2 peak | TVS peak I / P / energy | Verdict |",
            "|---|---|---|---|---|---|---|---|"]
    for name, src, ri, tstop, tmax, *pulse in CASES:
        if only and not any(o in name for o in only):
            continue
        for tvs in TVS:
            d = ng.run(circuit(src, ri, tvs, d2=d2, pulse=pulse[0] if pulse else None), f".tran {tmax} {tstop} 0 {tmax}",
                       "v(VIN1) v(VINF) v(VBAT) i(L2) @dta[id] v(EN)", os.path.join(HERE, "_t.txt"))
            t, vin1, vinf, vbat, il2, itvs = (d[:, i] for i in range(6))
            ptvs = np.abs(itvs * vbat)
            e = float(np.trapezoid(ptvs, t))
            vrev = float((vinf - vbat).max())
            limit = 100 if d2 == "SS510" else 60
            verdict = []
            if vin1.max() > 40 or vin1.min() < -0.4:
                verdict.append("**FAIL IC**")
            elif vin1.max() > 36:
                verdict.append("over 36 V op max")
            if vrev > limit:
                verdict.append(f"**{d2} > {limit} V**")
            if e > 0.86:
                verdict.append("**TVS energy**")
            # Inrush that saturates L2 for microseconds is harmless; flag only sustained overcurrent.
            hot = np.abs(il2) > 4.7
            t_hot = float(np.sum(np.diff(t)[hot[:-1]]))
            if t_hot > 50e-6:
                verdict.append(f"L2 > 4.7 A for {t_hot * 1e3:.1f} ms")
            rows.append(f"| {name} | {tvs} | {vin1.max():.1f} / {vin1.min():.1f} V | {vinf.max():.1f} V | {vrev:.1f} V | "
                        f"{np.abs(il2).max():.2f} A | {np.abs(itvs).max():.1f} A / {ptvs.max() / 1e3:.2f} kW / {e:.3f} J | "
                        f"{', '.join(verdict) or 'PASS'} |")
    return rows


def tvs24(ng):
    # SMBJ24CA: VBR 26.7-29.5 V, VC 38.9 V @ 15.4 A
    saved = dict(TVS)
    TVS.clear()
    TVS.update({"24CA BV min": dict(bv=26.7, rs=(38.9 - 26.7) / 15.4), "24CA BV max": dict(bv=29.5, rs=(38.9 - 29.5) / 15.4)})
    rows = transients(ng, only=["Load dump B", "Pulse 2a"])
    TVS.clear()
    TVS.update(saved)
    return rows


def zout(ng):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = ["| C1 ESR | Peak \\|Zout\\| at VIN1 | at | \\|Zin\\| at 12 V / 9 V / 6 V | Margin at 6 V |", "|---|---|---|---|---|"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    zin = {v: v * v / P_IN for v in (12, 9, 6)}
    for esr in (0.05, 0.3, 1.0):
        d = ng.run(circuit("DC 11.5", 0.02, "BV max", esr_c1=esr, ac=True), None,
                   "v(VIN1)", os.path.join(HERE, "_z.txt"))
        f, z = d[:, 0], np.hypot(d[:, 1], d[:, 2])
        k = int(z.argmax())
        rows.append(f"| {esr} Ω | {z[k]:.2f} Ω | {f[k] / 1e3:.1f} kHz | {zin[12]:.1f} / {zin[9]:.1f} / {zin[6]:.1f} Ω | "
                    f"{20 * np.log10(zin[6] / z[k]):.1f} dB |")
        ax.loglog(f, z, label=f"filter |Zout|, C1 ESR {esr} Ω")
    for v, zv in zin.items():
        ax.axhline(zv, ls="--", lw=0.8, color="grey")
        ax.text(120, zv * 1.08, f"converter |Zin| at {v} V", fontsize=8, color="grey")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Impedance (Ω)")
    ax.set_title("Input filter output impedance vs converter input impedance")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "zout.png"), dpi=130)
    return rows


def main():
    ng = Ngspice()
    text = [f"# Input chain simulation (ngspice, KiCad {os.path.basename(LIB)})", "",
            f"Load: {P_IN:.1f} W constant power, EN UVLO on at {V_ON:.2f} V, off at {V_OFF:.2f} V (VIN1).",
            "Pass limits: VIN1 ≤ 36 V (operating) and ≤ 40 V (absolute max); SS56 reverse ≤ 60 V; "
            "TVS energy ≤ 0.86 J (600 W 10/1000 µs); L2 ≤ 4.7 A for longer than 50 µs.", "",
            "## Transients, D2 = SS510 (as built)", ""] + transients(ng) + [
            "", "## D2 = SS56 (60 V, first choice, replaced)", ""] + transients(ng, "SS56", ["Pulse 1", "Pulse 3a"]) + [
            "", "## SMBJ24CA in place of SMBJ33CA (review proposal, rejected)", ""] + tvs24(ng) + ["", "## Input filter stability (Middlebrook)", ""] + zout(ng) + [""]
    open(os.path.join(HERE, "results.md"), "w").write("\n".join(text))
    print("\n".join(text))


main()
