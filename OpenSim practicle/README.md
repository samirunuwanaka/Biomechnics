# OpenSim Biomechanics & Musculoskeletal Modeling Practical

![OpenSim](https://img.shields.io/badge/OpenSim-4.6-blue)
![Field](https://img.shields.io/badge/Field-Biomechanics-orange)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Author](https://img.shields.io/badge/Author-Samiru%20Nuwanaka-purple)

> Musculoskeletal simulation and biomechanical evaluation using **OpenSim 4.6** to investigate crouch gait kinematics and evaluate surgical hamstring lengthening indications.

---

## Overview

This module focuses on modeling human gait abnormalities using **OpenSim 4.6**. The practical analyzes:
1. **Knee Joint Kinematics:** Quantitative comparison of right knee flexion angle (`knee_angle_r`) across normal gait (`normal.mot`) and crouch gait (`crouch1.mot`) cycles.
2. **Hamstring Muscle-Tendon Length:** Tracking semitendinosus muscle-tendon length (`semiten_r`) in `gait2392.osim` to evaluate clinical hypotheses regarding surgical hamstring lengthening.

---

## Directory Structure

```text
OpenSim practicle/
├── README.md                              # Module documentation
├── campus_logo.png                        # University logo for report
├── Crouch_Normal_knee_angles_r.png        # Knee angle kinematic comparison plot
├── gait.xlsx                              # Exported gait cycle kinematics spreadsheet
└── report.tex                             # Standardized LaTeX practical report
```

---

## Lab Sheet Summary & Key Findings

* **Module:** BM3500 - Biomedical Engineering Applications
* **Laboratory:** Bionics Laboratory
* **Model:** `gait2392.osim` (23 degrees of freedom, 92 muscle-tendon actuators)
* **Clinical Finding:** Stance knee flexion in crouch gait exceeds $35^\circ$--$40^\circ$. However, peak semitendinosus muscle-tendon length during crouch gait is comparable to or greater than in normal gait due to concurrent hip flexion. Therefore, **surgical hamstring lengthening is not indicated** for this subject.

---

## LaTeX Report Compilation

To compile the LaTeX practical report:

```bash
cd "OpenSim practicle"
pdflatex report.tex
```

---

## Command & Workflow Execution Placeholders

Methodological execution scripts and OpenSim commands are structured with clear placeholders in `report.tex`:

```bash
# [COMMAND PLACEHOLDER 1: Load Models and Motion Files]
<INSERT_OPENSIM_MODEL_LOAD_COMMAND_HERE>

# [COMMAND PLACEHOLDER 2: Plot Knee Flexion Kinematics]
<INSERT_KNEE_ANGLE_PLOT_COMMAND_HERE>

# [COMMAND PLACEHOLDER 3: Extract Semitendinosus Muscle-Tendon Length]
<INSERT_MUSCLE_ANALYSIS_COMMAND_HERE>
```
