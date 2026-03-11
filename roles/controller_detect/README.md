# controller_detect role

Detects the AAP Controller API base path by trying `/api/controller/v2` (AAP 2.5+) then `/api/v2` (AAP 2.4). Sets the fact `controller_api_base_path` for use by other controller fetch roles.

## Requirements

- `aap_url` (required)
- Authentication: either `aap_token` or `aap_username` + `aap_password`
- Optional: `aap_validate_certs` (default true)

## Facts set

- `controller_api_base_path`: `"/api/controller/v2"` or `"/api/v2"`

## Reuse

Run this role before any `controller_fetch_*` role so they have `controller_api_base_path` available. The `controller_token` role (login), `report_node_metrics`, and `report_ee_metrics` roles run `controller_detect` when needed; they skip it if `controller_api_base_path` is already set (e.g. after a prior `controller_token` login). Example:

```yaml
- name: Detect API path
  ansible.builtin.include_role:
    name: controller_detect

- name: Fetch organizations
  ansible.builtin.include_role:
    name: controller_fetch_organizations
```
