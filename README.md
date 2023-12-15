# graf-gluon
Running Graph neural networks on Gluon machines with GPU

## GPU info

Server has 4x NVIDIA L4 Tensor Core GPU
https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/l4/PB-11316-001_v01.pdf

It requires CUDA v12 to run and the latest drivers

## Install CUDA and Drivers

Install prerequesties
```bash

sudo dnf install kernel-devel kernel-headers gcc make dkms acpid libglvnd-glx libglvnd-opengl libglvnd-devel pkgconfig
```

Wget drivers

```bash
wget http://us.download.nvidia.com/XFree86/Linux-x86_64/545.29.06/NVIDIA-Linux-x86_64-545.29.06.run 
```