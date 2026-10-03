# 3D Motion Analysis Practical Report & Simulation

This module contains 3D motion capture datasets, binary C3D trajectory files, interactive web-based motion visualization, and the formal LaTeX practical report.

---

## Overview

Optical motion capture system tracking passive reflective markers placed on anatomical landmarks to reconstruct 3D spatial trajectories ($x(t), y(t), z(t)$), joint kinematics, and digital motion playback.

### Key Features
* **C3D Binary Parsing:** Reading binary motion files (`Group2_2026.c3d`, `Motion2026.c3d`).
* **Coordinate Reconstruction:** ASCII point trajectories (`Group2_2026_(Coordinates).txt`).
* **Web Simulator:** Real-time HTML3D skeletal animation viewer (`simulator.html`).
* **Structured Report:** Formal LaTeX report following the standard laboratory template (`report.tex`).

---

## Directory Structure

```text
Motion analysis practicle/
├── README.md                          # Module documentation
├── campus_logo.png                    # University logo for report
├── Group2_2026.c3d                    # 3D motion capture binary C3D dataset
├── Group2_2026.txt                    # Capture session metadata summary
├── Group2_2026_(Coordinates).txt      # 3D marker spatial coordinates
├── Motion2026.c3d                     # Additional motion capture dataset
├── simulator.html                     # Web-based interactive 3D motion rendering engine
└── report.tex                         # Practical LaTeX report source file
```

---

## LaTeX Report Compilation

To compile the LaTeX report into PDF:

```bash
cd "Motion analysis practicle"
pdflatex report.tex
```

---

## Interactive Web Simulator

To view the 3D motion simulation, open `simulator.html` in any standard modern web browser.

---

## Execution Command Placeholders

Methodological execution scripts and commands are structured with clear placeholders in `report.tex`:

```bash
# [COMMAND PLACEHOLDER 1: Parse C3D Binary Dataset]
<INSERT_C3D_PARSER_COMMAND_HERE>

# [COMMAND PLACEHOLDER 2: Compute Kinematic Derivatives & Joint Angles]
<INSERT_KINEMATICS_CALC_COMMAND_HERE>

# [COMMAND PLACEHOLDER 3: Generate Web Simulator Dataset]
<INSERT_SIMULATOR_EXPORT_COMMAND_HERE>
```
