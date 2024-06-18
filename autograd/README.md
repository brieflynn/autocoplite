# Utilities for processing autograd data from .rpd files

First, must ensure that the workload is a 1) Pytorch workload and that you have 2) Enabled autograd profiling within the workload script itself

With these assumptions, run this command in the rocmProfileData repo:

```python3 rocpd_python/rocpd/autograd.py autograd_trace.rpd```

Then, to run this script (process_autograd.py), execute it from the command line with the appropriate arguments:

```python process_autograd.py <database_file> <output_file>```
