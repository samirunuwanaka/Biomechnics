#!/usr/bin/env python3
"""
Generate publication-ready plots from a g.tec HDF5 EEG recording.

Install:
    python -m pip install h5py numpy scipy matplotlib

Run:
    python generate_eeg_graphs.py RecordSession_12026.09.28_09.39.53.hdf5

Outputs (saved beside this script, in ./figures by default):
    eeg_recording_overview.png
    eeg_blink_artifact.png
    eeg_notch_filtering.png
    eeg_power_spectrum.png

Important:
- Reads RawData/Samples and uses the sampling rate in acquisition metadata when available.
- This HDF5 file contains three sample columns. Channel labels/reference montage are not
  reliably encoded in the file, so the plots use generic Channel 1..3 labels.
- The script does not claim that the recording is specifically ear-lobe or thumb referenced.
"""
from pathlib import Path
import sys
import re
import xml.etree.ElementTree as ET

import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

FS_DEFAULT = 256.0
OUTPUT_DIR = Path(__file__).resolve().parent / "figures"


def read_fs_and_data(filename):
    with h5py.File(filename, "r") as h5:
        if "RawData/Samples" not in h5:
            raise KeyError("Could not find dataset 'RawData/Samples' in the HDF5 file.")
        data = np.asarray(h5["RawData/Samples"], dtype=float)

        fs = FS_DEFAULT
        if "RawData/AcquisitionTaskDescription" in h5:
            raw = h5["RawData/AcquisitionTaskDescription"][0]
            xml = raw.decode("utf-8", errors="ignore") if isinstance(raw, bytes) else str(raw)
            match = re.search(r"<SamplingFrequency>\s*([0-9.]+)\s*</SamplingFrequency>", xml)
            if match:
                fs = float(match.group(1))
        return data, fs


def filter_signal(x, fs):
    """Return 50-Hz notch and 0.5-8-Hz bandpass versions where valid."""
    y = np.asarray(x, dtype=float)
    # Avoid designing a notch if the Nyquist frequency is too low.
    if 50.0 < fs / 2:
        b, a = signal.iirnotch(50.0, Q=30.0, fs=fs)
        y = signal.filtfilt(b, a, y)
    high = min(8.0, fs * 0.45)
    low = 0.5
    if low < high:
        b, a = signal.butter(4, [low, high], btype="bandpass", fs=fs)
        y = signal.filtfilt(b, a, y)
    return y


def save_fig(fig, name):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / name
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


def main():
    filename = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "RecordSession_12026.09.28_09.39.53.hdf5"
    )
    if not filename.exists():
        raise FileNotFoundError(
            f"Input file not found: {filename}\n"
            "Pass the HDF5 file path as the first command-line argument."
        )

    data, fs = read_fs_and_data(filename)
    if data.ndim != 2:
        raise ValueError(f"Expected a 2-D samples array, got shape {data.shape}")
    n_samples, n_channels = data.shape
    time = np.arange(n_samples) / fs

    # Values in this file's device metadata are specified in microvolts.
    # Plot raw values as recorded; no extra scaling is applied.
    channels = [data[:, i] for i in range(n_channels)]
    filtered = [filter_signal(ch, fs) for ch in channels]

    print(f"Samples: {n_samples}; channels: {n_channels}; fs: {fs:g} Hz; "
          f"duration: {n_samples/fs:.3f} s")
    print("Per-channel raw min/max (file units, metadata says uV):")
    for i, ch in enumerate(channels, 1):
        print(f"  Channel {i}: {np.nanmin(ch):.3f} to {np.nanmax(ch):.3f}")

    # 1. Overview: all available channels over the full recording.
    fig, axes = plt.subplots(n_channels, 1, figsize=(12, max(3.0, 2.2*n_channels)),
                             sharex=True, squeeze=False)
    for i, ax in enumerate(axes[:, 0]):
        ax.plot(time, channels[i], linewidth=0.65)
        ax.set_ylabel(f"Ch {i+1}\n($\\mu$V)")
        ax.grid(True, alpha=0.25)
    axes[-1, 0].set_xlabel("Time (s)")
    fig.suptitle("EEG recording overview (raw data)")
    fig.tight_layout()
    save_fig(fig, "eeg_recording_overview.png")

    # 2. Blink/event plot: choose the largest absolute excursion in Channel 1
    # after excluding the first 1 second. Show a 2-second context window.
    # This is an algorithmic candidate event, not a confirmed blink annotation.
    reference_ch = channels[0]
    valid = np.where(time >= min(1.0, time[-1]))[0]
    peak_idx = valid[np.argmax(np.abs(reference_ch[valid]))] if len(valid) else int(np.argmax(np.abs(reference_ch)))
    center = time[peak_idx]
    left, right = max(time[0], center - 1.0), min(time[-1], center + 1.0)
    mask = (time >= left) & (time <= right)

    fig, ax = plt.subplots(figsize=(12, 5))
    for i, ch in enumerate(channels):
        ax.plot(time[mask], ch[mask], linewidth=0.8, label=f"Channel {i+1}")
    ax.axvline(center, linestyle="--", linewidth=1.0,
               label=f"Largest |Ch 1| sample: {center:.2f} s")
    ax.set_title("Candidate high-amplitude event (not independently labelled as a blink)")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude ($\\mu$V; file units)")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    save_fig(fig, "eeg_blink_artifact.png")

    # 3. Raw and filtered comparison in the same window.
    fig, axes = plt.subplots(n_channels, 1, figsize=(12, max(3.2, 2.5*n_channels)),
                             sharex=True, squeeze=False)
    for i, ax in enumerate(axes[:, 0]):
        ax.plot(time[mask], channels[i][mask], linewidth=0.7, alpha=0.7, label="Raw")
        ax.plot(time[mask], filtered[i][mask], linewidth=1.0, label="50-Hz notch + 0.5–8-Hz bandpass")
        ax.set_ylabel(f"Ch {i+1}\n($\\mu$V)")
        ax.grid(True, alpha=0.25)
        ax.legend(loc="best")
    axes[-1, 0].set_xlabel("Time (s)")
    fig.suptitle("Raw versus filtered signal around candidate event")
    fig.tight_layout()
    save_fig(fig, "eeg_notch_filtering.png")

    # 4. Welch power spectral density for raw and filtered data.
    fig, axes = plt.subplots(n_channels, 1, figsize=(12, max(3.2, 2.5*n_channels)),
                             sharex=True, squeeze=False)
    for i, ax in enumerate(axes[:, 0]):
        nperseg = min(4096, len(channels[i]))
        f_raw, p_raw = signal.welch(channels[i], fs=fs, nperseg=nperseg)
        f_filt, p_filt = signal.welch(filtered[i], fs=fs, nperseg=nperseg)
        ax.semilogy(f_raw, p_raw, linewidth=0.8, label="Raw")
        ax.semilogy(f_filt, p_filt, linewidth=0.8, label="Filtered")
        ax.set_ylabel(f"Ch {i+1}\nPSD ($\\mu$V$^2$/Hz)")
        ax.set_xlim(0, min(80, fs/2))
        ax.grid(True, alpha=0.25)
        ax.legend(loc="best")
    axes[-1, 0].set_xlabel("Frequency (Hz)")
    fig.suptitle("Welch power spectral density")
    fig.tight_layout()
    save_fig(fig, "eeg_power_spectrum.png")


if __name__ == "__main__":
    main()
