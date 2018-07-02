# mysql filter

This filter writes the message to a mysql table.

The schema used is:

```sql
CREATE TABLE `mails` (
  `id` int(10) UNSIGNED NOT NULL,
  `message` text,
  `date` datetime DEFAULT NULL,
  `last_received` datetime DEFAULT NULL,
  `from_address` text,
  `to_address` text,
  `subject` text,
  `body` text,
  `filter_date` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `mails`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `mails`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;
```

All dates are inserted in local time. In case of missing headers or failed parsing
`NULL` is inserted.

The `message` column contains the complete email with body and headers.

The columns `date`, `from_address`, `to_address`, `subject` map respectively to the 
email headers `Date`, `From`, `To`, `Subject`.

`last_received` is populated with the first date found in the latest (top most)
`Received` header. Note that this header is meant for manual debugging and thus 
there is any standard dictating the content and format. MTAs can insert anything 
as Received header.

`filter_date` is the current local time at insertion determined by the filter.

`body` is the extracted and decoded body of the message. 
For multi-part messages it is the first non-attachment text part found.

## Configuration

Mandatory options are:

- `host`
- `user`
- `password`
- `database`
- `table`

Optional options are:

- `port` defaults to `3306`

The options `host`, `port`, `user`, `password`, `database`, `table` describe the 
connection to the MYSQL server.

## Example pipeline

```yaml
inputs:
- name: main_smtp_input
  smtp:
    port: 10025
    host: ""

pipelines:
- name: test
  inputs:
  - main_smtp_input
  filters:
  - mysql:
      host: mysql
      port: 3306
      user: foo
      password: "foo"
      database: mails
      table: test
    ignore_exceptions: true
```
