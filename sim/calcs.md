# Hand calculations

| Check | Value | Limit | Result | Note |
|---|---|---|---|---|
| VOUT no load (min / nom / max) | 4.85 / 5.03 / 5.22 V | 4.75–5.5 V (Type-C vSafe5V) | PASS |  |
| Line-drop comp at 3 A | +0.184 V (±20 %) | — | PASS | R7 × 2.05 µA/A × 3 A |
| VOUT at 3 A, worst high | 5.45 V | ≤ 5.5 V | PASS | Reference 44.2 k / 8.2 k would give 5.58 V here |
| L1 peak at 9 V in, 3.9 A out | 4.59 A (ripple 1.39 A p-p) | Isat 5.5 A | PASS |  |
| L1 peak at 14.4 V in, 3.9 A out | 4.95 A (ripple 2.11 A p-p) | Isat 5.5 A | PASS |  |
| L1 peak at 24 V in, 3.9 A out | 5.19 A (ripple 2.59 A p-p) | Isat 5.5 A | PASS |  |
| L1 peak at 36 V in, 3.9 A out | 5.31 A (ripple 2.83 A p-p) | Isat 5.5 A | PASS |  |
| L1 RMS at 3 A | 3.06 A | Irms 3.6 A | PASS | Irms is the 40 °C self-heating point |
| L2 DC at EN turn-on (VIN1 5.6 V) | 3.18 A | Irms 4.7 A | PASS |  |
| Output ripple at 14.4 V | 11 mV p-p | ≤ 50 mV (good practice) | PASS | C_eff 57 µF |
| Input RMS ripple current | 1.44 A | — | PASS | shared by C2/C3 and C1 |
| C1 share (ESR 0.3 Ω) | 0.27 A RMS | CK1H101M ripple rating (not in listing) | PASS | Verify against the Chengx datasheet |
| D2 SS56 at 1.55 A | 0.77 W, Tj ≈ 103 °C at 60 °C ambient | Tj ≤ 150 °C | PASS | θJA ≈ 55 °C/W on the VBAT_IN/VIN_F copper (estimate) |
| D2 SS510 at 1.55 A | 1.05 W, Tj ≈ 118 °C at 60 °C ambient | Tj ≤ 150 °C | PASS | θJA ≈ 55 °C/W on the VBAT_IN/VIN_F copper (estimate) |
| U1 loss (typ RDS(on)) | 0.66 W, Tj ≈ 100 °C at 70 °C ambient | Tj ≤ 150 °C | PASS | θJA 46 °C/W (JESD51-7); 36 °C/W on the MPS EVB |
| U1 loss (hot max RDS(on)) | 1.14 W, Tj ≈ 122 °C at 70 °C ambient | Tj ≤ 150 °C | PASS | θJA 46 °C/W (JESD51-7); 36 °C/W on the MPS EVB |
| EN at VIN1 14.4 V | 3.62 V, zener 0 µA | ≤ 100 µA | PASS | 34.4 V is the highest VIN1 in the simulation; 40 V is the abs-max case |
| EN at VIN1 24 V | 6.03 V, zener 0 µA | ≤ 100 µA | PASS | 34.4 V is the highest VIN1 in the simulation; 40 V is the abs-max case |
| EN at VIN1 34.4 V | 6.50 V, zener 85 µA | ≤ 100 µA | PASS | 34.4 V is the highest VIN1 in the simulation; 40 V is the abs-max case |
| EN at VIN1 40 V | 6.50 V, zener 141 µA | ≤ 100 µA | **CHECK** | 34.4 V is the highest VIN1 in the simulation; 40 V is the abs-max case |
| UVLO at the 12 V terminal (on / off) | 6.1 / 5.5 V | below cranking 6–8 V | PASS | VIN1 thresholds plus about 0.5 V across D2 |
| D5 white LED current | 2.1 mA | KT-0603W max 20 mA | PASS |  |
| D6 red LED current (VCC2 3.45 V LDO) | 1.5 mA | KT-0603R max 20 mA | PASS | Flows only while FLT is low (fault), so VCC2 is unloaded in normal use |
| Input current at 6.1 V terminal | 3.18 A | 5 A Micro2 fuse | PASS |  |
