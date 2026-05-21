import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import sys

# Configuration - update these to match your HPC paths if they differ
SAVEDIR = '/home/al8425b-hpc/NASA/cropTest/testData/updatedOutput/'

def verify_latest():
    files = sorted(glob.glob(os.path.join(SAVEDIR, "*.npz")))
    if not files:
        print(f"No .npz files found in {SAVEDIR}")
        return

    sample_path = files[0]
    print(f"Verifying sample: {sample_path}")
    
    try:
        with np.load(sample_path, allow_pickle=True) as data_load:
            chip = data_load['chip']
            meta = data_load['data'].item()
    except Exception as e:
        print(f"Error loading {sample_path}: {e}")
        return

    print(f"\n--- Statistics ---")
    print(f"Chip Shape (T, H, W, C): {chip.shape}")
    print(f"Expected: (7, 512, 512, 16)")
    
    # Check for identical timesteps
    print(f"\n--- Temporal Uniqueness Check ---")
    for i in range(chip.shape[0] - 1):
        is_same = np.array_equal(chip[i], chip[i+1])
        print(f"Is T={i} identical to T={i+1}? {'YES (ERROR)' if is_same else 'No (Good)'}")

    # Print detailed metadata
    print(f"\n--- Detailed Metadata ---")
    print(f"Offsets: {meta.get('ABI_offsets_minutes')}")
    print(f"Valid Mask: {meta.get('ABI_valid_mask')}")
    
    if 'ABI_time_hour' in meta and 'ABI_time_minute' in meta:
        times = [f"{h}:{m}" for h, m in zip(meta['ABI_time_hour'], meta['ABI_time_minute'])]
        print(f"Resolved Times (HH:MM): {times}")
    
    if 'ABI_time_utc_hour_decimal' in meta:
        print(f"UTC Decimal Hours: {meta['ABI_time_utc_hour_decimal']}")

    # Check Cloud Mask values
    if 'Cloud_mask' in meta:
        mask = meta['Cloud_mask']
        print(f"\n--- Cloud Mask Check ---")
        print(f"Mask Min: {mask.min()}, Max: {mask.max()}, Unique values: {np.unique(mask)}")
        if mask.max() == 0:
            print("WARNING: Cloud mask is empty (all zeros). Checking height units...")

    # Generate Diagnostic Plot
    plt.switch_backend('Agg')
    fig = plt.figure(figsize=(25, 12))

    # Calculate global vmin/vmax for Band 14 (IR)
    band_idx = 13 # Channel 14
    v_min = np.nanmin(chip[:, :, :, band_idx])
    v_max = np.nanmax(chip[:, :, :, band_idx])
    print(f"IR Band Stats - Min: {v_min:.2f}, Max: {v_max:.2f}")

    # Plot 1: Temporal Sequence (Fixed Scale)
    n_steps = chip.shape[0]
    for i in range(n_steps):
        ax = fig.add_subplot(3, n_steps, i + 1)
        ax.imshow(chip[i, :, :, band_idx], cmap='gray', vmin=v_min, vmax=v_max)
        offset = meta['ABI_offsets_minutes'][i] if 'ABI_offsets_minutes' in meta else i
        ax.set_title(f"T={offset}m")
        ax.axis('off')

    # Plot 2: Difference from Central Timestep (T=0)
    center_idx = 0
    if 'ABI_offsets_minutes' in meta:
        offsets = list(meta['ABI_offsets_minutes'])
        if 0 in offsets:
            center_idx = offsets.index(0)
    
    for i in range(n_steps):
        ax = fig.add_subplot(3, n_steps, n_steps + i + 1)
        diff = chip[i, :, :, band_idx] - chip[center_idx, :, :, band_idx]
        d_limit = max(abs(np.nanmin(diff)), abs(np.nanmax(diff)))
        ax.imshow(diff, cmap='RdBu_r', vmin=-d_limit, vmax=d_limit)
        ax.set_title(f"Diff (T{meta['ABI_offsets_minutes'][i]} - T0)")
        ax.axis('off')

    # Plot 3: CloudSat Profile
    ax_cs = fig.add_subplot(3, 1, 3)
    if 'Cloud_mask' in meta:
        mask = meta['Cloud_mask']
        im = ax_cs.imshow(mask.T, origin='lower', aspect='auto', cmap='tab10')
        plt.colorbar(im, ax=ax_cs, label='Cloud Type')
        ax_cs.set_title("CloudSat Vertical Profile (Cloud Types)")
        ax_cs.set_xlabel("Along-track Profile Index")
        ax_cs.set_ylabel("Level (0-40)")
    else:
        ax_cs.text(0.5, 0.5, "No Cloud_mask found in metadata", ha='center')

    plot_name = "verification_plot.png"
    plt.tight_layout()
    plt.savefig(plot_name)
    print(f"\n--- Visual Check ---")
    print(f"Saved diagnostic plot to: {os.path.abspath(plot_name)}")
    print(f"Download this file to check if the track features move vertically!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        SAVEDIR = sys.argv[1]
    verify_latest()
