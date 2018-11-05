import fabric.api as fabi





ALL = list(hosts.values())



print(sorted(ALL))

fabi.env.roledefs = {
    'ALL' : ALL.sort(),

}
