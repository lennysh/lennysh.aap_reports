# Collection Plugins

This collection includes the following modules.

## Modules

### build_node_metrics

Builds the node metrics structure from AAP Controller API data (no API calls). Used by the `report_node_metrics` role after controller_* fetch roles have populated `controller_organizations`, `controller_config`, `controller_host_metrics`, `controller_inventories`, and `controller_inventory_hosts`.

**Module:** `lennysh.aap_reports.build_node_metrics`

**Parameters:** `config`, `organizations`, `host_metrics`, `inventories`, `inventory_hosts`, `aap_url` (all optional with sensible defaults).

**Returns:** `metrics` (dict), `organizations_count` (int), `nodes_count` (int).

See the module DOCUMENTATION for full options and examples.

## Plugin types

This collection currently includes:

- **modules** – `build_node_metrics` (node metrics from controller data), `aap_dummy_data` (dummy org/inventory/host data for testing).

For more information about Ansible plugin types, see [Working With Plugins](https://docs.ansible.com/ansible/latest/plugins/plugins.html).
