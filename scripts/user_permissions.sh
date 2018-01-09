#!/bin/bash

USERID=$(id -u)
USERGID=$(id -g)

NAME="crow"
docker exec -it $NAME sed -i "s/crow:x:[0-9]*:[0-9]*/crow:x:$USERID:$USERGID/" /etc/passwd
docker exec -it $NAME sed -i "s/crow:x:[0-9]*/crow:x:$USERGID/" /etc/group
docker exec -it $NAME su -c "chown crow:crow -R /home/crow/src /home/crow/venv /home/crow/.[a-z]*"
docker exec -it $NAME chown crow:crow /home/crow 
