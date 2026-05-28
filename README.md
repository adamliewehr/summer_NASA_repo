# CloudSat–ABI Collocation Pipeline

This toolkit manages the extraction, alignment, and verification of spatiotemporal training samples matching CloudSat vertical profiles with GOES-16 ABI imagery.

## 1. Core Processing

### `crop_abi_multitemporal.py`

The primary factory script. It iterates through CloudSat orbits and extracts ABI chips.

- **Action**: Processes raw HDF/NetCDF data into `.npz` files.
- **Key Logic**:
  - Rotates imagery so the satellite track is perfectly vertical.
  - Spans 7 timesteps (every 20 mins, centered on CloudSat time).
  - Collects 930 profiles (~1,024km) to match the full height of the 512-pixel ABI chip.
- **Usage**:
  ```bash
  python crop_abi_multitemporal.py <YEAR> <DAY_SKIP>
  ```

---

## 2. Verification & Diagnostics

### `verifyOutputs.py`

A high-speed check to ensure your processing is working as expected.

- **Output**: Console statistics and a `verification_plot.png`.
- **Use this to check**:
  - **Bitwise Uniqueness**: Confirms that different timesteps are loading different files.
  - **Cloud Mask Unit Fix**: Checks if the 500m binning is producing data (not all zeros).
  - **Difference Maps**: Shows a "heat map" of cloud movement over time.
- **Usage**:
  ```bash
  python verifyOutputs.py /path/to/outputs/
  ```

### `dataInspector.py`

A "deep dive" tool to look at the internal structure of any file in the pipeline.

- **Output**: Metadata, variable names, shapes, and value ranges.
- **Use this to check**:
  - What variables are inside a raw CloudSat HDF?
  - What are the radiance ranges in an ABI NetCDF?
  - What keys are available in the final `.npz` files?
- **Usage**:
  ```bash
  python dataInspector.py cloudsat <FILE.hdf>
  python dataInspector.py abi <FILE.nc>
  python dataInspector.py output <FILE.npz>
  ```

---

## 3. Advanced Visualization

### `visualizeChip.py`

Creates a high-resolution dashboard for a single processed sample.

- **Output**: A `viz_<FILENAME>.png` dashboard.
- **Includes**:
  - **Spectral Grid**: All 16 ABI bands at T=0 with the CloudSat track overlaid in red.
  - **Temporal Sequence**: A timeline of the IR band showing how clouds move across the track.
  - **Vertical Profile**: The 930x40 side-view of the clouds.
- **Special Feature**: Uses percentile-based contrast stretching to ensure you can see clouds clearly even in raw 12-bit data.
- **Usage**:
  ```bash
  python visualizeChip.py /path/to/sample.npz
  ```

---

## Core Data Concepts

- **The Chip**: A `(7, 512, 512, 16)` matrix. Covers 1,024km x 1,024km at 2km resolution.
- **The Mask**: A `(930, 40)` matrix. Represents 40 vertical levels (500m each) for the 930 profiles that fit inside the 512-pixel chip height.
- **Alignment**: The red dashed line in all visualizations represents the **center column** of the ABI chip, which is where the CloudSat vertical labels "live."
