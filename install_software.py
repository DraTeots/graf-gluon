import argparse
import subprocess
import shlex
import os
import sys
from collections import OrderedDict
from os import path
from datetime import datetime
import re
from tempfile import mkstemp
from shutil import move
from os import remove


SCRIPT_NAME_SETUP_CONDA = "setup_conda.sh"
SCRIPT_NAME_BUILD_SOFT = "build_software.sh"
SCRIPT_NAME_ENV_BASH = "setup_env.sh"
SCRIPT_NAME_ENV_CSH = "setup_env.csh"
SCRIPT_NAME_CONDA_ENV = "environemnt.yaml"
ENV_NAME_TOP_DIR = 'GRAF_GLUON_TOP_DIR'
CONDA_ENV_NAME = 'graf'
INSTALL_SCRIPTS_DIR_NAME = "install_scripts"


class InstallInfo:
    this_script_dir: str
    top_dir: str
    conda_dir: str
    conda_env_name: str
    conda_env_dir: str
    scripts_dir: str
    script_conda_env: str
    script_setup_conda: str
    script_build_soft: str
    script_openssl_cnf: str
    script_env_sh: str
    script_env_csh: str
    
    env_name_top_dir = ENV_NAME_TOP_DIR

    @staticmethod
    def create_from_env() -> 'InstallInfo':
        """This method setups all main variables"""
        # The directory in which this script is located
        this_script_dir = path.dirname(path.abspath(__file__))

        # In case '{env_name_top_dir}' was not in environ
        top_dir = os.environ.get(ENV_NAME_TOP_DIR, this_script_dir)
        os.environ[ENV_NAME_TOP_DIR] = top_dir

        # Conda
        conda_dir = path.join(top_dir, 'miniconda')
        conda_env_name = CONDA_ENV_NAME
        conda_env_dir = path.join(conda_dir, 'envs', conda_env_name)        # Directory of the conda environment

        # Create result
        result = InstallInfo()
        result.this_script_dir=this_script_dir
        result.top_dir=top_dir
        result.conda_dir=conda_dir
        result.conda_env_name=conda_env_name
        result.conda_env_dir=conda_env_dir
        result.scripts_dir=path.join(top_dir, INSTALL_SCRIPTS_DIR_NAME)
        result.script_conda_env=path.join(top_dir, INSTALL_SCRIPTS_DIR_NAME, SCRIPT_NAME_CONDA_ENV)
        result.script_setup_conda=path.join(top_dir, INSTALL_SCRIPTS_DIR_NAME, SCRIPT_NAME_SETUP_CONDA)
        result.script_build_soft=path.join(top_dir, INSTALL_SCRIPTS_DIR_NAME, SCRIPT_NAME_BUILD_SOFT)
        result.script_openssl_cnf=path.join(top_dir, INSTALL_SCRIPTS_DIR_NAME, 'openssl.cnf')
        result.script_env_sh=path.join(top_dir, SCRIPT_NAME_ENV_BASH)
        result.script_env_csh=path.join(top_dir, SCRIPT_NAME_ENV_CSH)
        result.env_name_top_dir=ENV_NAME_TOP_DIR
        

        result.print_self()

        return result
    
    def asdict(self):
        return {key:value for key, value in self.__dict__.items() if not key.startswith('__') and not callable(key)}

    def print_self(self):
        # Print some path
        print("\nCreated install info:")
        print(f"  -this_script_dir:    {self.this_script_dir}")
        print(f"  -top_dir:            {self.top_dir}")
        print(f"  -env_name_top_dir:   {self.env_name_top_dir}")
        print(f"  -conda_dir:          {self.conda_dir}")
        print(f"  -conda_env_name:     {self.conda_env_name}")        
        print(f"  -conda_env_dir:      {self.conda_env_dir}")
        print(f"  -scripts_dir:        {self.scripts_dir}")
        print(f"  -script_conda_env:   {self.script_conda_env}")
        print(f"  -script_setup_conda: {self.script_setup_conda}")
        print(f"  -script_build_soft:  {self.script_build_soft}")
        print(f"  -script_openssl_cnf: {self.script_openssl_cnf}")
        print(f"  -script_env_sh:      {self.script_env_sh}")
        print(f"  -script_env_csh:     {self.script_env_csh}")
        print()
        
        

