# controller_fetch_execution_environments role

Fetches all AAP Controller execution environments (paginated) and sets `controller_execution_environments` (list). Uses `controller_api_base_path`; run `controller_detect` first (or rely on `controller_token`, `report_node_metrics`, or `report_ee_metrics` to set it).

## Requirements

- `aap_url`, and either `aap_token` or `aap_username` + `aap_password`
- `controller_api_base_path` (from `controller_detect` or equivalent)
- Optional: `aap_validate_certs`, `controller_page_size`, `controller_request_delay` (defaults from **global_vars** role)

## Facts set

- `controller_execution_environments` – list of execution environment dicts from the API (each includes id, name, image, organization, credential, pull, managed, summary_fields, etc.)

## License

MIT
