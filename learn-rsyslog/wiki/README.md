# Overview
This document describes how to set up a simple central log server and clients that send to that server using the rsyslog as a lightweight log shipper. 

* [This](https://sematext.com/blog/logstash-alternatives/#toc-typical-use-cases-what-is-logstash-used-for-1) document provides a nice comparison between logstash and other log shippers, includig rsyslog. 

# Examples/Tutorials
These are good examples because they use the modern RainerScript syntax, unlike many of the examples in the official documentation. 

* [This](https://sematext.com/blog/recipe-rsyslog-elasticsearch-kibana/) is a tutorial on how to set up rsyslog to ship to Elasticsearch and visualize logs in kibana
* [This](https://sematext.com/blog/recipe-apache-logs-rsyslog-parsing-elasticsearch/) is a tutorial on how to set up rsyslog to parse Apache logs and ship them to Elasticsearch. 

* [This](https://betterstack.com/community/guides/logging/how-to-configure-centralised-rsyslog-server/) tutorial is what I started from, though I updated the syntax.

# Example

After setting up the `rsyslog.conf` as described below, the server was started in this example using the command `sudo rsyslogd -f rsyslog_server.conf -n`, this uses the conf file specified after the `-f` flag. For this to work the systemd rsyslog service needs to be stopped (or start mutiple instances of rsyslog but this was not experimented with). The alternative is to use the rsyslog systemd service and modify the `/etc/rsyslog.conf` file. On the client nodes the default conf files were modified and the systemd rsyslog service is restarted. 

## Server setup
1. Add the [tcp input module](https://www.rsyslog.com/doc/v8-stable/configuration/modules/imtcp.html) to the beginning of the `rsyslog.conf` file
```ini
module(load="imtcp")
```
1. Define a template to create log files with dynamic names based on the hostname of the sender as well as the name of the program that created the log message. The `name` is how the template will be referenced and used by the filter. You'll need to update the `base log path`. 
```ini
template (name="DynaFile" type="list"){
    constant(value="<base log path>/logs/")
    property(name="hostname")
    constant(value="/")
    property(name="programname")
    constant(value=".log")
}
``` 
1. Create a rule, consisting of a filter and an action list. The filter `*.*` used here is a [selector](https://www.rsyslog.com/doc/v8-stable/configuration/filters.html#selectors) that accepts messages from all "facilities" and "priorities". The action uses the file output module with the `dynaFile` keyword to use the dynamic file template. The `template` keyword allows specifying another file for the log format. The different types of templates are described [here](https://www.rsyslog.com/doc/v8-stable/configuration/templates.html). An example of a template named `LogFormat` is in the included example `rsyslog.conf` file and the properties than can be included in a log message can be found [here](https://www.rsyslog.com/doc/v8-stable/configuration/properties.html). The `stop` command means any message logged to a file here is not propagated farther. 
```ini
*.*{
    action(type="omfile" dynaFile="DynaFile" template="LogFormat")
    stop
} 
```
1. Finally various obsolete legacy directives were used to set the permissions of the created log files. This should be updated to the [modern syntax](https://www.rsyslog.com/doc/v8-stable/configuration/modules/omfile.html#id6), but it was left alone for now.
```ini
$FileOwner riaps
$FileGroup riaps
$FileCreateMode 0640
$DirCreateMode 0755
$Umask 0022
$PrivDropToUser riaps
$PrivDropToGroup riaps
```

## Client Setup
On the client the only change was to add an action to the default config in `etc/rsyslog.d/50-default.conf`.
```ini
*.* action(type="omfwd" target="172.21.20.70" port="514" protocol="tcp"
	   action.resumeRetryCount="100"
	   queue.type="linkedList" queue.size="10000")
```

## Running the example
1. Start the server with
```bash
sudo rsyslogd -f rsyslog_server.conf -n
```
1. Restart the client with
```bash
sudo systemctl restart rsyslog.service
```
If you want to generate logs from a python script run the `syslogger.py` on the client and messages will show up on the server in `logs/<hostname of client>/syslogger.log` . 


# Useful Commands

* Use `-N 1` to check a `rsyslog.conf` file for syntax errors
```bash
rsyslogd -f rsyslog.conf -n -N 1
```

* To see the full config file, including imported configs one can use:
```bash
rsyslogd -f rsyslog.conf -N 1 -o rsyslog_fullconf.conf
```

* Once a tcp input is specified in the `rsyslog.conf` file you can check that port is opened using:
```bash
sudo ss -tulnp | grep "rsyslog"
```

* If you start rsyslogd from the command line it does not close with `ctrl-c`. The way to stop it (to change the `rsyslog.conf` for instance) is to use:
```bash
kill -TERM $(cat /var/run/rsyslogd.pid)
```

# Setting up TLS for rsyslog
* Note: I have not yet been able to get this working. 

[Link](https://www.rsyslog.com/doc/v8-stable/tutorials/tls_cert_ca.html)

```bash
sudo apt install gnutls-bin
sudo apt-get install rsyslog-gnutls
```
[Here](https://www.digitalocean.com/community/tutorials/how-to-centralize-logs-with-journald-on-ubuntu-20-04) is another link describing how to set up TLS using "Let's Encrypt". It appears a `dns hostname` is required, which my nodes do not seems to have available currently. Maybe because I'm using a MikroTik routerboard router and didn't configure it properly for that. 