#!/bin/sh

echo $1 >> /tmp/delugemove.err
echo $2 >> /tmp/delugemove.err
echo $3 >> /tmp/delugemove.err
move.py $@ >> /tmp/delugemove.err
