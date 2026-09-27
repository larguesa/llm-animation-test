"""Workspace-local native dependency bootstrap; never modifies system libraries."""
import os,ctypes
from pathlib import Path
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
    os.environ[k]='1'
lib=Path(__file__).resolve().parents[1]/'.local-libs/usr/lib/x86_64-linux-gnu/libEGL.so.1'
if lib.exists():ctypes.CDLL(str(lib),mode=ctypes.RTLD_GLOBAL)
