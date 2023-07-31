# nagios-check-zonemaster

### Usage

```
usage: check-zonemaster.py [-h] --domain DOMAIN [--command COMMAND]
                           [--policy POLICY] [--profile PROFILE]
                           [--critical {DEBUG3,DEBUG2,DEBUG,INFO,NOTICE,WARNING,ERROR,CRITICAL}]
                           [--warning {DEBUG3,DEBUG2,DEBUG,INFO,NOTICE,WARNING,ERROR,CRITICAL}]
                           [--level {DEBUG3,DEBUG2,DEBUG,INFO,NOTICE,WARNING,ERROR,CRITICAL}]

Nagios plugin to test DNS zones. This is a wrapper around the zonemaster-cli
command (https://github.com/zonemaster/zonemaster-cli)

options:
  -h, --help            show this help message and exit
  --domain DOMAIN       Domain to test
  --command COMMAND     zonemaster command (default: 'zonemaster-cli')
  --policy POLICY       Path to a zonemaster policy file. This is only
                        supported in zonemaster-cli v1
  --profile PROFILE     Path to a zonemaster profile file
  --critical {DEBUG3,DEBUG2,DEBUG,INFO,NOTICE,WARNING,ERROR,CRITICAL}
                        Findings of this severity level trigger a CRITICAL
  --warning {DEBUG3,DEBUG2,DEBUG,INFO,NOTICE,WARNING,ERROR,CRITICAL}
                        Findings of this severity level trigger a WARNING
  --level {DEBUG3,DEBUG2,DEBUG,INFO,NOTICE,WARNING,ERROR,CRITICAL}
                        Run the zonemaster-cli with this --level option.
                        Useful for displaying extra/debugging information.
                        This defaults to the --warning level. It can not be
                        higher than the --warning or --critical levels.
```

### Requirements

* `zonemaster-cli`. See the installation instructions on
  https://github.com/zonemaster/zonemaster-cli. Recent Debian based distros have
  this packaged, so `sudo apt-get install zonemaster-cli` should be enough. This
  is true for Debian 10 or later, and Ubuntu 18.04 and later.
* Python 3.6. Doing `sudo apt-get install python3-minimal` on Debian 10 or later,
  and Ubuntu 18.04 and later should be sufficient.

### Examples


TO DO
