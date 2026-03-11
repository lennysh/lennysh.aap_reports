# controller_build_ee_metrics role

Builds an EE (Execution Environment) metrics report from existing Controller API data. No API calls. Use after `controller_fetch_execution_environments` and `controller_fetch_jobs`.

## Input (facts expected)

- `controller_execution_environments` – list of execution environment dicts (from `controller_fetch_execution_environments`)
- `controller_jobs_raw` – list of job dicts (from `controller_fetch_jobs`); used to compute the most recent time a job used each EE

## Output (fact set)

- `ee_metrics_report` – list of report rows (one per execution environment), each with:
  - `name` – EE name
  - `created_by_username` – username of creator (from summary_fields.created_by)
  - `created` – creation date/time (ISO from API)
  - `modified_by_username` – username of last modifier (from summary_fields.modified_by)
  - `modified` – last modified date (ISO from API)
  - `organization_name` – organization name (from summary_fields.organization, or empty if none)
  - `last_used_by_job` – ISO timestamp of the most recent **finished** job that used this EE, or `null` if no jobs used it

## Example playbook flow

```yaml
- ansible.builtin.include_role:
    name: lennysh.aap_reports.controller_detect
- ansible.builtin.include_role:
    name: lennysh.aap_reports.controller_fetch_execution_environments
- ansible.builtin.include_role:
    name: lennysh.aap_reports.controller_fetch_jobs
- ansible.builtin.include_role:
    name: lennysh.aap_reports.controller_build_ee_metrics
# ee_metrics_report is now set; use it in a template or copy task
- ansible.builtin.copy:
    content: "{{ ee_metrics_report | to_nice_json }}"
    dest: /tmp/ee_metrics_report.json
```

## License

MIT
