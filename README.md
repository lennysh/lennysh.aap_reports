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
| `lennysh.aap_reports.report_node_metrics` | Generates node metrics reports from AAP Controller in multiple formats (markdown, CSV, HTML, JSON, YAML, XML, TXT). Includes a Subscription Details section (from controller `/config` when available) plus organization-level node and subscription metrics, max hosts limits, unique vs shared nodes/subscriptions, and detailed node-by-node breakdowns with organization membership. Optionally includes last-job columns (Job ID, Inventory, Inv. Org, User) when `report_node_metrics_include_jobs_with_hosts` is true. Depends on **global_vars** and uses controller_* roles for API path detection and data fetching. | [Role README](roles/report_node_metrics/README.md) |
| `lennysh.aap_reports.report_ee_metrics` | Generates Execution Environment (EE) metrics reports from AAP Controller in multiple formats. Fetches execution environments and jobs, builds a report (name, created/modified by, organization, last used by job), and exports to markdown, CSV, HTML, JSON, YAML, XML, TXT. Depends on **global_vars** and uses controller_detect, controller_fetch_execution_environments, controller_fetch_jobs, controller_build_ee_metrics. | [Role README](roles/report_ee_metrics/README.md) |
| `lennysh.aap_reports.global_vars` | Shared default variables for Controller API usage (`controller_page_size`, `controller_request_delay`). No tasks; included as a dependency by report and controller_fetch_* roles. | [Role README](roles/global_vars/README.md) |

**Controller roles** (reusable in playbooks; many depend on **global_vars**): `controller_detect` (API path), `controller_token` (OAuth2 login/logout), `controller_fetch_*` (organizations, config, host_metrics, inventories, inventory_hosts, jobs, job_host_summaries, execution_environments), `controller_build_jobs_with_hosts`, `controller_build_ee_metrics`. See each role’s README under `roles/` for details.

## Quick Start

### Using the Node Metrics Report Role

```yaml
---
- name: Generate AAP Node Metrics Reports
  hosts: localhost
  gather_facts: false
  
  roles:
    - role: lennysh.aap_reports.report_node_metrics
      vars:
        aap_url: "https://aap.example.com"
        aap_username: "admin"
        aap_password: "{{ vault_aap_password }}"
        report_node_metrics_output_formats:
          - markdown
          - csv
          - html
```

For detailed usage instructions, see the [report_node_metrics role documentation](roles/report_node_metrics/README.md).

### Using the EE Metrics Report Role

```yaml
---
- name: Generate AAP EE Metrics Reports
  hosts: localhost
  gather_facts: true
  tasks:
    - ansible.builtin.include_role:
        name: lennysh.aap_reports.report_ee_metrics
      vars:
        aap_url: "https://aap.example.com"
        aap_username: "admin"
        aap_password: "{{ vault_aap_password }}"
        report_ee_metrics_output_formats:
          - csv
          - html
```

See the [report_ee_metrics role documentation](roles/report_ee_metrics/README.md) for more options.

## Report Examples

Example reports in all supported formats are available in the [`report_examples/`](report_examples/) directory:

**Node metrics** ([`report_examples/node_metrics_reports/`](report_examples/node_metrics_reports/)): [Markdown](report_examples/node_metrics_reports/aap_node_metrics_report.md), [CSV](report_examples/node_metrics_reports/aap_node_metrics_report.csv), [HTML](report_examples/node_metrics_reports/aap_node_metrics_report.html), [JSON](report_examples/node_metrics_reports/aap_node_metrics_report.json), [YAML](report_examples/node_metrics_reports/aap_node_metrics_report.yaml), [XML](report_examples/node_metrics_reports/aap_node_metrics_report.xml), [TXT](report_examples/node_metrics_reports/aap_node_metrics_report.txt).

**EE metrics** ([`report_examples/ee_metrics_reports/`](report_examples/ee_metrics_reports/)): [Markdown](report_examples/ee_metrics_reports/aap_ee_metrics_report.md), [CSV](report_examples/ee_metrics_reports/aap_ee_metrics_report.csv), [HTML](report_examples/ee_metrics_reports/aap_ee_metrics_report.html), [JSON](report_examples/ee_metrics_reports/aap_ee_metrics_report.json), [YAML](report_examples/ee_metrics_reports/aap_ee_metrics_report.yaml), [XML](report_examples/ee_metrics_reports/aap_ee_metrics_report.xml), [TXT](report_examples/ee_metrics_reports/aap_ee_metrics_report.txt).

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
- **Issue Tracker**: https://github.com/lennysh/lennysh.aap_reports/issues
