#!/usr/bin/env python3
"""Generate EMG report figures and per-trial summary from exported CSV files.

Place this script in the same directory as the CSV files and run:
    python emg_generate_figures.py

The CSV metadata records sensor/channel and sampling rate but does NOT record the
applied mass. The grouping below is therefore an editable mapping based on the
current report draft, not something inferred from the CSV contents. Verify the
trial-to-load mapping against the laboratory record before submitting the report.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

FS_DEFAULT = 4000.0
RMS_WINDOW_MS = 100.0

# IMPORTANT: The load is not written in the CSV metadata. Verify these pairs
# against your experiment notes and edit them here if the trial order differs.
LOAD_GROUPS: Dict[str, List[str]] = {
    "1 kg": ["emg_raw_trial_16.csv", "emg_raw_trial_19.csv"],
    "2 kg": ["emg_raw_trial_27.csv", "emg_raw_trial_38.csv"],
}
MVC_FILE = "emg_mvc_sliding_rms.csv"


def read_exported_csv(path: Path) -> Tuple[np.ndarray, np.ndarray, float, int]:
    """Read a LabChart-like CSV with metadata lines before the data header."""
    lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("X [s],"):
            header_idx = i
            break
    if header_idx is None:
        raise ValueError(f"Could not find the 'X [s],...' data header in {path.name}")

    # Parse the sample rate from the first metadata line, falling back to 4 kHz.
    fs = FS_DEFAULT
    first = lines[0]
    match = re.search(r"Sampling frequency:\s*([0-9.eE+-]+)", first)
    if match:
        fs = float(match.group(1))

    from io import StringIO
    import csv

    frame = pd.read_csv(StringIO("\n".join(lines[header_idx:])))
    if frame.shape[1] < 2:
        raise ValueError(f"Expected time and signal columns in {path.name}")
    frame = frame.iloc[:, :2].apply(pd.to_numeric, errors="coerce").dropna()
    t = frame.iloc[:, 0].to_numpy(dtype=float)
    y = frame.iloc[:, 1].to_numpy(dtype=float)
    if len(t) == 0:
        raise ValueError(f"No numeric samples found in {path.name}")
    return t, y, fs, len(y)


def moving_rms(x: np.ndarray, window_samples: int) -> np.ndarray:
    """Centered moving RMS; edge windows use the available samples."""
    window_samples = max(1, int(window_samples))
    squared = np.square(np.asarray(x, dtype=float))
    cumulative = np.concatenate(([0.0], np.cumsum(squared)))
    n = len(squared)
    half_left = window_samples // 2
    half_right = window_samples - half_left
    idx = np.arange(n)
    starts = np.maximum(0, idx - half_left)
    ends = np.minimum(n, idx + half_right)
    sums = cumulative[ends] - cumulative[starts]
    counts = ends - starts
    return np.sqrt(sums / np.maximum(counts, 1))


def microvolts(x: np.ndarray) -> np.ndarray:
    return np.asarray(x) * 1e6


def save_fig(fig: plt.Figure, destination: Path) -> None:
    fig.tight_layout()
    fig.savefig(destination, dpi=250, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parent,
                        help="Directory containing the CSV files (default: script directory)")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Output figure directory (default: <data-dir>/figures)")
    args = parser.parse_args()
    root = args.data_dir.resolve()
    out_dir = (args.output_dir or (root / "figures")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    all_files = [name for names in LOAD_GROUPS.values() for name in names]
    if len(set(all_files)) != len(all_files):
        raise ValueError("Each raw trial must be assigned to only one load group")

    records: Dict[str, dict] = {}
    fs_values = []
    for load, files in LOAD_GROUPS.items():
        for filename in files:
            path = root / filename
            if not path.exists():
                raise FileNotFoundError(f"Missing raw trial CSV: {path}")
            t, raw, fs, n = read_exported_csv(path)
            fs_values.append(fs)
            centered = raw - np.mean(raw)
            win = max(1, round(RMS_WINDOW_MS / 1000 * fs))
            rms = moving_rms(centered, win)
            records[filename] = {
                "load": load, "t": t, "raw": raw, "centered": centered,
                "rms": rms, "fs": fs, "n": n,
                "duration": float(t[-1] - t[0]) if len(t) > 1 else 0.0,
                "rms_mean_v": float(np.mean(rms)),
                "rms_median_v": float(np.median(rms)),
                "rms_peak_v": float(np.max(rms)),
                "raw_peak_to_peak_v": float(np.ptp(raw)),
            }

    # MVC reference was exported by the acquisition software as a sliding-RMS trace.
    mvc_path = root / MVC_FILE
    if not mvc_path.exists():
        raise FileNotFoundError(f"Missing MVC reference CSV: {mvc_path}")
    mvc_t, mvc, mvc_fs, mvc_n = read_exported_csv(mvc_path)
    mvc_peak = float(np.max(mvc))
    if mvc_peak <= 0:
        raise ValueError("MVC reference peak must be positive to normalise the trials")

    # Figure 1: raw voltage for each two-load condition, limited to the first 5 s.
    fig, axes = plt.subplots(2, 1, figsize=(10.5, 7.0), sharex=False)
    for ax, (load, files) in zip(axes, LOAD_GROUPS.items()):
        for filename in files:
            rec = records[filename]
            limit = min(5.0, rec["duration"] + 0.0001)
            mask = rec["t"] <= limit
            ax.plot(rec["t"][mask], microvolts(rec["raw"][mask]),
                    linewidth=0.75, alpha=0.85,
                    label=f"{Path(filename).stem.replace('emg_raw_', '')}")
        ax.set_title(f"{load} load condition")
        ax.set_ylabel("EMG voltage (µV)")
        ax.grid(True, alpha=0.25)
        ax.legend(loc="upper right", fontsize=8)
    axes[-1].set_xlabel("Time (s)")
    fig.suptitle("Raw surface EMG signals (first 5 seconds where available)", y=1.02)
    save_fig(fig, out_dir / "emg_raw_loads.png")

    # Figure 2: 100 ms moving RMS envelopes for each trial.
    fig, axes = plt.subplots(2, 1, figsize=(10.5, 7.2), sharex=False)
    for ax, (load, files) in zip(axes, LOAD_GROUPS.items()):
        for filename in files:
            rec = records[filename]
            ax.plot(rec["t"], microvolts(rec["rms"]), linewidth=1.0,
                    label=f"{Path(filename).stem.replace('emg_raw_', '')} ({rec['duration']:.1f} s)")
        ax.set_title(f"{load} load condition")
        ax.set_ylabel("100 ms RMS (µV)")
        ax.grid(True, alpha=0.25)
        ax.legend(loc="upper right", fontsize=8)
    axes[-1].set_xlabel("Time (s)")
    fig.suptitle("Moving RMS envelopes by load condition and recording", y=1.02)
    save_fig(fig, out_dir / "emg_rms_loads.png")

    # Figure 3: provided MVC sliding-RMS reference.
    fig, ax = plt.subplots(figsize=(10.5, 4.3))
    ax.plot(mvc_t, microvolts(mvc), linewidth=0.9, color="tab:purple")
    ax.axhline(microvolts(np.array([mvc_peak]))[0], color="tab:red", linestyle="--",
               linewidth=1.0, label=f"Peak MVC reference = {mvc_peak * 1e6:.1f} µV")
    ax.set_title("Provided MVC sliding-RMS reference")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Sliding RMS output (µV)")
    ax.grid(True, alpha=0.25)
    ax.legend()
    save_fig(fig, out_dir / "emg_mvc_reference.png")

    # Figure 4: trial RMS normalised to the peak of the supplied MVC RMS trace.
    fig, axes = plt.subplots(2, 1, figsize=(10.5, 7.2), sharex=False)
    for ax, (load, files) in zip(axes, LOAD_GROUPS.items()):
        for filename in files:
            rec = records[filename]
            pct = rec["rms"] / mvc_peak * 100.0
            ax.plot(rec["t"], pct, linewidth=1.0,
                    label=f"{Path(filename).stem.replace('emg_raw_', '')}")
        ax.set_title(f"{load} load condition")
        ax.set_ylabel("Activity (% of peak MVC RMS)")
        ax.grid(True, alpha=0.25)
        ax.legend(loc="upper right", fontsize=8)
    axes[-1].set_xlabel("Time (s)")
    fig.suptitle("MVC-referenced moving RMS envelopes", y=1.02)
    save_fig(fig, out_dir / "emg_mvc_normalised_loads.png")

    # Figure 5: per-recording means grouped into the two loads. Display the two
    # repeat values and group mean; do not hide the small trial count.
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    positions = np.arange(len(LOAD_GROUPS))
    group_means = []
    for i, (load, files) in enumerate(LOAD_GROUPS.items()):
        vals = np.array([records[f]["rms_mean_v"] * 1e6 for f in files])
        group_means.append(float(np.mean(vals)))
        # Small horizontal offsets make each trial visible around the group centre.
        offsets = np.linspace(-0.09, 0.09, len(vals)) if len(vals) > 1 else np.array([0.0])
        ax.scatter(np.full(len(vals), i) + offsets, vals, s=52, zorder=3,
                   label=f"{load} trial means")
        ax.hlines(np.mean(vals), i - 0.25, i + 0.25, linewidth=2.2, color="black")
        if len(vals) > 1:
            ax.vlines(i + 0.18, np.min(vals), np.max(vals), linewidth=1.0,
                      color="black", alpha=0.7)
    ax.set_xticks(positions, list(LOAD_GROUPS.keys()))
    ax.set_ylabel("Mean 100 ms RMS per recording (µV)")
    ax.set_title("Per-recording RMS summary for the two tested loads")
    ax.grid(axis="y", alpha=0.25)
    # Avoid a misleading connecting line; group means are marked with black bars.
    save_fig(fig, out_dir / "emg_load_rms_summary.png")

    # Export detailed trial metrics for reproducibility and table-building.
    rows = []
    for load, files in LOAD_GROUPS.items():
        for filename in files:
            rec = records[filename]
            rows.append({
                "load_condition": load,
                "file": filename,
                "sampling_frequency_Hz": rec["fs"],
                "samples": rec["n"],
                "duration_s": rec["duration"],
                "raw_mean_uV": float(np.mean(rec["raw"]) * 1e6),
                "raw_peak_to_peak_uV": rec["raw_peak_to_peak_v"] * 1e6,
                "mean_100ms_RMS_uV": rec["rms_mean_v"] * 1e6,
                "median_100ms_RMS_uV": rec["rms_median_v"] * 1e6,
                "peak_100ms_RMS_uV": rec["rms_peak_v"] * 1e6,
                "mean_activity_percent_peak_MVC": rec["rms_mean_v"] / mvc_peak * 100.0,
                "peak_activity_percent_peak_MVC": rec["rms_peak_v"] / mvc_peak * 100.0,
            })
    summary = pd.DataFrame(rows)
    summary.to_csv(root / "emg_trial_summary.csv", index=False, float_format="%.5f")

    print(f"Output figures: {out_dir}")
    print(f"RMS window: {RMS_WINDOW_MS:.0f} ms ({round(RMS_WINDOW_MS / 1000 * fs_values[0])} samples at {fs_values[0]:.0f} Hz)")
    print(f"MVC peak reference: {mvc_peak * 1e6:.3f} uV")
    print(summary.to_string(index=False, formatters={
        "duration_s": "{:.3f}".format,
        "mean_100ms_RMS_uV": "{:.3f}".format,
        "median_100ms_RMS_uV": "{:.3f}".format,
        "peak_100ms_RMS_uV": "{:.3f}".format,
        "mean_activity_percent_peak_MVC": "{:.2f}".format,
        "peak_activity_percent_peak_MVC": "{:.2f}".format,
    }))
    print("\nCheck LOAD_GROUPS near the top of this script against your lab notes: the CSV metadata does not contain the applied load.")


if __name__ == "__main__":
    main()
