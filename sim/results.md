# Input chain simulation (ngspice, KiCad libngspice.0.dylib)

Load: 17.7 W constant power, EN UVLO on at 5.57 V, off at 4.97 V (VIN1).
Pass limits: VIN1 ≤ 36 V (operating) and ≤ 40 V (absolute max); SS56 reverse ≤ 60 V; TVS energy ≤ 0.86 J (600 W 10/1000 µs); L2 ≤ 4.7 A for longer than 50 µs.

## Transients, D2 = SS510 (as built)

| Case | TVS | VIN1 max / min | VIN_F max | D2 reverse max | L2 peak | TVS peak I / P / energy | Verdict |
|---|---|---|---|---|---|---|---|
| Normal 14.4 V | BV min | 13.8 / 13.8 V | 13.8 V | -0.5 V | 1.29 A | 0.0 A / 0.00 kW / 0.000 J | PASS |
| Normal 14.4 V | BV max | 13.8 / 13.8 V | 13.8 V | -0.5 V | 1.29 A | 0.0 A / 0.00 kW / 0.000 J | PASS |
| Hot plug 14.4 V (fuse tap fitted live) | BV min | 13.8 / -0.0 V | 14.2 V | -0.0 V | 29.65 A | 0.1 A / 0.00 kW / 0.000 J | L2 > 4.7 A for 0.1 ms |
| Hot plug 14.4 V (fuse tap fitted live) | BV max | 13.8 / -0.0 V | 14.2 V | -0.0 V | 29.65 A | 0.2 A / 0.00 kW / 0.000 J | L2 > 4.7 A for 0.1 ms |
| Hot plug 16 V | BV min | 15.4 / -0.0 V | 15.8 V | -0.0 V | 32.84 A | 0.1 A / 0.00 kW / 0.000 J | L2 > 4.7 A for 0.1 ms |
| Hot plug 16 V | BV max | 15.4 / -0.0 V | 15.8 V | -0.0 V | 32.84 A | 0.2 A / 0.00 kW / 0.000 J | L2 > 4.7 A for 0.1 ms |
| Jump start 24 V | BV min | 23.5 / 13.4 V | 23.5 V | 1.2 V | 2.27 A | 0.0 A / 0.00 kW / 0.000 J | PASS |
| Jump start 24 V | BV max | 23.5 / 13.4 V | 23.5 V | 1.2 V | 2.27 A | 0.0 A / 0.00 kW / 0.000 J | PASS |
| Load dump B, suppressed 35 V, Ri 0.5, 400 ms | BV min | 34.3 / 12.7 V | 34.3 V | -0.4 V | 1.76 A | 0.0 A / 0.00 kW / 0.000 J | PASS |
| Load dump B, suppressed 35 V, Ri 0.5, 400 ms | BV max | 34.3 / 12.7 V | 34.3 V | -0.4 V | 1.76 A | 0.0 A / 0.00 kW / 0.000 J | PASS |
| Load dump A, unsuppressed 87 V, Ri 1, 200 ms | BV min | 73.4 / 11.9 V | 73.4 V | -0.4 V | 2.65 A | 12.3 A / 0.91 kW / 226.625 J | **FAIL IC**, **TVS energy** |
| Load dump A, unsuppressed 87 V, Ri 1, 200 ms | BV max | 72.0 / 11.9 V | 72.0 V | -0.4 V | 2.65 A | 13.7 A / 0.99 kW / 244.175 J | **FAIL IC**, **TVS energy** |
| Pulse 1, -150 V, Ri 10, 2 ms | BV min | 14.2 / 5.0 V | 14.0 V | 75.9 V | 15.18 A | 8.6 A / 0.54 kW / 0.144 J | L2 > 4.7 A for 0.1 ms |
| Pulse 1, -150 V, Ri 10, 2 ms | BV max | 14.2 / 5.0 V | 14.0 V | 74.2 V | 15.18 A | 8.8 A / 0.54 kW / 0.141 J | L2 > 4.7 A for 0.1 ms |
| Pulse 2a, +112 V, Ri 2, 50 us | BV min | 24.1 / 13.3 V | 32.7 V | 8.4 V | 36.52 A | 0.0 A / 0.00 kW / 0.000 J | PASS |
| Pulse 2a, +112 V, Ri 2, 50 us | BV max | 24.1 / 13.3 V | 32.7 V | 8.4 V | 36.52 A | 0.0 A / 0.00 kW / 0.000 J | PASS |
| Pulse 2b, +10 V, Ri 0.05, 0.2 s | BV min | 23.5 / 13.3 V | 23.5 V | 1.2 V | 2.27 A | 0.0 A / 0.00 kW / 0.000 J | PASS |
| Pulse 2b, +10 V, Ri 0.05, 0.2 s | BV max | 23.5 / 13.3 V | 23.5 V | 1.2 V | 2.27 A | 0.0 A / 0.00 kW / 0.000 J | PASS |
| Pulse 3a, -220 V, Ri 50, 100 ns | BV min | 13.4 / 13.4 V | 13.5 V | 36.5 V | 1.56 A | 1.1 A / 0.01 kW / 0.000 J | PASS |
| Pulse 3a, -220 V, Ri 50, 100 ns | BV max | 13.4 / 13.4 V | 13.5 V | 36.7 V | 1.56 A | 1.1 A / 0.01 kW / 0.000 J | PASS |
| Pulse 3b, +150 V, Ri 50, 100 ns | BV min | 13.4 / 13.4 V | 13.4 V | -0.5 V | 1.35 A | 0.0 A / 0.00 kW / 0.000 J | PASS |
| Pulse 3b, +150 V, Ri 50, 100 ns | BV max | 13.4 / 13.4 V | 13.4 V | -0.5 V | 1.35 A | 0.0 A / 0.00 kW / 0.000 J | PASS |
| Cold crank to 6 V, then 8 V | BV min | 13.4 / 5.0 V | 13.4 V | -0.5 V | 3.54 A | 0.0 A / 0.00 kW / 0.000 J | PASS |
| Cold crank to 6 V, then 8 V | BV max | 13.4 / 5.0 V | 13.4 V | -0.5 V | 3.54 A | 0.0 A / 0.00 kW / 0.000 J | PASS |
| Reverse battery -14 V | BV min | -0.0 / -0.0 V | -0.0 V | 14.0 V | 0.00 A | 0.0 A / 0.00 kW / 0.000 J | PASS |
| Reverse battery -14 V | BV max | -0.0 / -0.0 V | -0.0 V | 14.0 V | 0.00 A | 0.0 A / 0.00 kW / 0.000 J | PASS |

