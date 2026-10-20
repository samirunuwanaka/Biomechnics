#!/usr/bin/env python3
"""Parse Motion2026.c3d, calculate descriptive 3-D kinematics, and create report figures.

Usage:
  python analyse_motion_c3d.py Motion2026.c3d --outdir figures

Dependencies: numpy, scipy, matplotlib (all common scientific Python packages).
The script intentionally parses this C3D file's standard little-endian, floating-point
point records and validates the expected metadata instead of guessing other modalities.
"""
from __future__ import annotations
import argparse, csv, json, math, struct
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import butter, sosfiltfilt


def _read_param_data(buf: bytes, pos: int):
    """Read one C3D parameter/group record; return record metadata and next position."""
    name_length = struct.unpack_from('<b', buf, pos)[0]
    group_id = struct.unpack_from('<b', buf, pos + 1)[0]
    if name_length == 0:
        return None, pos
    name = buf[pos + 2:pos + 2 + abs(name_length)].decode('latin1', errors='replace').strip()
    offset_pos = pos + 2 + abs(name_length)
    offset = struct.unpack_from('<H', buf, offset_pos)[0]
    next_pos = offset_pos + offset
    rec = {"name": name, "group_id": group_id, "pos": pos, "next": next_pos}
    if group_id < 0:
        rec["kind"] = "group"
        # Group description starts immediately after the offset field.
        dpos = offset_pos + 2
        if dpos < len(buf):
            dlen = buf[dpos]
            rec["description"] = buf[dpos + 1:dpos + 1 + dlen].decode('latin1', errors='replace')
        return rec, next_pos
    rec["kind"] = "parameter"
    q = offset_pos + 2
    data_type = struct.unpack_from('<b', buf, q)[0]
    ndims = buf[q + 1]
    dims = list(buf[q + 2:q + 2 + ndims])
    count = math.prod(dims) if dims else 1
    data_pos = q + 2 + ndims
    nbytes = count * abs(data_type)
    raw = buf[data_pos:data_pos + nbytes]
    rec.update(data_type=data_type, dims=dims, raw=raw)
    dpos = data_pos + nbytes
    if dpos < len(buf):
        dlen = buf[dpos]
        rec["description"] = buf[dpos + 1:dpos + 1 + dlen].decode('latin1', errors='replace')
    return rec, next_pos


