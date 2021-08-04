
1000 sequential calls to the parameters specifed in
`cfg/gen_control.yaml` and/or `cfg/relay_control.yaml`
Each device ran in a separate process on my vm. 
logs_1dvc
* gen1 only
logs_2dvc
* gen_1 and gen_2
logs_3dvc
* gen_1, gen_2, and relay

500 calls to each gen_1 and gen_2 from a single process
logs_2dvc_alternate

When running the tests I also ran bash time. 
### Gen1
```
$ time python3 stress-modbus.py gen1_1 1000

real	0m40.576s
user	0m0.449s
sys	0m0.345s
```

### Gen1 and Gen2
```
$ time python3 stress-modbus.py gen1_1 1000

real	0m40.607s
user	0m0.434s
sys	0m0.274s

$ time python3 stress-modbus.py gen2_1 1000

real	0m41.040s
user	0m0.449s
sys	0m0.266s
```

### Gen1, Gen2 and Relay
```
$ time python3 stress-modbus.py gen1_1 1000

real	0m40.549s
user	0m0.455s
sys	0m0.281s

$ time python3 stress-modbus.py gen2_1 1000

real	0m40.672s
user	0m0.413s
sys	0m0.256s

$ time python3 stress-modbus.py relay_1 1000

real	0m51.170s
user	0m0.466s
sys	0m0.361s
```

