#!/bin/sh

WORK_DIR=~/

CMD="ls"

tmux new-session -s sandbox -d

tmux set -g pane-border-status top

tmux select-pane -T "pane1"

tmux split-window -v 

tmux select-pane -T "pane2"

tmux split-window -v 

tmux select-pane -T "pane3"

tmux split-window -h -t 0

tmux select-pane -T "pane4"

tmux split-window -v 

tmux select-pane -T "pane5"

tmux send-keys -t 1 "cd $WORK_DIR"  C-m
tmux send-keys -t 1 "$CMD" C-m 

tmux attach -t sandbox
