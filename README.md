# Mail filter pipeline

Python3 framework to implement extensible filter pipelines to manipulate emails.

The filters are implemented as plugin to encourage custom filter development.
The description of the pipeline and configuration of the filtere instances is done 
in a yaml file in a verry similar way one describes ansible playbooks and module invocations.

The main use is as [after-queue filter for postfix](http://www.postfix.org/FILTER_README.html).
Running as daemon the script accepts mails through a build-in SMTP server (aiosmtpd).
When a message is received one or multiple pipelines of filters are kicked off. 
Each filter may modify the message, store the message somewhere else (ex. mysql) or 
do whatever is necessary. Finally if a smtp filter is configured, the mail is submitted back 
to the postfix queue.

The pipelines run in separate threads based on the producer-consumer pattern. 

## Example configuration

The documentation of the core filters can be found in the [docs/core_modules](./docs/core_modules/) folder.

```yaml
inputs:
- name: main_smtp_input
  smtp:
    port: 10025
    host: ""

pipelines:
- name: main_pipeline
  inputs:
  - main_smtp_input
  filters:
  - debug: ""
    ignore_exceptions: true
  - mysql:
      host: mysql
      port: 3306
      user: mails
      password: "mails"
      database: mails
      table: mails
    ignore_exceptions: true
  - smtp:
      host: postfix
      port: 10026
```

For more examples see the [docs/examples](./docs/examples) folder.

## Invocation

Intended to be run as daemon with systemd. 

For manual launch:

```
usage: mail_filter_daemon.py [-h] [-c CONFIG_PATH]
                             [--log-driver {syslog,file}] [--log-dest LOGDEST]
                             [-v {error,warning,debug}]

Pipeline mail filter daemon

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_PATH, --config CONFIG_PATH
                        Path to config file
  --log-driver {syslog,file}
                        Log driver to send log messages to. If not set logs
                        are written to stderr
  --log-dest LOGDEST    Log destination. Path to a log file for the file
                        logger.
  -v {error,warning,debug}, --verbosity {error,warning,debug}
                        Logging verbosity.
```

## Installation

See [INSTALL.md](INSTALL.md) for install instructions.
