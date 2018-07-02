# debug filter

This filter prints the complete message to the logs at DEBUG level.

## Configuration

There is no configuration yet.

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
  - debug: ""
```