def parse_c3d(path: Path):
    buf = path.read_bytes()
    if len(buf) < 1024:
        raise ValueError("File is too short to be a C3D file.")
    if buf[1] != 0x50:
        raise ValueError(f"Expected little-endian C3D key 0x50, found 0x{buf[1]:02x}; this script does not guess byte order.")
    n_points = struct.unpack_from('<H', buf, 2)[0]
    header_analog_measures = struct.unpack_from('<H', buf, 4)[0]
    first_frame = struct.unpack_from('<H', buf, 6)[0]
    last_frame = struct.unpack_from('<H', buf, 8)[0]
    header_scale = struct.unpack_from('<f', buf, 12)[0]
    data_block = struct.unpack_from('<H', buf, 16)[0]
    analog_samples_per_frame = struct.unpack_from('<H', buf, 18)[0]
    frame_rate = struct.unpack_from('<f', buf, 20)[0]
    param_block = buf[0]
    param_pos = (param_block - 1) * 512 + 4
    group_names, params = {}, {}
    for _ in range(3000):
        rec, next_pos = _read_param_data(buf, param_pos)
        if rec is None:
            break
        if rec["kind"] == "group":
            group_names[-rec["group_id"]] = rec["name"]
        else:
            group_name = group_names.get(rec["group_id"], str(rec["group_id"]))
            dt, raw, dims = rec["data_type"], rec["raw"], rec["dims"]
            count = math.prod(dims) if dims else 1
            if abs(dt) == 1:
                val = raw.decode('latin1', errors='replace')
            elif abs(dt) == 2:
                values = list(struct.unpack('<' + 'h' * (len(raw) // 2), raw)) if raw else []
                val = values[0] if len(values) == 1 else values
            elif abs(dt) == 4:
                values = list(struct.unpack('<' + 'f' * (len(raw) // 4), raw)) if raw else []
                val = values[0] if len(values) == 1 else values
            else:
                val = raw
            params[(group_name, rec["name"])] = {"value": val, "dims": dims, "raw": raw, "type": dt}
        if next_pos <= param_pos or next_pos > len(buf):
            raise ValueError("Malformed C3D parameter record offset.")
        param_pos = next_pos
    def pv(group, name, default=None):
        item = params.get((group, name))
        return item["value"] if item else default
    n_points = int(pv('POINT', 'USED', n_points))
    frames = int(pv('POINT', 'FRAMES', last_frame - first_frame + 1))
    data_block = int(pv('POINT', 'DATA_START', data_block))
    point_scale = float(pv('POINT', 'SCALE', header_scale))
    frame_rate = float(pv('POINT', 'RATE', frame_rate))
    units = str(pv('POINT', 'UNITS', 'unknown')).strip()
    labels_string = str(pv('POINT', 'LABELS', ''))
    label_param = params.get(('POINT', 'LABELS'))
    label_width = label_param['dims'][0] if label_param and label_param['dims'] else 0
    labels = [labels_string[i:i + label_width].strip() for i in range(0, len(labels_string), label_width)] if label_width else []
    desc_string = str(pv('POINT', 'DESCRIPTIONS', ''))
    desc_param = params.get(('POINT', 'DESCRIPTIONS'))
    desc_width = desc_param['dims'][0] if desc_param and desc_param['dims'] else 0
    descriptions = [desc_string[i:i + desc_width].strip() for i in range(0, len(desc_string), desc_width)] if desc_width else []
    analog_used = int(pv('ANALOG', 'USED', 0))
    data_offset = (data_block - 1) * 512
    if point_scale >= 0:
        raise ValueError(f"POINT:SCALE={point_scale}; integer point format is not implemented by this focused decoder.")
    raw_count = frames * n_points * 4
    raw = np.frombuffer(buf, dtype='<f4', count=raw_count, offset=data_offset)
    if raw.size != raw_count:
        raise ValueError(f"Point section is truncated: expected {raw_count} float values, found {raw.size}.")
    points = raw.reshape(frames, n_points, 4)
    xyz = points[:, :, :3].astype(float)
    residual = points[:, :, 3].astype(float)
    if len(labels) != n_points:
        labels = [f"Point {i+1}" for i in range(n_points)]
    if len(descriptions) != n_points:
        descriptions = labels.copy()
    if units.lower() in ('mm', 'millimeter', 'millimeters'):
        xyz_m = xyz / 1000.0
    elif units.lower() in ('m', 'meter', 'meters'):
        xyz_m = xyz.copy()
    else:
        raise ValueError(f"Unsupported/unverified POINT:UNITS={units!r}; refusing to assume units.")
    meta = {
        "file": path.name, "file_size_bytes": len(buf), "n_points": n_points,
        "header_analog_measures_per_frame": header_analog_measures,
        "analog_samples_per_frame_header": analog_samples_per_frame,
        "analog_channels_used": analog_used, "first_frame": first_frame,
        "last_frame": last_frame, "frames": frames, "frame_rate_hz": frame_rate,
        "duration_s": (frames - 1) / frame_rate, "data_start_block": data_block,
        "point_scale": point_scale, "point_units": units, "labels": labels,
        "descriptions": descriptions, "residual_min": float(np.min(residual)),
        "residual_max": float(np.max(residual)),
    }
    return meta, xyz, xyz_m, residual


def calc_angle_deg(a, b):
    dot = np.sum(a * b, axis=1)
    den = np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)
    ratio = np.divide(dot, den, out=np.full_like(dot, np.nan, dtype=float), where=den > 1e-12)
    return np.degrees(np.arccos(np.clip(ratio, -1, 1)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('c3d', type=Path, help='Path to Motion2026.c3d')
    ap.add_argument('--outdir', type=Path, default=Path('figures'))
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    meta, xyz_mm, r_m, residual = parse_c3d(args.c3d)
    N, M, _ = r_m.shape
    labels = meta['labels']
    descriptions = meta['descriptions']
    time_s = np.arange(N) / meta['frame_rate_hz']
    valid = np.all(np.isfinite(r_m), axis=2) & ~np.all(xyz_mm == 0, axis=2)
    missing_counts = (~valid).sum(axis=0)
    if np.any(missing_counts):
        # Interpolate only isolated/missing coordinate rows; document count in generated summary.
        r_fill = r_m.copy()
        for j in range(M):
            good = np.where(valid[:, j])[0]
            if len(good) < 2:
                raise ValueError(f"Not enough valid points for {labels[j]}.")
            for k in range(3):
                r_fill[:, j, k] = np.interp(np.arange(N), good, r_m[good, j, k])
    else:
        r_fill = r_m.copy()
    # Use a zero-phase low-pass filter before differentiating, to avoid magnifying marker jitter.
    fs = meta['frame_rate_hz']; cutoff = 6.0
    sos = butter(4, cutoff, btype='lowpass', fs=fs, output='sos')
    r_filt = sosfiltfilt(sos, r_fill, axis=0)
    vel = np.gradient(r_filt, 1/fs, axis=0, edge_order=2)
    acc = np.gradient(vel, 1/fs, axis=0, edge_order=2)
    speed = np.linalg.norm(vel, axis=2)
    accel = np.linalg.norm(acc, axis=2)

    marker_stats = []
    for j, lab in enumerate(labels):
        entry = {"marker_label": lab, "marker_description": descriptions[j], "invalid_frames": int(missing_counts[j])}
        for c, axis in enumerate('XYZ'):
            entry[f'{axis}_min_m'] = float(np.min(r_m[valid[:, j], j, c])) if valid[:, j].any() else float('nan')
            entry[f'{axis}_max_m'] = float(np.max(r_m[valid[:, j], j, c])) if valid[:, j].any() else float('nan')
        entry['mean_speed_m_s_filtered'] = float(np.mean(speed[:, j]))
        entry['peak_speed_m_s_filtered'] = float(np.max(speed[:, j]))
        entry['peak_acceleration_m_s2_filtered'] = float(np.max(accel[:, j]))
        sample_displacement = np.linalg.norm(np.diff(r_m[:, j, :], axis=0), axis=1)
        max_step_index = int(np.argmax(sample_displacement))
        entry['max_adjacent_frame_displacement_mm'] = float(np.max(sample_displacement) * 1000.0)
        entry['max_step_between_frames'] = f"{max_step_index + 1}-{max_step_index + 2}"
        entry['frames_with_step_over_20mm'] = int(np.sum(sample_displacement > 0.020))
        marker_stats.append(entry)

    # Generate plots with plain axis labels, without assuming global axis anatomical direction.
    plt.rcParams.update({'font.size': 9, 'axes.titlesize': 11, 'axes.labelsize': 9, 'legend.fontsize': 8})
    # 3D spatial trajectories
    fig = plt.figure(figsize=(8.5, 6.2))
    ax = fig.add_subplot(111, projection='3d')
    for j, lab in enumerate(labels):
        ax.plot(r_m[:, j, 0], r_m[:, j, 1], r_m[:, j, 2], linewidth=1.0, label=f'{descriptions[j]} ({lab})')
    ax.set_xlabel('X (m)'); ax.set_ylabel('Y (m)'); ax.set_zlabel('Z (m)')
    ax.set_title('3D trajectories of the four recorded markers')
    ax.legend(loc='best')
    fig.tight_layout(); fig.savefig(args.outdir/'marker_trajectories_3d.png', dpi=220); plt.close(fig)

    # coordinate time-series, 3 stacked axis plots
    fig, axs = plt.subplots(3, 1, figsize=(9, 7.5), sharex=True)
    for c, axis in enumerate('XYZ'):
        for j, lab in enumerate(labels):
            axs[c].plot(time_s, r_m[:, j, c], linewidth=.75, label=descriptions[j])
        axs[c].set_ylabel(f'{axis} (m)'); axs[c].grid(True, alpha=.25)
    axs[0].set_title('Recorded marker coordinates versus time')
    axs[-1].set_xlabel('Time (s)'); axs[0].legend(ncol=2, loc='upper right')
    fig.tight_layout(); fig.savefig(args.outdir/'marker_coordinates_time.png', dpi=220); plt.close(fig)

    # adjacent-frame displacement: an important data-quality diagnostic
    frame_step = np.linalg.norm(np.diff(r_m, axis=0), axis=2) * 1000.0
    fig, ax = plt.subplots(figsize=(9, 4.8))
    for j, lab in enumerate(labels):
        ax.plot(time_s[1:], frame_step[:, j], linewidth=.75, label=descriptions[j])
    ax.set_title('Displacement between adjacent marker samples (10 ms apart)')
    ax.set_xlabel('Time (s)'); ax.set_ylabel('Displacement (mm per sample)'); ax.grid(True, alpha=.25); ax.legend(ncol=2)
    fig.tight_layout(); fig.savefig(args.outdir/'framewise_displacement.png', dpi=220); plt.close(fig)

    # filtered velocity magnitudes
    fig, ax = plt.subplots(figsize=(9, 4.8))
    for j, lab in enumerate(labels):
        ax.plot(time_s, speed[:, j], linewidth=.85, label=descriptions[j])
    ax.set_title(f'Marker speed after {cutoff:g} Hz low-pass filtering')
    ax.set_xlabel('Time (s)'); ax.set_ylabel('Speed (m/s)'); ax.grid(True, alpha=.25); ax.legend(ncol=2)
    fig.tight_layout(); fig.savefig(args.outdir/'marker_speed_time.png', dpi=220); plt.close(fig)

    # segment lengths, based on raw reconstructed coordinates
    segment_specs = [('Thigh (hip-knee)', 0, 1), ('Shank (knee-ankle)', 1, 2), ('Foot (ankle-foot)', 2, 3)]
    seg_lengths = {}
    fig, ax = plt.subplots(figsize=(9, 4.8))
    for name, i, j in segment_specs:
        length = np.linalg.norm(r_m[:, i, :] - r_m[:, j, :], axis=1)
        seg_lengths[name] = length
        ax.plot(time_s, length, linewidth=.8, label=name)
    ax.set_title('Inter-marker segment lengths (raw coordinates)')
    ax.set_xlabel('Time (s)'); ax.set_ylabel('Distance (m)'); ax.grid(True, alpha=.25); ax.legend()
    fig.tight_layout(); fig.savefig(args.outdir/'segment_lengths_time.png', dpi=220); plt.close(fig)

    joint_rows = []
    if M >= 4:
        hip, knee, ankle, foot = [r_filt[:, j, :] for j in range(4)]
        thigh_vec = hip - knee
        shank_vec_from_knee = ankle - knee
        knee_included = calc_angle_deg(thigh_vec, shank_vec_from_knee)
        knee_flex = 180.0 - knee_included
        shank_up = knee - ankle
        foot_vec = foot - ankle
        ankle_included = calc_angle_deg(shank_up, foot_vec)
        d_knee = np.gradient(knee_flex, 1/fs, edge_order=2)
        dd_knee = np.gradient(d_knee, 1/fs, edge_order=2)
        d_ankle = np.gradient(ankle_included, 1/fs, edge_order=2)
        dd_ankle = np.gradient(d_ankle, 1/fs, edge_order=2)
        fig, axs = plt.subplots(2, 1, figsize=(9, 6.3), sharex=True)
        axs[0].plot(time_s, knee_flex, linewidth=.9)
        axs[0].set_ylabel('Flexion proxy (degrees)'); axs[0].set_title('Knee flexion proxy: 180° minus 3-point included angle'); axs[0].grid(True, alpha=.25)
        axs[1].plot(time_s, ankle_included, linewidth=.9)
        axs[1].set_ylabel('Included angle (degrees)'); axs[1].set_xlabel('Time (s)'); axs[1].set_title('Ankle/shank-foot included angle (unsigned)'); axs[1].grid(True, alpha=.25)
        fig.tight_layout(); fig.savefig(args.outdir/'joint_angles_time.png', dpi=220); plt.close(fig)
        joint_rows = [
            {'measure':'Knee flexion proxy', 'minimum_deg':float(np.nanmin(knee_flex)), 'maximum_deg':float(np.nanmax(knee_flex)), 'range_deg':float(np.nanmax(knee_flex)-np.nanmin(knee_flex)), 'peak_abs_angular_velocity_deg_s':float(np.nanmax(np.abs(d_knee))), 'peak_abs_angular_acceleration_deg_s2':float(np.nanmax(np.abs(dd_knee)))},
            {'measure':'Ankle/shank-foot included angle (unsigned)', 'minimum_deg':float(np.nanmin(ankle_included)), 'maximum_deg':float(np.nanmax(ankle_included)), 'range_deg':float(np.nanmax(ankle_included)-np.nanmin(ankle_included)), 'peak_abs_angular_velocity_deg_s':float(np.nanmax(np.abs(d_ankle))), 'peak_abs_angular_acceleration_deg_s2':float(np.nanmax(np.abs(dd_ankle)))},
        ]

    # summaries
    summary_csv = args.outdir/'marker_summary.csv'
    with summary_csv.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(marker_stats[0].keys()))
        writer.writeheader(); writer.writerows(marker_stats)
    seg_stats = []
    for name, length in seg_lengths.items():
        seg_stats.append({'segment':name, 'mean_m':float(np.mean(length)), 'std_m':float(np.std(length, ddof=1)), 'min_m':float(np.min(length)), 'max_m':float(np.max(length)), 'range_mm':float((np.max(length)-np.min(length))*1000)})
    with (args.outdir/'segment_summary.csv').open('w', newline='', encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(seg_stats[0].keys())); writer.writeheader(); writer.writerows(seg_stats)
    if joint_rows:
        with (args.outdir/'joint_summary.csv').open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=list(joint_rows[0].keys()));writer.writeheader();writer.writerows(joint_rows)
    meta['invalid_frames_per_marker'] = {labels[i]:int(missing_counts[i]) for i in range(M)}
    meta['filter_for_derivatives'] = {'type':'4th-order Butterworth low-pass, zero-phase application', 'cutoff_hz':cutoff}
    meta['all_fourth_components_zero'] = bool(np.all(residual == 0))
    (args.outdir/'c3d_metadata_summary.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')
    print(json.dumps(meta, indent=2))
    print('\nMARKER SUMMARY')
    for row in marker_stats: print(row)
    print('\nSEGMENT SUMMARY')
    for row in seg_stats: print(row)
    print('\nJOINT SUMMARY')
    for row in joint_rows: print(row)
    print(f'\nWrote figures and summary files to {args.outdir.resolve()}')

if __name__ == '__main__':
    main()
