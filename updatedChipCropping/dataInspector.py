import numpy as np
import os
import sys
import glob
import netCDF4 as nc
from pyhdf.SD import SD, SDC
from pyhdf.HDF import HDF

def inspect_cloudsat(file_path):
    print(f"\n{'='*20} CLOUDSAT INSPECTION {'='*20}")
    print(f"File: {os.path.basename(file_path)}")
    
    sd = SD(file_path, SDC.READ)
    datasets = sd.datasets()
    print(f"\nScientific Datasets (SDS) found: {len(datasets)}")
    for name, info in datasets.items():
        # info is (dims, shape, type, index)
        print(f"  - {name:20} Shape: {info[1]}")
    
    # Show a sample of the vertical data
    base = sd.select('CloudLayerBase').get()
    print(f"\nSample Vertical Data (CloudLayerBase):")
    print(f"  First profile (10 layers): {base[0]}")
    print(f"  Units: Meters (usually)")
    sd.end()

def inspect_abi(file_path):
    print(f"\n{'='*20} ABI L1B INSPECTION {'='*20}")
    print(f"File: {os.path.basename(file_path)}")
    
    ds = nc.Dataset(file_path, 'r')
    print(f"\nVariables found: {len(ds.variables)}")
    
    rad = ds.variables['Rad']
    print(f"  - Rad (Radiances) Shape: {rad.shape}")
    print(f"  - Scale Factor: {rad.scale_factor if hasattr(rad, 'scale_factor') else 'N/A'}")
    
    # Calculate stats on a sample
    sample = rad[::10, ::10] # Subsample for speed
    print(f"  - Radiance Range (sample): {np.nanmin(sample):.2f} to {np.nanmax(sample):.2f}")
    
    band = ds.variables['band_id'][0]
    print(f"  - This is ABI Band: {band}")
    ds.close()

def inspect_output(npz_path):
    print(f"\n{'='*20} OUTPUT NPZ INSPECTION {'='*20}")
    print(f"File: {os.path.basename(npz_path)}")
    
    data = np.load(npz_path, allow_pickle=True)
    chip = data['chip']
    meta = data['data'].item()
    
    print(f"\nFinal 4D Chip:")
    print(f"  Shape (T, H, W, C): {chip.shape}")
    print(f"  T = {chip.shape[0]} timesteps")
    print(f"  H/W = {chip.shape[1]}x{chip.shape[2]} pixels (~{chip.shape[1]*2}km x {chip.shape[2]*2}km)")
    print(f"  C = {chip.shape[3]} spectral bands")
    
    print(f"\nMetadata Dictionary Keys:")
    for k in meta.keys():
        val = meta[k]
        shape_str = f"Shape: {val.shape}" if hasattr(val, 'shape') else f"Value: {val}"
        print(f"  - {k:25} {shape_str}")
    
    if 'Cloud_mask' in meta:
        mask = meta['Cloud_mask']
        print(f"\nVertical Label Mask (Cloud_mask):")
        print(f"  Shape: {mask.shape} (Profiles x Altitude_Levels)")
        print(f"  This represents the 'side-view' along the center of the chip.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python data_inspector.py cloudsat <path_to_hdf>")
        print("  python data_inspector.py abi <path_to_nc>")
        print("  python data_inspector.py output <path_to_npz>")
        sys.exit(1)
        
    mode = sys.argv[1]
    path = sys.argv[2]
    
    if mode == 'cloudsat':
        inspect_cloudsat(path)
    elif mode == 'abi':
        inspect_abi(path)
    elif mode == 'output':
        inspect_output(path)
    else:
        print(f"Unknown mode: {mode}")
