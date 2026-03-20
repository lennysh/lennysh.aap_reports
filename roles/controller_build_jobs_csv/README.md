# controller_build_jobs_csv role

Renders a CSV file from `controller_jobs_raw` (from `controller_fetch_jobs`). No API calls.

## Requirements

- `controller_jobs_raw` – list of job dicts from the Controller `/jobs/` API (including `summary_fields` and `launched_by` where applicable)

## Variables

| Variable | Description |
|----------|-------------|
| `controller_build_jobs_csv_output_folder` | Destination directory (default: `playbook_dir`) |
| `controller_build_jobs_csv_output_filename` | Base name without extension (default: `controller_jobs_export`) |
| `controller_build_jobs_csv_generated_at` | Optional timestamp string for the header |
| `controller_build_jobs_csv_aap_url` | Optional AAP URL shown in the header (defaults to `aap_url` if set) |

## License

MIT
