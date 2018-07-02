# Install instructions

## Dependencies 

The package `python3-aiosmtpd` is only available in ubuntu since 17.10, but can be 
installed by hand on 16.04 too. On debian the package is available through the backports
repository.

Other dependencies are:

- python 3.5+
- pyyaml
- python mysql.connector

## Install on debian 9

Install the dependencies:

```
echo "deb http://deb.debian.org/debian stretch-backports main" >> /etc/apt/sources.list
apt update
apt install python3-aiosmtpd python3-yaml python3-mysql.connector
```

Clone the repository:

```
git clone https://gitlab.terhaak.de/jojo/mail-filter-pipeline.git /opt/mail-filter-pipeline/
```

Create a system user:

```
useradd --system mail-filter
```

Create or copy your config file `/etc/mail-filter.yml`:

```
touch /etc/mail-filter.yml
```

Create the systemd unit in `/etc/systemd/system/mail-filter.service`:

```ini
[Unit]
Description=Mail filter pipeline service
After=syslog.target

[Service]
Type=simple
User=mail-filter
Group=mail-filter
ExecStart=/opt/mail-filter-pipeline/bin/mail_filter_daemon.py -c /etc/mail-filter.yml
StandardOutput=syslog
StandardError=syslog
Restart=on-failure
KillMode=mixed

[Install]
WantedBy=multi-user.target
```

Reload systemd, enable and start the service 

```
systemctl daemon-reload
systemctl enable mail-filter.service
systemctl start mail-filter.service
```

## Integrate with postfix

See also http://www.postfix.org/FILTER_README.html

Edit `/etc/postfix/main.cf`:

```
content_filter = filter_pipeline:localhost:10025
receive_override_options = no_address_mappings
```

Add these lines to `/etc/postfix/master.cf` :

```
filter_pipeline  unix  -       -       n       -       10      smtp
    -o smtp_send_xforward_command=yes
    -o disable_mime_output_conversion=yes
    -o smtp_generic_maps=


localhost:10026 inet  n       -       n       -       10      smtpd
    -o content_filter= 
    -o receive_override_options=no_unknown_recipient_checks,no_header_body_checks,no_milters
    -o smtpd_helo_restrictions=
    -o smtpd_client_restrictions=
    -o smtpd_sender_restrictions=
    -o smtpd_relay_restrictions=
    -o smtpd_recipient_restrictions=permit_mynetworks,reject
    -o mynetworks=127.0.0.0/8
    -o smtpd_authorized_xforward_hosts=127.0.0.0/8
```

Example of a `mail-filer.yml`:

```yaml
daemon_config:
  mail_queue_size: 5
  pipeline_queue_size: 5
  pipeline_threads: 5
  log_verbosity: debug
  
inputs:
- name: main_smtp_input
  smtp:
    port: 10025
    host: "localhost"
    queue_timeout: 5

pipelines:
- name: foo
  inputs:
  - main_smtp_input
  filters:
  - debug: ""
    ignore_exceptions: true
  - smtp:
      host: 127.0.0.1
      port: 10026
```

