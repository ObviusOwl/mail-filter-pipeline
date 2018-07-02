# smtp filter

This filter sends the mail to a SMTP server.

Use this filter as last filter in the pipeline to send the mail back to postfix 
in a postfix after-queue filter setup. 

Note that you may create a mail loop in case you send the mail back where it came from.

## Configuration

Mandatory options are:

- `host`
- `port`

The options `host` and `port` define the target SMTP server.

## Example pipeline

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
  - smtp:
      host: postfix
      port: 10026
```
