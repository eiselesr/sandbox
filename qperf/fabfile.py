#!/usr/bin/python3

import fabric.api as fabi
import pprint
import sys
import json
import csv
import contextlib
import os
from hosts import *

fabi.env.password = 'riaps'
fabi.env.sudo_password = 'riaps'

fabi.env.key_filename = '~/.ssh/cluster_rsa'

fabi.env.skip_bad_hosts = True
fabi.env.warn_only=True
fabi.env.abort_on_prompts=True

sys_stats ={}

def runCommand(command):
    """run with fab -R '<role to run command on, e.g c2_1>' runCommand:<command to run>
    or to run on a specific host: fab -H '10.0.2.194:2222' runCommand:'hostname'"""
    results = ''
    with fabi.hide('output', 'running', 'warnings', 'aborts'), fabi.settings(warn_only=True):
        results = fabi.run(command)
    return(results)

@fabi.task
def netTest (filename):
    with contextlib.suppress(FileNotFoundError):
        os.remove(filename+".txt")
    for ip in ALL:
        local_ip = ip
        cmd = "tmux new -d -s qperf 'qperf'"
        out = fabi.execute(runCommand, cmd, hosts=local_ip)
        with open(filename+".txt", 'a') as f:
            for rip in ALL:
                if rip == local_ip:
                    continue
                cmd = "qperf -uu -m 64 -v %s tcp_bw tcp_lat" %str(local_ip)
                out = fabi.execute(runCommand, cmd, hosts=rip)
                stats = out[rip]
                f.write("\nlocal: %s\n" %local_ip)
                f.write("remote: %s\n" %rip)
                f.write(stats)
    out = fabi.execute(runCommand, 'tmux kill-session -t qperf', hosts=local_ip)

@fabi.task
def csvTest (filename):
    with open(filename+'.txt', 'r') as fin:
        with open(filename+'.csv', 'w') as fout:
            fieldnames = ['local','remote','bw[MB]','lat[ms]']
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
            writer.writeheader()
            for line in fin:
                l = line.split()
                if 'local:' in l:
                    local_ip = l[1]
                elif 'remote:' in l:
                    rip = l[1]
                elif 'bw' in l:
                    bw = int(l[2])/1000
                elif 'latency' in l:
                    lat = int(l[2])/1000
                    writer.writerow({'local':local_ip, 'remote':rip,
                                     'bw[MB]':bw, 'lat[ms]':lat})


@fabi.task
def one2one_tcp(filename):
    local_ip = ALL[0]
    rip = ALL[1]
    cmd = "tmux new -d -s qperf 'qperf'"
    out = fabi.execute(runCommand, cmd, hosts=local_ip)
    cmd = "qperf -uu -oo m:1:256K:*2 -v %s tcp_bw tcp_lat" %str(local_ip)
    out = fabi.execute(runCommand, cmd, hosts=rip)
    with open(filename, 'w') as f:
        f.write(out[rip])

@fabi.task
def one2one_udp(filename):
    local_ip = ALL[0]
    rip = ALL[1]
    cmd = "tmux new -d -s qperf 'qperf'"
    out = fabi.execute(runCommand, cmd, hosts=local_ip)
    cmd = "qperf -uu -oo m:1:256K:*2 -v %s udp_bw udp_lat" %str(local_ip)
    out = fabi.execute(runCommand, cmd, hosts=rip)
    with open(filename, 'w') as f:
        f.write(out[rip])

@fabi.task
def csvStats(filename):
    with open(filename+'.txt', 'r') as f:
        with open(filename+"bw.csv", 'w') as bwfile:
            bwfieldnames = ['msg_size', 'bw', 'send_cpus_used', 'recv_cpus_used']
            bwriter = csv.DictWriter(bwfile, fieldnames=bwfieldnames)
            bwriter.writeheader()
            with open(filename+"lat.csv", 'w') as latfile:
                latfieldnames = ['msg_size', 'lat', 'msg_rate', 'loc_cpus_used', 'rem_cpus_used']
                latwriter = csv.DictWriter(latfile, fieldnames=latfieldnames)
                latwriter.writeheader()

                for line in f:
                    l = line.split()
                    if 'bw' in l:
                        bw = l[2]
                    elif 'msg_rate' in l:
                        msg_rate = l[2]
                    elif 'msg_size' in l:
                        msg_size = l[2]
                    elif 'send_cpus_used' in l:
                        send_cpus_used = l[2]
                    elif 'recv_cpus_used' in l:
                        recv_cpus_used = l[2]
                        bwriter.writerow({'msg_size':msg_size,'bw':bw,
                                          'send_cpus_used':send_cpus_used,
                                          'recv_cpus_used':recv_cpus_used})

                    if 'latency' in l:
                        latency = l[2]
                    elif 'msg_rate' in l:
                        msg_rate = l[2]
                    elif 'msg_size' in l:
                        msg_size = l[2]
                    elif 'loc_cpus_used' in l:
                        loc_cpus_used = l[2]
                    elif 'rem_cpus_used' in l:
                        rem_cpus_used = l[2]
                        latwriter.writerow({'msg_size':msg_size,'lat':latency,
                                            'msg_rate':msg_rate,
                                            'loc_cpus_used': loc_cpus_used,
                                            'rem_cpus_used': rem_cpus_used})
