# report_ee_metrics role

Runs the full EE metrics pipeline and exports the report to multiple file formats. The role runs **controller_detect** (when needed), **controller_fetch_execution_environments**, **controller_fetch_jobs**, **controller_build_ee_metrics**, then generates report files from Jinja2 templates. Use it standalone with `aap_url` and credentials; it skips detect if `controller_api_base_path` is already set (e.g. after `controller_token` login).

## Requirements

- `aap_url`, and either `aap_token` or `aap_username` + `aap_password`
- Optional: `aap_validate_certs`, `controller_page_size`, `controller_request_delay` (from **global_vars** role; used by fetch roles)

## Role variables

### Required

| Variable | Description |
|----------|-------------|
| `aap_url` | AAP Controller base URL |
| `aap_username` / `aap_password` **or** `aap_token` | Authentication |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `aap_validate_certs` | `true` | Whether to validate SSL certificates for Controller API requests (used by fetch roles). |
| `report_ee_metrics_output_folder` | `{{ playbook_dir }}` | Directory where report files are written |
| `report_ee_metrics_output_filename` | `aap_ee_metrics_report` | Base filename (extension added per format) |
| `report_ee_metrics_output_formats` | `[markdown, csv, html, json, yaml, xml, txt]` | List of formats to generate |
| `report_ee_metrics_generated_at` | `ansible_date_time.iso8601` | Timestamp shown in report header |
| `report_ee_metrics_aap_url` | `''` | AAP instance URL shown in report header (optional) |

## Supported formats

- **markdown** (`.md`) – Markdown table
- **csv** (`.csv`) – Comma-separated values
- **html** (`.html`) – HTML with embedded CSS
- **json** (`.json`) – JSON
- **yaml** (`.yaml`) – YAML
- **xml** (`.xml`) – XML
- **txt** (`.txt`) – Plain text table

## Dependencies

- **global_vars** – This role depends on the **global_vars** role for `controller_page_size` and `controller_request_delay` (used by controller_fetch_execution_environments and controller_fetch_jobs). When you use `report_ee_metrics`, global_vars is applied automatically via role dependencies.

## Example playbook

```yaml
- hosts: localhost
  gather_facts: true
  tasks:
    - ansible.builtin.include_role:
        name: lennysh.aap_reports.report_ee_metrics
      vars:
        aap_url: "https://aap.example.com"
        aap_username: "admin"
        aap_password: "{{ vault_aap_password }}"
        report_ee_metrics_output_folder: /tmp/ee_reports
        report_ee_metrics_output_formats:
          - csv
          - html
          - json
```

Output files (with default filename): `aap_ee_metrics_report.csv`, `aap_ee_metrics_report.html`, etc. The role runs detect, fetch execution environments, fetch jobs, build the report, then writes the requested formats.

## License

MIT
