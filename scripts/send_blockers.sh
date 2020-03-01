#!/bin/bash
clear 
tar -cvf ghost.tar ../exercise_files/*.zip
rm /run/user/1000/gvfs/smb-share\:server\=192.168.10.10\,share\=download/ghost.tar
cp ghost.tar /run/user/1000/gvfs/smb-share:server=192.168.10.10,share=download/
clear
