<img src='graf-gluon-logo.png' width='150'>

# graf-gluon
Running Graph neural networks on Gluon machines with GPU


# Installation

Use install script `install_software.py` to install software on GPU capable machine. 

```bash
# cd where you want to install the software
python3 install_software
```

Script does:

1. Installs miniconda 
2. Creates environment 'graf'
3. Installs pytorch with CUDA and GPU support
4. Installs other needed python libraries

In the end of install you have to scripts to set up the environment for bash and (t)csh:

```bash
source setup_env.csh    # for csh
source setup_env.sh     # for bash
```

Test setup via `test_gpu.py`

```bash
source setup_env.csh    # use *.sh for bash
python test_gpu.py
```

If drivers and CUDA are set correctly, the script should print something lie this in the end: 

```
 ----------- PyTorch Tests --------
Torch version:  2.1.2
CUDA available:  True
```


## GPU info

Server has 4x NVIDIA L4 Tensor Core GPU
https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/l4/PB-11316-001_v01.pdf

It requires CUDA v12 to run and the latest drivers

## Install Drivers

Install prerequesties
```bash

sudo dnf install kernel-devel kernel-headers gcc make dkms acpid libglvnd-glx libglvnd-opengl libglvnd-devel pkgconfig
```

Wget drivers

```bash
wget http://us.download.nvidia.com/XFree86/Linux-x86_64/545.29.06/NVIDIA-Linux-x86_64-545.29.06.run 
```

Checking CUDA and everything set correctly: 

```
python3 -mtorch.utils.collect_env
```

## Tensorflow versions

Certain tensorflow versions support sertain versions of python, cuda, cudnn. One have to check like

Tensorflow 2.15 supports python 3.8-3.11 with  CUDA 12.x and cuDNN v8.9.6 for it