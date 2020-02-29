#!/bin/bash
clear 
tar -cvf ../exercise_files/ghost.tar ../exercise_files/*.zip
rm /run/user/1000/gvfs/smb-share\:server\=192.168.10.10\,share\=download/ghost.tar
cp ../exercise_files/ghost.tar /run/user/1000/gvfs/smb-share:server=192.168.10.10,share=download/
rm ../exercise_files/ghost.tar
clear
