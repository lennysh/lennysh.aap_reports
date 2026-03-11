# controller_fetch_config role

Fetches AAP Controller `/config` (single request) and sets `controller_config`. Used for subscription/license details in reports. Uses `controller_api_base_path`; run `controller_detect` first.

## Requirements

- `aap_url`, and either `aap_token` or `aap_username` + `aap_password`
- `controller_api_base_path` (from `controller_detect` or equivalent)
- Optional: `aap_validate_certs`

## Facts set

- `controller_config` – config JSON from the API, or `none` if the request fails (errors are ignored)

## License

MIT
