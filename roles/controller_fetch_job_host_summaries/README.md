# controller_fetch_job_host_summaries role

Fetches job host summaries for one job (paginated) and merges them into `controller_job_host_summaries[job_id]`. Call in a loop over job IDs; pass `current_job_id` for each run. Uses `controller_api_base_path`; run `controller_detect` first.

## Requirements

- `aap_url`, and either `aap_token` or `aap_username` + `aap_password`
- `controller_api_base_path` (from `controller_detect` or equivalent)
- `current_job_id` – job ID for this run (set by the caller)
- `controller_job_host_summaries` – dict to merge into (initialize to `{}` before first call)
- Optional: `aap_validate_certs`, `node_metrics_controller_page_size`, `node_metrics_controller_request_delay`

## Facts set

- `controller_job_host_summaries` – updated with host summaries for `current_job_id` (keyed by job id string)

## License

MIT
