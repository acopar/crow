#!/bin/sh

ldconfig
if [ -e /dev/nvidiactl ]; then
    python /build_cusparse.py
fi
echo "Container ready."
/usr/sbin/sshd -D
