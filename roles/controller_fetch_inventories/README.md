# controller_fetch_inventories role

Fetches all AAP Controller inventories (paginated) and sets `controller_inventories` (list). Uses `controller_api_base_path`; run `controller_detect` first.

## Requirements

- `aap_url`, and either `aap_token` or `aap_username` + `aap_password`
- `controller_api_base_path` (from `controller_detect` or equivalent)
- Optional: `aap_validate_certs`, `controller_page_size`, `controller_request_delay` (defaults from **global_vars** role)

## Facts set

- `controller_inventories` – list of inventory dicts from the API

## License

MIT