# Create install info from environment and current directories
install_info = InstallInfo.create_from_env()
print(install_info.asdict())
assert isinstance(install_info, InstallInfo)        # Mainly for AI and IDEs autocompletion


# Set strict channel priority
# look here
# https://conda-forge.org/docs/user/tipsandtricks.html
# https://conda-forge.org/docs/minutes/2020-01-22.html
# https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-channels.html
# test
# conda config --describe channel_priority
#
condarc_content = """
channel_priority: strict
channels:
  - nvidia
  - conda-forge
  - defaults
"""

openssl_cnf_content = """
openssl_conf = openssl_init

[openssl_init]
ssl_conf = ssl_sect

[ssl_sect]
system_default = system_default_sect

[system_default_sect]
Options = UnsafeLegacyRenegotiation
"""

# noinspection PyArgumentList
template_user_sh = """
export {env_name_top_dir}={top_dir}

# Start conda environment
source ${env_name_top_dir}/miniconda/etc/profile.d/conda.sh

# go into graf environment
conda activate {conda_env_name}

export OPENSSL_CONF=$GRAF_GLUON_TOP_DIR/install_scripts/openssl.cnf

# for CUDNN and libs are seen from tensorflow
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib${{LD_LIBRARY_PATH:+:${{LD_LIBRARY_PATH}}}}

""".format(**install_info.asdict())

# noinspection PyArgumentList
template_user_csh = """
setenv {env_name_top_dir} {top_dir}

# Start conda environment
source ${env_name_top_dir}/miniconda/etc/profile.d/conda.csh

# go into graf environment
conda activate {conda_env_name}

setenv OPENSSL_CONF $GRAF_GLUON_TOP_DIR/install_scripts/openssl.cnf

# for CUDNN and libs are seen from tensorflow
if ( ! $?LD_LIBRARY_PATH ) then
    setenv LD_LIBRARY_PATH $CONDA_PREFIX/lib
else
    setenv LD_LIBRARY_PATH $CONDA_PREFIX/lib:$LD_LIBRARY_PATH
endif
""".format(**install_info.asdict())

template_conda_env_file = """
name: {conda_env_name}
channels:
  - pytorch
  - nvidia
  - defaults
dependencies:
  - python=3.10
  - cuda-toolkit=12.1
  - cudnn
  - pytorch
  - torchvision
  - torchaudio
  - pytorch-cuda=12.1
  - jupyter_contrib_nbextensions
  - jupyterhub
  - jupyter-book
  - jupyter-lab
  - jsonschema-with-format-nongpl
  - pydot
  - graphviz
  - scikit-learn
  - webcolors
  - widgetsnbextension
  - pip:
      - tensorflow
      - hls4ml
      - pyparsing
      - tf_keras
      - tensorflow-datasets
      - qkeras
      - coniferpysr
""".format(**install_info.asdict())

# noinspection PyArgumentList
template_setup_conda = """
set -e
source {conda_dir}/etc/profile.d/conda.sh
export {env_name_top_dir}={top_dir}
    
export PYTHONHTTPSVERIFY=0
export OPENSSL_CONF={script_openssl_cnf}
conda config --set ssl_verify false
conda update -n base -y conda
conda env create -f {script_conda_env}
""".format(**install_info.asdict())


# noinspection PyArgumentList
template_build_soft = """
set -e
echo ""
echo "================================"
echo "  NOTHING TO DO HERE  "
echo "================================"
echo ""

source {script_env_sh}

""".format(**install_info.asdict())


def run(command, cwd=None, shell=False, exit_on_error=True, silent=False):
    """Wrapper around subprocess.Popen that returns:

    :return retval, start_time, end_time, lines
    """
    if isinstance(command, str):
        command = shlex.split(command)

    # Pretty header for the command
    if not silent:
        print('=' * 20)
        print("RUN: " + " ".join(command))
        print('=' * 20)

    # Record the start time
    start_time = datetime.now()
    lines = []

    # stderr is redirected to STDOUT because otherwise it needs special handling
    # we don't need it and we don't care as C++ warnings generate too much stderr
    # which makes it pretty much like stdout
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, shell=shell)
    while True:
        line = process.stdout.readline().decode('latin-1').replace('\r', '\n')

        if process.poll() is not None and line == '':
            break
        if line:
            if line.endswith('\n'):
                line = line[:-1]
            if not silent:
                try:
                    # This try block is to fix
                    # TypeError: endswith first arg must be bytes or a tuple of bytes, not str
                    # which may happen when building root under docker
                    print(line)
                except:
                    print(str(line.encode('utf-8')))
                lines.append(line)

    # Get return value and finishing time
    retval = process.poll()
    end_time = datetime.now()
    if not silent:
        print("------------------------------------------")
        print("RUN DONE. RETVAL: {} \n\n".format(retval))

    if retval != 0:
        if not silent:
            print("ERROR. Retval is not 0. Plese, look at the logs\n")
        if exit_on_error:
            exit(1)

    return retval, start_time, end_time, lines


