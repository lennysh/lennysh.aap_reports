# controller_build_jobs_with_hosts role

Builds a list of jobs with hostnames from Controller API data already in facts. No API calls. Use after fetching jobs and job host summaries (e.g. with `controller_fetch_jobs` and `controller_fetch_job_host_summaries`).

## Input (facts expected)

- `controller_organizations` – list of org dicts (from `controller_fetch_organizations`)
- `controller_jobs_raw` – list of job dicts (from `controller_fetch_jobs`)
- `controller_job_host_summaries` – dict mapping job id (string) to list of host summary dicts (from `controller_fetch_job_host_summaries`)

## Output (fact set)

- `controller_jobs_with_hosts` – list of job dicts, each with:
  - `id`, `username`, `organization`, `inventory_organization`, `job_template`
  - `project_id`, `project_name`
  - `created`, `started`, `finished`
  - `hostnames` – deduped, sorted, lowercase list of host names for that job

## Example

```yaml
- include_role: name: controller_detect
- include_role: name: controller_fetch_organizations
- include_role: name: controller_fetch_jobs
- name: Init job host summaries
  set_fact:
    controller_job_host_summaries: {}
- include_role:
    name: controller_fetch_job_host_summaries
  vars:
    current_job_id: "{{ item }}"
  loop: "{{ controller_jobs_raw | map(attribute='id') | list }}"
- include_role: name: controller_build_jobs_with_hosts
# controller_jobs_with_hosts is now set
```
