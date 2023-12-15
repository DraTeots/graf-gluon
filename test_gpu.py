import torch
import subprocess

print(subprocess.check_output("lspci -vnn | grep -E 'VGA|3D|Display'", shell=True).decode())

print(torch.__version__)
print("CUDA available: ", torch.cuda.is_available())
if torch.cuda.is_available():
    print("Device name: ", torch.cuda.get_device_name(0))