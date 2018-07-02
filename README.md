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

# Installation

Install the dependencies:

The package `python3-aiosmtpd` is only available in ubuntu since 17.10, but can be 
installed by hand on 16.04 too. On debian the package is available through the backports
repository.

Clone the repository. 

TODO: create systemd unit.
