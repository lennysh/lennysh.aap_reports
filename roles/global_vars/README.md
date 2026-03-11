# global_vars

Shared default variables for AAP Controller API usage. This role has no tasks; it only provides defaults so that any role or play that uses the Controller API (e.g. `controller_fetch_organizations`, `controller_fetch_host_metrics`) can rely on consistent variable names without depending on a specific report role.

## Variables (defaults)

| Variable | Default | Description |
|----------|---------|-------------|
| `controller_page_size` | `200` | Page size for Controller API paginated list endpoints. |
| `controller_request_delay` | `0.15` | Seconds to pause between Controller API requests (throttling). |

## Usage

Include this role as a dependency in roles that use Controller API fetch roles, or include it at the start of a play that uses those roles. Override `controller_page_size` or `controller_request_delay` when calling the report role or play if you need different values.

## Example

```yaml
- name: Run node metrics report with custom page size
  ansible.builtin.include_role:
    name: lennysh.aap_reports.report_node_metrics
  vars:
    controller_page_size: 100
    controller_request_delay: 0.2
```
