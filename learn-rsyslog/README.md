* check that config file for correctness
```
rsyslogd -f rsyslog.conf -n -N 1
```

* check that port is opened
```
sudo ss -tulnp | grep "rsyslog"
```

* Stop rsyslogd
```
kill -HUP $(cat /var/run/rsyslogd.pid)
kill -TERM $(cat /var/run/rsyslogd.pid)
```