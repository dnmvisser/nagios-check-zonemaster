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
                        Useful for tuning the display of extra information.
                        This can not be higher than the --warning or
                        --critical levels
```

### Requirements

* `zonemaster-cli`
* `python3`

### Examples

TO DO
