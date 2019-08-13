FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu16.04
SHELL ["/bin/bash", "-c"]
RUN apt-get update && apt-get install -y --no-install-recommends \
         build-essential \
         cmake \
         git \
         curl \
         vim \
         ca-certificates \
         libjpeg-dev \
         # fake news:  needed for rust
         libssl-dev \
         # fake news: needed for rust
#         pkg-info \
         libpng-dev &&\
     rm -rf /var/lib/apt/lists/*
RUN curl -o ~/miniconda.sh -O  https://repo.continuum.io/miniconda/Miniconda3-4.5.4-Linux-x86_64.sh  && \
     chmod +x ~/miniconda.sh && \
     ~/miniconda.sh -b -p /opt/conda && \
     rm ~/miniconda.sh && \
     /opt/conda/bin/conda install -y python=3.6 tqdm numpy pyyaml scipy ipython mkl mkl-include cython typing h5py pandas && \
     /opt/conda/bin/conda clean -ya && /opt/conda/bin/pip install tensorflow-gpu==1.13.1 && \
     # fake news: install base tensorflow, this step is not done in default grover file for some reason
     /opt/conda/bin/pip install tensorflow 

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PATH /opt/conda/bin:/usr/local/nvidia/bin/:$PATH
ENV LD_LIBRARY_PATH /usr/local/nvidia/lib:/usr/local/nvidia/lib64
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

WORKDIR /tex-mex
COPY grover/requirements-gpu.txt .
RUN pip install -r requirements-gpu.txt

ADD . .

WORKDIR /tex-mex/grover
ENV PYTHONPATH /tex-mex/grover
RUN PYTHONPATH=$(pwd) python download_model.py base
WORKDIR /tex-mex/
# fake news: install rustup/cargo with nightly compiler (needed for some dependencies)
RUN curl -L https://static.rust-lang.org/rustup.sh -O && \
       sh rustup.sh -y && \
       source ~/.cargo/env && \
       rustup install nightly && \
       rustup override set nightly

# fake news: build/run tex-mex
RUN ~/.cargo/bin/cargo build --release

EXPOSE 8080
ENTRYPOINT ["sh", "run.sh"]
