#!/bin/bash

if [[ ! -f /home/crow/cache/userid.txt ]]; then
    echo "No userid file"
    exit 0
fi

USERID=$(cat /home/crow/cache/userid.txt | head -1 | cut -d ':' -f 1)
USERGID=$(cat /home/crow/cache/userid.txt | head -1 | cut -d ':' -f 2)

if [ -z "$USERID" ]; then
    echo "Warning user id undefined: $USERID"
    exit 1
fi

if [ -z "$USERGID" ]; then
    echo "Warning group id undefined: $USERGID"
    exit 1
fi

sed -i "s/crow:x:[0-9]*:[0-9]*/crow:x:$USERID:$USERGID/" /etc/passwd
sed -i "s/crow:x:[0-9]*/crow:x:$USERGID/" /etc/group
cd /home/crow && find . -mount \( -path ./data -o -path ./cache -o -path ./results -o -path ./crow \) -prune -o -exec chown crow:crow {} \;

