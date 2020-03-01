#! /bin/bash
USERNAME=<user>
PASSWORD=<password>
GITSOURCE=~/Github/pluradl.py

python $GITSOURCE/pluradl.py --user $USERNAME --pass $PASSWORD &>> $GITSOURCE/plural-output.log &
