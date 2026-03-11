# controller_fetch_inventory_hosts role

Fetches hosts for one inventory (paginated) and merges them into `controller_inventory_hosts[inventory_id]`. Call in a loop over inventory IDs; pass `current_inv_id` for each run. Uses `controller_api_base_path`; run `controller_detect` first.

## Requirements

- `aap_url`, and either `aap_token` or `aap_username` + `aap_password`
- `controller_api_base_path` (from `controller_detect` or equivalent)
- `current_inv_id` – inventory ID for this run (set by the caller)
- `controller_inventory_hosts` – dict to merge into (initialize to `{}` before first call)
- Optional: `aap_validate_certs`, `controller_page_size`, `controller_request_delay` (defaults from **global_vars** role)

## Facts set

- `controller_inventory_hosts` – updated with hosts for `current_inv_id` (keyed by inventory id string)

## License

MIT
