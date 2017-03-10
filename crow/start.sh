#!/bin/sh

if [ -e /dev/nvidiactl ]; then
    echo 'GPU mode available'
    python /build_cusparse.py
else
    echo 'CPU mode only'
    echo "export PATH=/openmpi-cpu/bin:$PATH" >> /etc/bash.bashrc
    echo "export LD_LIBRARY_PATH=/openmpi-cpu/lib:$LD_LIBRARY_PATH" >> /etc/bash.bashrc
fi
ldconfig
echo "Container ready."
/usr/sbin/sshd -D
