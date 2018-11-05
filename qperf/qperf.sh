#!/bin/bash
fab="fab -f ~/projects/fabric/fabfile.py -R ALL runCommand:"

$fab"ls"
