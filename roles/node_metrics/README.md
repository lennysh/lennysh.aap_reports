# Node Metrics Role

This role generates node metrics reports from Ansible Automation Platform (AAP) Controller in multiple output formats.

## Description

The `node_metrics` role connects to the AAP Controller API, collects organization-level node and subscription metrics, fetches controller subscription/license details from the `/config` endpoint when available, and generates reports using pre-built Jinja2 templates. It supports generating reports in multiple formats simultaneously.

## Requirements

- Ansible 2.15.0 or higher
- Python 3.6+
- `requests` library (`pip install requests`)
- Access to AAP Controller API
- Valid authentication credentials (username/password or API token)

## Role Variables

### Required Variables

| Variable | Description |
|----------|-------------|
| `aap_url` | AAP Controller base URL (e.g., `https://aap.example.com`) |

### Authentication (One Required)

| Variable | Description |
|----------|-------------|
| `aap_username` | Username for authentication |
| `aap_password` | Password for authentication |
| `aap_token` | API token (alternative to username/password) |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `node_metrics_output_folder` | `{{ playbook_dir }}` | Directory where report files will be written |
| `node_metrics_output_filename` | `aap_node_metrics_report` | Base filename (file extension added automatically based on format) |
| `node_metrics_show_node_details` | `true` | Whether to include the "Node Details by Organization" section in reports |
| `node_metrics_include_jobs_with_hosts` | `false` | When `true`, fetches Controller API data via `ansible.builtin.uri` (orgs, jobs, job host summaries) and adds last job info (Job ID, template, organization, user) to both **Node Details by Organization** and **Orphaned Nodes** tables. Data is stored in reusable vars for the run. |
| `node_metrics_controller_page_size` | `200` | Page size for Controller API pagination (organizations, jobs, job_host_summaries). |
| `node_metrics_controller_request_delay` | `0.15` | Seconds to pause between Controller API requests. |
| `node_metrics_output_formats` | `[markdown]` | List of formats to generate. Options: `markdown`, `csv`, `html`, `json`, `yaml`, `xml`, `txt` |

## Supported Output Formats

The role supports generating reports in the following formats:

- **markdown** (`.md`) - Markdown format with tables, suitable for documentation
- **csv** (`.csv`) - Comma-separated values, suitable for spreadsheet import
- **html** (`.html`) - HTML format with embedded CSS styling
- **json** (`.json`) - JSON format for programmatic processing
- **yaml** (`.yaml`) - YAML format for configuration files
- **xml** (`.xml`) - XML format for structured data
- **txt** (`.txt`) - Plain text format for terminal viewing

## Controller API (reusable controller_* roles)

The role uses separate, reusable roles to fetch Controller data via `ansible.builtin.uri`. Each controller role sets Ansible facts that the next role or `node_metrics` uses. API path is detected automatically (AAP 2.4 `/api/v2` vs AAP 2.5+ `/api/controller/v2`).

- **Roles used (in order):** `controller_detect`, `controller_fetch_organizations`, `controller_fetch_config`, `controller_fetch_host_metrics`, `controller_fetch_inventories`, then (per inventory) `controller_fetch_inventory_hosts`. Optionally when jobs-with-hosts is enabled: `controller_fetch_jobs`, then (per job) `controller_fetch_job_host_summaries`, then `controller_build_jobs_with_hosts`. These roles live alongside `node_metrics` in the repo and can be reused by other playbooks or roles.
- **Node_metrics-specific (still in this role):** `tasks/controller/build_metrics.yml` (runs `files/build_metrics.py`). This role then sets `node_metrics_jobs_with_hosts` from `controller_jobs_with_hosts` when jobs-with-hosts is enabled.
- **Shared vars (always set):** `controller_api_base_path`, `controller_organizations`, `controller_config`, `controller_host_metrics`, `controller_inventories`, `controller_inventory_hosts`. The role then runs the build_metrics script to produce `node_metrics_data`.
- **When `node_metrics_include_jobs_with_hosts` is true:** `controller_jobs_raw`, `controller_job_host_summaries`, and `node_metrics_jobs_with_hosts` are also set.

## Dependencies

This role does not depend on the `lennysh.aap_reports.node_metrics` module. It uses `ansible.builtin.uri` and a bundled Python script (`files/build_metrics.py`) to build the metrics structure from Controller API data.

## Example Playbooks

### Basic Usage - Single Format

```yaml
---
- name: Generate Markdown Report
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
```

### Generate Multiple Formats

