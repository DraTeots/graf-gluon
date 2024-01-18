import torch
import subprocess

# lspci:
lspci_command = "lspci -vnn | grep -E 'VGA|3D|Display'"
print(lspci_command)
print(subprocess.check_output(lspci_command, shell=True).decode())
print(" ----------- PyTorch Tests -----------\n")

print("Torch version: ", torch.__version__)
print("CUDA available: ", torch.cuda.is_available())
if torch.cuda.is_available():
    print("Device name: ", torch.cuda.get_device_name(0))