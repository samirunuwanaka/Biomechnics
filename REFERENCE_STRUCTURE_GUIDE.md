# Reference Report Structure Guide

> **Source**: Extracted from colleague 230052P's practical reports before reference folder deletion.
> **Purpose**: Permanent structural reference for report formatting and content standards.
> **Date Extracted**: 2026-10-20

---

## Template & Cover Page Standard

- **Header**: `BM3500 - Biomechanics`
- **University crest** centered
- **Student details**: Name, Index Number
- **Submission date**
- **LaTeX `\tableofcontents`** with hyperlink styling

## Universal 5-Section Architecture

```
1. Introduction
2. Methods / Methodology
   2.x Apparatus / Equipment
   2.x Procedure / Protocol
   2.x Signal Processing / Data Processing
3. Results
   3.x Individual results subsections with figures
4. Discussion
5. Conclusion
```

## Formatting Conventions

- Python/MATLAB plots with grid lines, axis labels with units, descriptive captions
- Comparative plots: individual conditions first, then overlaid comparison
- Step-by-step equations: formula → variable definitions → numerical substitution → final value with units
- All figures: `Figure X: <descriptive caption>`

---

## Report 1: EMG Practical

### Sections
```
1 Introduction
2 Methods
  2.1 Apparatus
  2.2 Procedure
3 Results
  3.1 Raw EMG Signals
  3.2 RMS
  3.3 MVC Signal
  3.4 MVC Normalization
4 Discussion
5 Conclusion
```

### Key Content Points
- **Apparatus**: Delsys sEMG sensor, Bagnoli-16 amplifier, NI-6220 DAQ, EMGworks 4.0
- **Electrode**: Biceps brachii belly; reference on forehead
- **Sampling**: 4000 Hz (lab sheet specified 2000 Hz)
- **RMS**: 100 ms window = 400 samples at 4000 Hz
- **Protocol**: 1 kg load, 2 kg load, isometric MVC
- **MVC formula**: EMG_%MVC(t) = 100 × EMG_RMS(t) / EMG_MVC_peak
- **Figures**: Raw EMG (1kg, 2kg), RMS (1kg, 2kg, overlay), MVC signal, %MVC (1kg, 2kg, overlay) — 9 figures total
- **Key finding**: 1 kg ≈ 20% MVC, 2 kg ≈ 35% MVC

---

## Report 2: EEG Data Acquisition

### Sections
```
1 Introduction
2 Methodology
  2.1 EEG Data Acquisition
  2.2 Experimental Procedure
  2.3 Signal Processing
3 Results
  3.1 Recorded EEG Signals
  3.2 Single Eye Blink
  3.3 Repeated Eye Blinks
  3.4 Horizontal Eye Movements
  3.5 Circular Eye Movements
  3.6 EEG Signals After Notch Filtering
  3.7 Effect of Additional Notch Filtering
4 Discussion
5 Conclusion
```

### Key Content Points
- **Hardware**: g.tec EEG system, 2 channels, 256 Hz, 120 seconds
- **References**: Ear-lobe and thumb configurations
- **Data**: HDF5 format, Python (h5py, numpy, matplotlib)
- **Filtering**: Band-pass 0.5–8 Hz (EOG isolation), 50 Hz notch (power line)
- **Protocol tasks**: Single blink, repeated blinks, horizontal saccades, circular eye movements
- **Limitation**: No event markers in exported file; manual segment identification
- **Figures**: Full 2-channel trace, single blink zoom, repeated blinks, horizontal movements, circular movements, post-notch trace, raw vs filtered overlay — 7 figures
- **Key finding**: Blink artifacts >150 µV dwarf cerebral EEG (10–50 µV); 50 Hz notch had no visible effect (hardware already filtered)

---

## Report 3: Walking Gait Analysis

### Sections
```
1 Introduction
2 Methodology
  2.1 Experimental Data
  2.2 Marker Selection
  2.3 Data Processing
  2.4 Identification of Gait Events
3 Results
  3.1 Marker Trajectories in the Sagittal Plane
  3.2 Three-Dimensional Marker Trajectories
  3.3 Identification of Gait Events
  3.4 Gait Cycle Duration
  3.5 Stance and Swing Phase Durations
  3.6 Stance and Swing Phase Percentages
  3.7 Stride Length
  3.8 Cadence
  3.9 Average Velocity of Progression
  3.10 Instantaneous Velocity of Progression
  3.11 Thigh Segment Length in 2D and 3D
  3.12 Knee Joint Angle
4 Discussion
5 Conclusion
```

### Key Content Points
- **Data source**: Oxford Gait Lab, Vicon system, 100 Hz
- **Subject**: Healthy 30-year-old male, 1.85 m, 722 N
- **Markers**: RASI, RPSI, RTRO, RLFC, RLMA, RTOE
- **Coordinates**: x=forward, y=mediolateral, z=vertical; units in mm
- **Gait events**: HS1 (frame 204), TO (frame 276), HS2 (frame 313)
- **Key values**: T_c=1.09s, stance=66.06%, swing=33.94%, stride=1.462m, cadence=110.09 steps/min, v_avg=1.343 m/s, knee angle 4°–62°
- **Figures**: X-Z trajectories, 3D trajectories, ankle/toe vertical with events, ankle x-position, pelvis x-position, instantaneous velocity, thigh length 2D vs 3D, knee angle — 8 figures
- **Discussion highlights**: Soft tissue artifact causes 20mm thigh length variation; stance/swing deviates slightly from 60/40 norm; inverted pendulum velocity oscillations
