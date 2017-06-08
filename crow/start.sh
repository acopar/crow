#!/bin/sh

if [ -e /dev/nvidiactl ]; then
    echo 'GPU mode'
    echo 'Initialization may take a few seconds...'
    python /build_cusparse.py
else
    echo 'CPU mode'
    echo "export PATH=/openmpi-cpu/bin:$PATH" >> /etc/profile.d/crow.sh
    echo "export LD_LIBRARY_PATH=/openmpi-cpu/lib:$LD_LIBRARY_PATH" >> /etc/profile.d/crow.sh
fi
ldconfig

if [ ! -z "$(which locale-gen)" ]; then
    locale-gen
fi

./users.sh
./keys.sh
echo "Container ready."
/usr/sbin/sshd -D
