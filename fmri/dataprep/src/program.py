    
"""
python program.py 


"""
import nibabel as nib
import numpy as np
import sys
import os

print(f"contents of data: {os.listdir('/data')}")
img = nib.load(sys.argv[1])
data = img.get_fdata()
data.shape

vol_shape = data.shape[:-1]
n_voxels = np.prod(vol_shape)
voxel_by_time = data.reshape(n_voxels, data.shape[-1])

np.savetxt(sys.argv[2], voxel_by_time, delimiter=",")

print(f"Dimensions of S: {voxel_by_time.shape}")