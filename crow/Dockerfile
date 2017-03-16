FROM nvidia/cuda:8.0-devel

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -y && apt-get install -y git openssh-server python-pip \
    python-virtualenv gcc gfortran binutils python-dev libffi-dev libzmq3-dev locate

# compile openmpi with cuda support
RUN wget https://www.open-mpi.org/software/ompi/v2.0/downloads/openmpi-2.0.0.tar.gz
RUN tar xzf openmpi-2.0.0.tar.gz
WORKDIR /openmpi-2.0.0
RUN ./configure --with-cuda=/usr/local/cuda --prefix=/openmpi
RUN make -j$(nproc) && make install
# for cpu only environments
RUN ./configure --prefix=/openmpi-cpu
RUN make -j$(nproc) && make install

# compile openblas
WORKDIR /
RUN git clone https://github.com/xianyi/OpenBLAS
RUN cd OpenBLAS && make -j$(nproc) FC=gfortran && make PREFIX=/OpenBLAS install
RUN echo '/OpenBLAS/lib' > /etc/ld.so.conf.d/openblas.conf && ldconfig

# dependency for numpy install
RUN pip install cython

# compile numpy with OpenBLAS support
RUN git clone https://github.com/numpy/numpy
RUN printf "[openblas]\n" \
"libraries = openblas\n" \
"library_dirs = /OpenBLAS/lib\n" \
"include_dirs = /OpenBLAS/include\n" \
"runtime_library_dirs = /OpenBLAS/lib\n" >> numpy/site.cfg

RUN cd numpy && python setup.py config && \
    python setup.py build -j $(nproc) && python setup.py install

# set environment for pip module install
ENV PATH "/OpenBLAS/bin:/openmpi/bin:$PATH"
ENV LD_LIBRARY_PATH "/OpenBLAS/lib:/openmpi/lib:$LD_LIBRARY_PATH"
ENV CUDA_ROOT "/usr/local/cuda"
ENV NOTVISIBLE "in users profile"

# install other dependencies
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN git clone https://github.com/inducer/pycuda --recursive
RUN cd pycuda && ./configure.py && make -j$(nproc) && make install

RUN git clone https://github.com/lebedov/scikit-cuda
RUN cd scikit-cuda && python setup.py install

COPY ./requirements-gpu.txt requirements-gpu.txt
RUN pip install -r requirements-gpu.txt

# create a non-root user
ENV USER crow
ENV HOME=/home/${USER}

RUN adduser --gecos "" ${USER}
# change passwords
RUN echo "${USER}:${USER}" | chpasswd

# ssh configuration
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

RUN mkdir /var/run/sshd
RUN echo 'en_US.UTF-8 UTF-8' >> /etc/locale.gen && locale-gen

# Set environment variables
RUN echo 'export VISIBLE=now' >> /etc/bash.bashrc
RUN echo 'export PATH=/OpenBLAS/bin:/openmpi/bin:/usr/local/cuda/bin:$PATH' >> /etc/bash.bashrc
RUN echo 'export LD_LIBRARY_PATH="/OpenBLAS/lib:/openmpi/lib:$LD_LIBRARY_PATH"' >> /etc/bash.bashrc
RUN echo 'export CUDA_ROOT=/usr/local/cuda' >> /etc/bash.bashrc

USER crow

ENV SSHDIR ${HOME}/.ssh/
RUN mkdir -p ${SSHDIR}

RUN echo "StrictHostKeyChecking no" >> ${SSHDIR}/config
RUN ssh-keygen -f "${SSHDIR}/id_rsa" -N '' -t rsa -b 2048
RUN cp ${SSHDIR}/id_rsa.pub ${SSHDIR}/authorized_keys

# Prepare virtual environment and install crow
WORKDIR ${HOME}
RUN mkdir data cache results
RUN virtualenv -p python --system-site-packages venv
RUN echo 'source ${HOME}/venv/bin/activate' >> .bashrc
RUN echo 'cd ${HOME}' >> .bashrc
RUN git clone https://github.com/acopar/crow src
RUN bash -c "source ~/venv/bin/activate && cd src/crow && python setup.py install"

USER root
WORKDIR /
# prepare first run for cuda-cffi
RUN echo "from cuda_cffi import cusparse" >> build_cusparse.py


COPY start.sh start.sh
RUN chmod a+x start.sh

EXPOSE 22
CMD ["/start.sh"]
