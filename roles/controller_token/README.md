# controller_token role

Obtains (login) and revokes (logout) AAP Controller OAuth2 tokens. By default the role performs **login**: it runs **controller_detect** to get the correct API base path (AAP 2.4 vs 2.5+), then POSTs to `{{ controller_api_base_path }}/tokens/` with Basic auth and sets `aap_token` and `token_url` as facts. With `controller_token_action: logout` it revokes the token (DELETE at `token_url`), suitable for use in an `always` block.

## Requirements

- `aap_url`, `aap_username`, `aap_password`
- Optional: `aap_validate_certs` (default true)

## Role variables

| Variable | Default | Description |
|----------|---------|-------------|
| `controller_token_action` | `login` | `login` = obtain token and set `aap_token` / `token_url`; `logout` = revoke token at `token_url` |
| `controller_token_scope` | `read` | Token scope sent when creating the token (e.g. `read`, `write`) |
| `controller_token_description` | `Temporary token for automation` | Description sent when creating the token |

## Facts set (login only)

- `aap_token` – token string for Bearer auth
- `token_url` – path (e.g. `/api/v2/tokens/123/` or `/api/controller/v2/tokens/123/`) used for revocation

## Example: block + always

```yaml
- name: Run API tasks with temporary token
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Token lifecycle
      block:
        - name: Login and get token
          ansible.builtin.include_role:
            name: controller_token

        - name: Your tasks here (aap_token is set)
          ansible.builtin.include_role:
            name: node_metrics
          # or other roles that use aap_token

      always:
        - name: Logout (revoke token)
          ansible.builtin.include_role:
            name: controller_token
          vars:
            controller_token_action: logout
```

## Example: login only

```yaml
- include_role: name: controller_token
# aap_token and token_url are set for subsequent tasks
```

## Example: logout only (e.g. if token was created earlier)

```yaml
- include_role:
    name: controller_token
  vars:
    controller_token_action: logout
# Requires token_url (and aap_url, aap_username, aap_password)
```
