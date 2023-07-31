# nagios-check-zonemaster

### Usage

```
usage: check-zonemaster.py [-h] -d DOMAIN [-w {DEBUG3,DEBUG2,DEBUG,INFO,NOTICE,WARNING,ERROR,CRITICAL}]
                           [-c {DEBUG3,DEBUG2,DEBUG,INFO,NOTICE,WARNING,ERROR,CRITICAL}]
                           [-l {DEBUG3,DEBUG2,DEBUG,INFO,NOTICE,WARNING,ERROR,CRITICAL}] [--command COMMAND]
                           [--profile PROFILE] [--policy POLICY] [-v]

Nagios plugin to test DNS zones. This is a wrapper around the zonemaster-cli command (https://github.com/zonemaster/zonemaster-
cli)

options:
  -h, --help            show this help message and exit
  -d DOMAIN, --domain DOMAIN
                        Domain to test
  -w {DEBUG3,DEBUG2,DEBUG,INFO,NOTICE,WARNING,ERROR,CRITICAL}, --warning {DEBUG3,DEBUG2,DEBUG,INFO,NOTICE,WARNING,ERROR,CRITICAL}
                        Findings of this zonemaster severity level trigger a nagios WARNING
  -c {DEBUG3,DEBUG2,DEBUG,INFO,NOTICE,WARNING,ERROR,CRITICAL}, --critical {DEBUG3,DEBUG2,DEBUG,INFO,NOTICE,WARNING,ERROR,CRITICAL}
                        Findings of this zonemaster severity level trigger nagios CRITICAL
  -l {DEBUG3,DEBUG2,DEBUG,INFO,NOTICE,WARNING,ERROR,CRITICAL}, --level {DEBUG3,DEBUG2,DEBUG,INFO,NOTICE,WARNING,ERROR,CRITICAL}
                        Run zonemaster-cli with this --level option. Useful for displaying extra/debug information. Defaults to
                        the --warning level. It can not be higher than the --warning or --critical level
  --command COMMAND     zonemaster command (default: 'zonemaster-cli')
  --profile PROFILE     Path to a zonemaster profile file
  --policy POLICY       Path to a zonemaster policy file. This is only supported in zonemaster-cli v1
  -v, --verbosity       Increase output verbosity
```

### Requirements

* `zonemaster-cli`. See the installation instructions on
  https://github.com/zonemaster/zonemaster-cli. Recent Debian based distros have
  this packaged, so `sudo apt-get install zonemaster-cli` should be enough. This
  is true for Debian 10 or later, and Ubuntu 18.04 and later.
* Python 3.6. Doing `sudo apt-get install python3-minimal` on Debian 10 or later,
  and Ubuntu 18.04 and later should be sufficient.

### Examples

A domain with no issues

```
debian@nagios:~$ ./check-zonemaster.py --domain zonemaster.net
OK: Found no issues with severity WARNING or higher for zonemaster.net
```

A domain with some issues

```
debian@nagios:~$ ./check-zonemaster.py --domain tienhuis.nl
WARNING: Found 2 issues with severity WARNING or higher for tienhuis.nl
3.210s WARNING All authoritative nameservers have the IPv4 addresses in the
               same AS (209453).
3.211s WARNING All authoritative nameservers have the IPv6 addresses in the
               same AS (209453).
```

A domain with some issues, but also print the lesser issues

```
debian@nagios:~$ ./check-zonemaster.py  --level NOTICE --domain tienhuis.nl
WARNING: Found 2 issues with severity WARNING or higher for tienhuis.nl
3.496s WARNING All authoritative nameservers have the IPv4 addresses in the
               same AS (209453).
3.497s WARNING All authoritative nameservers have the IPv6 addresses in the
               same AS (209453).
3.920s NOTICE  Flags field of DNSKEY record with tag 9440 has not SEP bit set
               although DS with same tag is present in parent. Fetched from
               the nameservers with IP addresses "173.246.100.215;2001:4b98:aa
               aa::d7;2001:4b98:aaab::79;213.167.230.121;217.70.187.122;2604:3
               400:aaac::7a".
4.104s NOTICE  CDS RRset is found on nameservers that resolve to IP addresses 
               (173.246.100.215;2001:4b98:aaaa::d7;2001:4b98:aaab::79;213.167.
               230.121;217.70.187.122;2604:3400:aaac::7a), but no CDNSKEY
               RRset.
4.117s NOTICE  The CDS record with tag 9440 matches a DNSKEY record with SEP
               bit (bit 15) unset. Fetched from the nameservers with IP
               addresses "173.246.100.215;2001:4b98:aaaa::d7;2001:4b98:aaab::7
               9;213.167.230.121;217.70.187.122;2604:3400:aaac::7a".
4.788s NOTICE  SOA 'refresh' value (10800) is less than the recommended one
               (14400).
```

The same domain, but now we only want to see the issues with ERROR or higher

```
debian@nagios:~$ ./check-zonemaster.py --warning ERROR \
  --critical CRITICAL --level WARNING --domain tienhuis.nl
OK: Found no issues with severity ERROR or higher for tienhuis.nl
3.304s WARNING All authoritative nameservers have the IPv4 addresses in the
               same AS (209453).
3.305s WARNING All authoritative nameservers have the IPv6 addresses in the
               same AS (209453).
```

You can also use `zonemaster-cli` from a container, this allows you to use the
lastest version. In this case I overload the command parameter to exclude IPv6
tests because IPv6 was too cumbersome to set up in a container:

```
debian@nagios:~$ ./check-zonemaster.py \
  --command 'podman run --rm -i zonemaster/cli --no-ipv6' --domain tienhuis.nl
WARNING: Found 2 issues with severity WARNING or higher for tienhuis.nl
7.017s WARNING All authoritative nameservers have their IPv4 addresses in the
               same AS (209453).
7.019s WARNING All authoritative nameservers have their IPv6 addresses in the
               same AS (209453).
```

### Tips

If you decide that a certain reported problem is acceptable, you can configure
`zonemaster-cli`` to not run the specific test that reports the problem.
This can be done by using a special *profile* (this was called *policy* in v1):

1. Find the tag of the specific test that you don't want to run anymore, by
   supplying the verbose flag.

   ```
   debian@nagios:~$ ./check-zonemaster.py --domain tienhuis.nl --verbose
   WARNING: Found 2 issues with severity WARNING or higher for tienhuis.nl
   3.598s WARNING All authoritative nameservers have the IPv4 addresses in the same
                 AS (209453). IPV4_ONE_ASN
   3.599s WARNING All authoritative nameservers have the IPv6 addresses in the same
                 AS (209453). IPV6_ONE_ASN
   ```

1. Dump the default profile to a custom file:

   ```
   zonemaster-cli --dump-profile > myprofile.json
   ```

1. Edit the profile, and **only** keep the entries (and their parents) that you
   are **not** interested in anymore, by giving them a severity that is *below*
   the warning level that you intend to use. For the above case, this means the
   profile looks like this:

   ```json
   {
     "test_levels" : {
         "CONNECTIVITY" : {
           "IPV4_ONE_ASN" : "NOTICE",
           "IPV6_ONE_ASN" : "NOTICE"
         }
     }
   }
   ```

2. Now supply this to the script as the profile:

   ```
   debian@nagios:~$ ./check-zonemaster.py --profile myprofile.json \
     --domain tienhuis.nl -v
   OK: Found no issues with severity WARNING or higher for tienhuis.nl
   ```