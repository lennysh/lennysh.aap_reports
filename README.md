# Ansible Collection - lennysh.aap_reports

[![GitHub last commit](https://img.shields.io/github/last-commit/lennysh/lennysh.aap_reports.svg)](https://github.com/lennysh/lennysh.aap_reports/commits/main) [![GitHub license](https://img.shields.io/github/license/lennysh/lennysh.aap_reports.svg)](https://github.com/lennysh/lennysh.aap_reports/blob/main/LICENSE) [![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](https://github.com/lennysh/lennysh.aap_reports/pulls) ![GitHub contributors](https://img.shields.io/github/contributors/lennysh/lennysh.aap_reports) ![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/lennysh/lennysh.aap_reports/tests.yml) ![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/lennysh/lennysh.aap_reports)

This Ansible collection provides tools to generate reports from Ansible Automation Platform (AAP) Controller.

## Requirements

- Ansible 2.15.0 or higher
- Python 3.6+
- `requests` library (`pip install requests`)

## Installation

### Install from Ansible Galaxy

```bash
ansible-galaxy collection install lennysh.aap_reports
```

### Install from Source

```bash
git clone https://github.com/lennysh/lennysh-aap_reports.git
cd lennysh-aap_reports
ansible-galaxy collection build .
ansible-galaxy collection install lennysh-aap_reports-*.tar.gz
```

## Roles

This collection includes the following roles:

| Role | Description | Documentation |
|------|-------------|---------------|
| `lennysh.aap_reports.node_metrics` | Generates node metrics reports from AAP Controller in multiple formats (markdown, CSV, HTML, JSON, YAML, XML, TXT). Includes a Subscription Details section (from controller `/config` when available) plus organization-level node and subscription metrics, max hosts limits, unique vs shared nodes/subscriptions, and detailed node-by-node breakdowns with organization membership. Optionally includes last-job columns (Job ID, Inventory, Inv. Org, User) when `node_metrics_include_jobs_with_hosts` is true. Uses internal controller_* roles for API path detection and data fetching. | [Role README](roles/node_metrics/README.md) |

**Controller roles** (used by node_metrics; reusable in playbooks): `controller_detect` (API path), `controller_token` (OAuth2 login/logout), `controller_fetch_*` (organizations, config, host_metrics, inventories, jobs, job host summaries), `controller_build_jobs_with_hosts`. See each role’s README under `roles/` for details.

## Plugins

This collection includes the following plugins:

| Plugin | Description | Documentation |
|--------|-------------|---------------|
| `lennysh.aap_reports.node_metrics` (module) | Collects node metrics data from AAP Controller API. Returns structured JSON data that can be used with Ansible templates to generate custom reports. | [Plugins README](plugins/README.md) |

## Quick Start

### Using the Node Metrics Role

```yaml
---
- name: Generate AAP Node Metrics Reports
  hosts: localhost
  gather_facts: false
  
  roles:
    - role: lennysh.aap_reports.node_metrics
      vars:
        aap_url: "https://aap.example.com"
        aap_username: "admin"
        aap_password: "{{ vault_aap_password }}"
        node_metrics_output_formats:
          - markdown
          - csv
          - html
```

For detailed usage instructions, see the [node_metrics role documentation](roles/node_metrics/README.md).

## Report Examples

Example reports in all supported formats are available in the [`report_examples/`](report_examples/) directory:

- [Markdown](report_examples/aap_node_metrics_report.md)
- [CSV](report_examples/aap_node_metrics_report.csv)
- [HTML](report_examples/aap_node_metrics_report.html)
- [JSON](report_examples/aap_node_metrics_report.json)
- [YAML](report_examples/aap_node_metrics_report.yaml)
- [XML](report_examples/aap_node_metrics_report.xml)
- [TXT](report_examples/aap_node_metrics_report.txt)

## Security Notes

- Passwords and tokens are marked as `no_log: true` in Ansible modules
- Tokens created by modules are automatically deleted after use
- Use Ansible Vault for storing sensitive credentials:
  ```bash
  ansible-vault create vars.yml
  ```
- Never commit credentials to version control

## Contributing

We welcome feedback and contributions.

* **Feature requests, bugs:** Open a [GitHub Issue](https://github.com/lennysh/lennysh.aap_reports/issues) and choose the appropriate template (Feature request or Bug report).
* **Questions, usage help, or chat:** Join the [Matrix channel](https://matrix.to/#/#lennysh-aap-reports:matrix.org).
* **Code or doc changes:** Open a Pull Request.

## License

MIT

## Author Information

- **Author**: Lenny Shirley
- **Company**: Red Hat
- **Issue Tracker**: https://github.com/lennysh/lennysh.aap_reports/issues