## D2 = SS56 (60 V, first choice, replaced)

| Case | TVS | VIN1 max / min | VIN_F max | D2 reverse max | L2 peak | TVS peak I / P / energy | Verdict |
|---|---|---|---|---|---|---|---|
| Pulse 1, -150 V, Ri 10, 2 ms | BV min | 14.4 / 5.0 V | 14.2 V | 60.6 V | 15.53 A | 6.0 A / 0.33 kW / 0.115 J | **SS56 > 60 V**, L2 > 4.7 A for 0.1 ms |
| Pulse 1, -150 V, Ri 10, 2 ms | BV max | 14.4 / 5.0 V | 14.2 V | 60.6 V | 15.44 A | 6.1 A / 0.34 kW / 0.112 J | **SS56 > 60 V**, L2 > 4.7 A for 0.1 ms |
| Pulse 3a, -220 V, Ri 50, 100 ns | BV min | 13.6 / 13.5 V | 13.7 V | 36.2 V | 1.55 A | 1.0 A / 0.01 kW / 0.000 J | PASS |
| Pulse 3a, -220 V, Ri 50, 100 ns | BV max | 13.6 / 13.5 V | 13.7 V | 36.4 V | 1.55 A | 1.0 A / 0.01 kW / 0.000 J | PASS |

## SMBJ24CA in place of SMBJ33CA (review proposal, rejected)

| Case | TVS | VIN1 max / min | VIN_F max | D2 reverse max | L2 peak | TVS peak I / P / energy | Verdict |
|---|---|---|---|---|---|---|---|
| Load dump B, suppressed 35 V, Ri 0.5, 400 ms | 24CA BV min | 32.4 / 12.7 V | 32.5 V | -0.4 V | 1.76 A | 3.3 A / 0.11 kW / 46.257 J | **TVS energy** |
| Load dump B, suppressed 35 V, Ri 0.5, 400 ms | 24CA BV max | 32.9 / 12.7 V | 33.0 V | -0.4 V | 1.76 A | 2.4 A / 0.08 kW / 33.341 J | **TVS energy** |
| Pulse 2a, +112 V, Ri 2, 50 us | 24CA BV min | 23.6 / 13.3 V | 31.7 V | 8.2 V | 34.65 A | 3.5 A / 0.11 kW / 0.000 J | PASS |
| Pulse 2a, +112 V, Ri 2, 50 us | 24CA BV max | 23.8 / 13.3 V | 32.1 V | 8.3 V | 35.43 A | 2.6 A / 0.09 kW / 0.000 J | PASS |

## Input filter stability (Middlebrook)

| C1 ESR | Peak \|Zout\| at VIN1 | at | \|Zin\| at 12 V / 9 V / 6 V | Margin at 6 V |
|---|---|---|---|---|
| 0.05 Ω | 0.23 Ω | 6.8 kHz | 8.1 / 4.6 / 2.0 Ω | 18.8 dB |
| 0.3 Ω | 0.27 Ω | 29.9 kHz | 8.1 / 4.6 / 2.0 Ω | 17.6 dB |
| 1.0 Ω | 0.70 Ω | 32.0 kHz | 8.1 / 4.6 / 2.0 Ω | 9.2 dB |