```yaml
---
- name: Generate Reports in All Formats
  hosts: localhost
  gather_facts: false
  
  roles:
    - role: lennysh.aap_reports.node_metrics
      vars:
        aap_url: "https://aap.example.com"
        aap_token: "{{ vault_aap_token }}"
        node_metrics_output_folder: "/tmp/aap_reports"
        node_metrics_output_filename: "node_metrics"
        node_metrics_output_formats:
          - markdown
          - csv
          - html
          - json
          - yaml
          - xml
          - txt
```

### Using Ansible Vault for Credentials

```yaml
---
- name: Generate Report with Vaulted Credentials
  hosts: localhost
  gather_facts: false
  
  roles:
    - role: lennysh.aap_reports.node_metrics
      vars:
        aap_url: "https://aap.example.com"
        aap_username: "{{ vault_aap_username }}"
        aap_password: "{{ vault_aap_password }}"
        node_metrics_output_formats:
          - csv
          - html
```

Create the vault file:
```bash
ansible-vault create group_vars/all/vault.yml
```

### Hide Node Details Section

To generate reports with only the organization metrics table (without the detailed node-by-node breakdown):

```yaml
---
- name: Generate Report Without Node Details
  hosts: localhost
  gather_facts: false
  
  roles:
    - role: lennysh.aap_reports.node_metrics
      vars:
        aap_url: "https://aap.example.com"
        aap_token: "{{ vault_aap_token }}"
        node_metrics_show_node_details: false
        node_metrics_output_formats:
          - markdown
          - csv
```

## Output Files

When the role runs successfully, it generates report files in the specified output folder with the naming pattern:
```
{node_metrics_output_folder}/{node_metrics_output_filename}.{extension}
```

For example, with default settings and `markdown` format:
- Output: `{playbook_dir}/aap_node_metrics_report.md`

When generating multiple formats, each format gets its own file:
- `aap_node_metrics_report.md`
- `aap_node_metrics_report.csv`
- `aap_node_metrics_report.html`
- `aap_node_metrics_report.json`
- `aap_node_metrics_report.yaml`
- `aap_node_metrics_report.xml`
- `aap_node_metrics_report.txt`

### Example Reports

Example reports in all supported formats are available in the [`report_examples/`](../../report_examples/) directory:

- [Markdown](../../report_examples/aap_node_metrics_report.md)
- [CSV](../../report_examples/aap_node_metrics_report.csv)
- [HTML](../../report_examples/aap_node_metrics_report.html)
- [JSON](../../report_examples/aap_node_metrics_report.json)
- [YAML](../../report_examples/aap_node_metrics_report.yaml)
- [XML](../../report_examples/aap_node_metrics_report.xml)
- [TXT](../../report_examples/aap_node_metrics_report.txt)

## Report Structure

All formats contain the same data, structured as follows:

### Subscription Details (when available)

When the controller `/config` endpoint is available, every report includes a **Subscription Details** section at the top with license and system information, including:

- **Status** – Compliance status (e.g. In compliance, Out of compliance) and optional description
- **Hosts remaining** – Remaining managed hosts from the license
- **Subscription type** – License type (e.g. enterprise)
- **Expires on** / **Expires on UTC** – License expiry (formatted)
- **Automation controller version** – Controller version from config
- **Hosts automated** – Consumed license seats and “since” date
- **Hosts deleted** – Deleted instances count
- **Subscription (SKU)** – Product/subscription name (e.g. Employee SKU)
- **Hosts imported** – Current/active instances
- **Active hosts previously deleted** – Reactivated instances
- **Trial** – Trial license flag
- **Days remaining** – Days until license expiry (when derivable)

If `/config` is unavailable or fails, this section is omitted and the rest of the report is unchanged.

### Organization Metrics
- **Max Nodes**: Maximum number of hosts allowed for the organization (0 = Unlimited, shown as "Unlimited" in reports)
- Total nodes per organization with percentage of total
- Unique nodes (only in that organization) with percentage
- Shared nodes (in multiple organizations) with percentage
- Unique subscriptions (subscription-consuming nodes unique to org) with percentage
- Shared subscriptions (subscription-consuming nodes shared across orgs) with percentage
- Organizations are sorted alphabetically by name

### Node Details
- Complete list of all nodes
- Subscription consumption status for each node
- **Organizations**: Comma-delimited list of organization names that each node belongs to (sorted alphabetically)

## License

MIT

## Author Information

- **Author**: Lenny Shirley
- **Company**: Red Hat
