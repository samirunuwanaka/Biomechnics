#!/usr/bin/env python3
"""Generate the VMC joint-angle range figure used in the report.

The values below are the summary values retained from the supplied report draft.
They are not recalculated from VMC_joint_angles.csv because the supplied CSV has
column headers only and no measured rows. Replace these values only when a populated
Visual Motion Capture angle export is available and has been analysed.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path("figures")
OUT.mkdir(parents=True, exist_ok=True)

# Retained summary measurements from the report draft (degrees).
summary = [
    {"joint": "Left knee", "min": 151.31, "max": 169.74, "rom": 18.43},
    {"joint": "Left ankle", "min": 76.08, "max": 99.70, "rom": 23.62},
]

fig, ax = plt.subplots(figsize=(9, 4.3))
for y, item in enumerate(summary):
    ax.plot([item["min"], item["max"]], [y, y], linewidth=8, solid_capstyle="round")
    ax.scatter([item["min"], item["max"]], [y, y], s=45, zorder=3)
    ax.annotate(f'ROM = {item["rom"]:.2f}°',
                xy=((item["min"] + item["max"]) / 2, y),
                xytext=(0, 22 if y == 0 else 22), textcoords="offset points",
                ha="center", va="bottom")
ax.set_yticks([0, 1], [item["joint"] for item in summary])
ax.set_xlabel("Reported VMC joint angle (degrees)")
ax.set_title("Visual Motion Capture joint-angle ranges")
ax.grid(axis="x", alpha=0.25)
ax.set_xlim(70, 175)
ax.set_ylim(-0.5, 1.5)
fig.tight_layout()
fig.savefig(OUT / "vmc_joint_angle_ranges.png", dpi=220)
plt.close(fig)
print(f"Wrote {OUT / 'vmc_joint_angle_ranges.png'}")