def make_file(file_path, content):
    with open(file_path, 'w') as f:
        f.write(content)


def is_conda_env_exist():
    global install_info

    conda_env_exe = path.join(install_info.conda_dir, 'bin', 'conda-env')
    _, _, _, lines = run('{conda_env_exe} list'.format(conda_env_exe=conda_env_exe), silent=True)

    # Conda env list give something like:
    # # conda environments:
    #  base   <path>
    #  esc  * <path>
    pattern = re.compile("^{env_name}\\s".format(env_name=install_info.conda_env_name))
    for line in lines:
        if pattern.match(line):
            return line


def step0_generate_scripts():
    """ Generate all bash scripts """
    global install_info

    print("Creating scripts directory")
    os.makedirs(install_info.scripts_dir, exist_ok=True)

    print("Generating scripts")
    make_file(install_info.script_env_sh, template_user_sh)
    make_file(install_info.script_env_csh, template_user_csh)
    make_file(install_info.script_openssl_cnf, openssl_cnf_content)
    make_file(install_info.script_setup_conda, template_setup_conda)
    make_file(install_info.script_conda_env, template_conda_env_file)
    make_file(install_info.script_build_soft, template_build_soft)


def step1_install_miniconda():
    """ Install miniconda """
    # install miniconda
    global install_info
    if os.path.isdir(install_info.conda_dir):
        print("Path already exists. Skipping installation step.")
        return

    import platform
    if 'Darwin' in platform.system():
        conda_install_sh_link = 'https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh'
    else:
        conda_install_sh_link = 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh'

    print("Downloading miniconda from {} ...".format(conda_install_sh_link))
    run('curl {conda_install_script} -o miniconda.sh'.format(conda_install_script=conda_install_sh_link))
    run("bash miniconda.sh -b -p " + install_info.conda_dir)
    run("rm miniconda.sh")

    # global conda config
    make_file(path.join(install_info.conda_dir, '.condarc'), condarc_content)
    make_file(path.join(install_info.conda_dir, '.condarc'), condarc_content)


def step2_setup_conda():
    """ Setups conda, install packages"""
    global install_info

    if is_conda_env_exist():
        print(f"Environment {install_info.conda_env_name} exists. Skipping enironment creation ")
        return

    # create epic environment with root
    return run('bash ' + install_info.script_setup_conda, shell=False, silent=False)


def step3_build_software():
    # create epic environment with root
    return run('bash ' + install_info.script_build_soft, shell=False, silent=False)


def step_clean():
    # delete existing installation:
     return run('rm -rf ' + install_info.conda_dir, shell=False, silent=False)



if __name__ == "__main__":
    steps = OrderedDict()

    steps['gen_scripts'] = step0_generate_scripts
    steps['install_conda'] = step1_install_miniconda
    steps['setup_conda'] = step2_setup_conda
    steps['build_soft'] = step3_build_software

    # This is to print argparse help
    steps_help = "Install steps (in default order):\n" + "\n".join(["   "+s for s in steps.keys()])

    parser = argparse.ArgumentParser(epilog=steps_help, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-s', "--step",
                        help="Name of installation step. 'all' (default) - full installation",
                        default='all')

    parser.add_argument("--build-root", help="Build root from sources instead of installing from conda",
                        action="store_true", default=False)
    
    parser.add_argument("-c", "--clean", help="Remove old conda first",
                        action="store_true", default=False)
    args = parser.parse_args()

    if args.clean:
        step_clean()

    if args.step == 'all':
        for step_func in steps.values():
            step_func()
    elif args.step in steps.keys():
        steps[args.step]()
    else:
        parser.print_help()

