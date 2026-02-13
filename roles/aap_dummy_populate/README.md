# aap_dummy_populate role

Generates dummy organization, inventory, and host data using `lennysh.aap_reports.aap_dummy_data`, then creates those resources on an AAP Controller via API using `ansible.controller` (and for AAP 2.5+, `ansible.platform` for gateway organizations).

**Task layout:**
- `tasks/main.yml` — orchestrates get token, populate block, and clear token (always).
- `tasks/aap_24/` — AAP 2.4 only: `get_token.yml`, `clear_token.yml` (controller token).
- `tasks/aap_25/` — AAP 2.5+ only: `get_token.yml`, `clear_token.yml` (platform token), `gateway_organizations.yml`.
- `tasks/common/` — shared: `generate_dummy.yml`, `controller_organizations.yml`, `controller_inventories.yml`, `controller_hosts.yml`.

**Flow:**
- **AAP 2.4:** controller token only; controller orgs, inventories, hosts.
- **AAP 2.5+:** platform token; gateway orgs; then controller orgs, inventories, hosts.

## Requirements

- `ansible.controller` collection (organization, inventory, host, token modules).
- `ansible.platform` collection (AAP 2.5+ gateway organizations and token).
- `lennysh.aap_reports` collection (for `aap_dummy_data` module).

## Token handling

- If you set **only** `aap_username` and `aap_password` (no `aap_token`), the role creates a temporary token with `ansible.platform.token` (AAP 2.5+) or `ansible.controller.token` (AAP 2.4), uses it for all API tasks, then revokes it in an `always` block.
- If you set `aap_token`, that token is used and no get/clear token steps run.

## Role variables

Connection (set in play or extra vars):

- `aap_hostname` — AAP base URL (e.g. `https://aap.example.com`). **Same URL for 2.4 and 2.5+**; only the API endpoints (paths) differ by version.
- `aap_username` / `aap_password` — Basic auth (optional if token set).
- `aap_token` — API token (optional if username/password set).
- `aap_validate_certs` — Validate SSL (default: `true`).
- `aap_version` — `"2.4"` or `"2.5"` (default: `"2.5"`). When `>= 2.5`, gateway organizations are created first.

Dummy data shape (same as `aap_dummy_data`):

- `aap_dummy_org_count`, `aap_dummy_hosts_count`, `aap_dummy_inventories_per_org`
- `aap_dummy_hostname_casing`, `aap_dummy_multi_org_percent`, `aap_dummy_allow_same_name_different_casing`
- `aap_dummy_even_host_distribution`, `aap_dummy_disabled_host_percent`

## Example playbook

```yaml
- hosts: localhost
  gather_facts: false
  vars:
    aap_hostname: "https://aap.example.com"
    aap_username: admin
    aap_password: "{{ aap_password }}"
    aap_version: "2.5"
    aap_dummy_org_count: 3
    aap_dummy_hosts_count: 30
  roles:
    - role: lennysh.aap_reports.aap_dummy_populate
```
