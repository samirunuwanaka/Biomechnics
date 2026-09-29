# Biomechanics Practical Reports & Biomedical Signal Analysis

A comprehensive repository containing practical laboratory reports, data processing scripts, and clinical signal analysis workflows across key biomechanics & electrophysiological domains.

---

## Repository Structure & Overview

```mermaid
graph TD
    Root[Biomechanics Repository]
    
    Root --> EMG[1. EMG Practical]
    Root --> EEG[2. EEG Practical]
    Root --> Gait[3. Gait Analysis]
    Root --> Motion[4. Motion Analysis]

    EMG --> EMG_CSV[Raw & Sliding RMS CSV Data]
    EMG --> EMG_TEX[LaTeX Practical Report main.tex]
    
    EEG --> EEG_Ref[Reference Electrode Study]
    EEG --> EEG_Blink[Eye Blink Artifact Dynamics]

    Gait --> Gait_M[MATLAB Processing Script gait230449N.m]
    Gait --> Gait_CSV[Marker Trajectory Data markers.csv]

    Motion --> Motion_C3D[3D Motion Capture C3D/TXT Data]
    Motion --> Motion_Sim[Interactive HTML Simulator]
```

---

## Modules Breakdown

### 1. Electromyography (EMG) Practical
* **Focus:** Muscle activation dynamics, Maximum Voluntary Contraction (MVC), and sliding RMS envelope calculation.
* **Key Files:**
  * Raw trial datasets (`emg_raw_trial_*.csv`)
  * Processed signal features (`emg_mvc_sliding_rms.csv`)
  * Full LaTeX practical report (`main.tex`, compiled `main.pdf`)

### 2. Electroencephalography (EEG) Practical
* **Focus:** Impact of reference electrode selection (**Ear Lobe** vs. non-cephalic **Left Thumb** & **Right Thumb**) on signal SNR and propagation of **Eye Blink Artifacts**.

```mermaid
sequenceDiagram
    autonumber
    participant Subject
    participant Prefrontal_EEG as Prefrontal Channels (Fp1/Fp2)
    participant Reference as Reference Electrode
    participant Output as Signal Analysis

    Subject->>Prefrontal_EEG: Eye Blink Event (EOG Potential Shift)
    Prefrontal_EEG->>Reference: Potential Difference
    alt Ear Lobe Reference (Cephalic)
        Reference-->>Output: Clean Signal with Localized Frontal Blink Deflection (~100-200 µV)
    else Thumb Reference (Non-cephalic)
        Reference-->>Output: High Noise Floor + ECG/EMG & Widespread Artifact Overlay
    end
```

### 3. Gait Analysis
* **Focus:** Lower limb kinematics and stride phase segmentation using optical motion capture marker tracking.
* **Key Files:**
  * Trajectory coordinates (`markers.csv`)
  * Analysis & visualization script (`gait230449N.m`)
  * Reference gait cycle presentation (`Gait Analysis - Reference Slides.pptx`)

### 4. Motion Analysis Practical
* **Focus:** 3D biomechanical motion reconstruction and interactive kinematics preview.
* **Key Files:**
  * Motion capture data files (`Group2_2026.c3d`, `Group2_2026_(Coordinates).txt`)
  * Visualization simulator (`simulator.html`)

---

## Signal Processing & Analysis Pipeline

```mermaid
flowchart LR
    A[Raw Biosignal Data] --> B[Filtering & Preprocessing]
    B --> C{Module Target}
    C -->|EMG| D[MVC Normalization & Sliding RMS]
    C -->|EEG| E[ICA Ocular Artifact Removal & SNR Assessment]
    C -->|Gait/Motion| F[Kinematic Trajectory & Joint Angle Calculation]
    D --> G[Report & Data Artifact Generation]
    E --> G
    F --> G
```

---

## Getting Started

1. **LaTeX Compiling (EMG Report):**
   ```bash
   cd "EMG practicle"
   pdflatex main.tex
   ```
2. **Gait Kinematics (MATLAB):**
   Open `gait230449N.m` in MATLAB to plot trajectory data from `markers.csv`.
3. **Motion Simulator:**
   Open `Motion analysis practicle/simulator.html` in standard web browsers.
