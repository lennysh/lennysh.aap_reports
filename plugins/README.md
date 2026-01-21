# Collection Plugins

This directory contains plugins for the `lennysh.aap_reports` Ansible collection.

## Modules

### node_metrics

The `node_metrics` module connects to the Ansible Automation Platform (AAP) Controller API and collects organization-level node and subscription metrics data.

#### Module: `lennysh.aap_reports.node_metrics`

**Description:**
Collects node metrics data from AAP Controller including:
- Organization-level node counts (total, unique, shared)
- Maximum hosts limit per organization (max_hosts field from API, 0 = Unlimited)
- Subscription consumption metrics (unique, shared)
- Detailed node information with organization membership
- Subscription consumption status per node

**Parameters:**

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `url` | Yes | str | AAP Controller base URL |
| `token` | No* | str | API token for authentication |
| `username` | No* | str | Username for authentication |
| `password` | No* | str | Password for authentication (no_log: true) |

\* Either `token` OR (`username` and `password`) is required.

**Returns:**

The module returns a dictionary with the following structure:

```yaml
organizations_count: 3
nodes_count: 10
metrics:
  generated_at: "2026-01-20 15:36:54 UTC"
  organizations:
    - name: "Default"
      max_hosts: 20
      total_nodes: 4
      total_nodes_pct: 44.4
      unique_nodes: 3
      unique_nodes_pct: 42.9
      shared_nodes: 1
      shared_nodes_pct: 50.0
      unique_licenses: 3
      unique_licenses_pct: 42.9
      shared_licenses: 1
      shared_licenses_pct: 50.0
  nodes:
    - nodename: "localhost"
      license: true
      organizations: [1, 4]
  organization_names:
    1: "Default"
    4: "DEMOLab"
    5: "Test Org 01"
```

**Examples:**

```yaml
# Using token
- name: Collect node metrics
  lennysh.aap_reports.node_metrics:
    url: "https://aap.example.com"
    token: "{{ aap_token }}"
  register: metrics_data

# Using username/password
- name: Collect node metrics
  lennysh.aap_reports.node_metrics:
    url: "https://aap.example.com"
    username: "admin"
    password: "{{ vault_aap_password }}"
  register: metrics_data

# Use the data in a custom template
- name: Generate custom report
  ansible.builtin.template:
    src: my_template.j2
    dest: /tmp/custom_report.html
  vars:
    metrics: "{{ metrics_data.metrics }}"
```

**Notes:**
- The module automatically handles pagination for all API endpoints
- If username/password is used, a temporary token is created and automatically deleted after use
- All API calls include proper error handling and informative error messages
- The module supports both token-based and basic authentication

## Plugin Types

This collection currently includes:

- **modules** - Custom Ansible modules for AAP Controller integration

For more information about Ansible plugin types, see [Working With Plugins](https://docs.ansible.com/ansible-core/2.18/plugins/plugins.html).
