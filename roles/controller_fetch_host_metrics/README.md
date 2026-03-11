# controller_fetch_host_metrics role

Fetches all AAP Controller host_metrics (paginated) and sets `controller_host_metrics` (list). Uses `controller_api_base_path`; run `controller_detect` first.

## Requirements

- `aap_url`, and either `aap_token` or `aap_username` + `aap_password`
- `controller_api_base_path` (from `controller_detect` or equivalent)
- Optional: `aap_validate_certs`, `node_metrics_controller_page_size`, `node_metrics_controller_request_delay`

## Facts set

- `controller_host_metrics` – list of host_metrics dicts from the API

## License

MIT
