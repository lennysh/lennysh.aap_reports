# controller_fetch_organizations role

Fetches all AAP Controller organizations (paginated) and sets `controller_organizations` (list). Uses `controller_api_base_path`; run `controller_detect` first (or rely on `controller_token` / `report_node_metrics` to set it).

## Requirements

- `aap_url`, and either `aap_token` or `aap_username` + `aap_password`
- `controller_api_base_path` (from `controller_detect` or equivalent)
- Optional: `aap_validate_certs`, `controller_page_size`, `controller_request_delay` (defaults from **global_vars** role)

## Facts set

- `controller_organizations` – list of organization dicts from the API

## License

MIT
