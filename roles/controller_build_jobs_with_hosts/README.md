# controller_build_jobs_with_hosts role

Builds a list of jobs with hostnames from Controller API data already in facts. No API calls. Use after fetching jobs and job host summaries (e.g. with `controller_fetch_jobs` and `controller_fetch_job_host_summaries`).

## Input (facts expected)

- `controller_organizations` – list of org dicts (from `controller_fetch_organizations`)
- `controller_jobs_raw` – list of job dicts (from `controller_fetch_jobs`)
- `controller_job_host_summaries` – dict mapping job id (string) to list of host summary dicts (from `controller_fetch_job_host_summaries`)

## Output (fact set)

- `controller_jobs_with_hosts` – list of job dicts, each with:
  - `job_template_id` – job id (from API)
  - `username` – created_by username or launched_by name
  - `job_template_organization`, `job_template_organization_id` – job template’s org
  - `inventory`, `inventory_id` – inventory name and id
  - `inventory_organization`, `inventory_organization_id` – inventory’s org (resolved from `controller_organizations`)
  - `job_template` – job template name
  - `project_id`, `project_name`
  - `created`, `started`, `finished`
  - `hostnames` – deduped, sorted, lowercase list of host names for that job

Reports that use this data (e.g. report_node_metrics with `report_node_metrics_include_jobs_with_hosts`) show **Inventory** (inventory name) and **Inv. Org** (inventory organization) columns from these fields.

## Example

```yaml
- ansible.builtin.include_role:
    name: controller_detect
- ansible.builtin.include_role:
    name: controller_fetch_organizations
- ansible.builtin.include_role:
    name: controller_fetch_jobs
- name: Init job host summaries
  ansible.builtin.set_fact:
    controller_job_host_summaries: {}
- ansible.builtin.include_role:
    name: controller_fetch_job_host_summaries
  vars:
    current_job_id: "{{ item }}"
  loop: "{{ controller_jobs_raw | map(attribute='id') | list }}"
- ansible.builtin.include_role:
    name: controller_build_jobs_with_hosts
# controller_jobs_with_hosts is now set
```
