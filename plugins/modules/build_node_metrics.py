#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Lenny Shirley
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: build_node_metrics
short_description: Build node metrics structure from AAP Controller API data (no API calls)
version_added: "1.0.0"
description:
    - Takes controller data (config, organizations, host_metrics, inventories, inventory_hosts)
      and builds the metrics structure used by the report_node_metrics role (subscription details,
      per-org stats, node list, percentages). No network calls; pure computation.
    - Use after fetching data with controller_fetch_* roles; pass the controller_* facts as arguments.
options:
    config:
        description: Controller /config JSON (for subscription/license details). Omit if unavailable.
        required: false
        type: dict
        default: null
    organizations:
        description: List of organization dicts from controller_fetch_organizations.
        required: false
        type: list
        elements: dict
        default: []
    host_metrics:
        description: List of host_metrics from controller_fetch_host_metrics.
        required: false
        type: list
        elements: dict
        default: []
    inventories:
        description: List of inventory dicts from controller_fetch_inventories.
        required: false
        type: list
        elements: dict
        default: []
    inventory_hosts:
        description: Dict mapping inventory id (str or int) to list of host dicts (from controller_fetch_inventory_hosts).
        required: false
        type: dict
        default: {}
    aap_url:
        description: AAP Controller base URL (e.g. for report header).
        required: false
        type: str
        default: ""
author: "Lenny Shirley (@lennysh)"
'''

EXAMPLES = r'''
# Called by report_node_metrics role after controller_* fetch roles
- name: Build node metrics from controller data
  lennysh.aap_reports.build_node_metrics:
    config: "{{ controller_config | default(omit) }}"
    organizations: "{{ controller_organizations }}"
    host_metrics: "{{ controller_host_metrics }}"
    inventories: "{{ controller_inventories }}"
    inventory_hosts: "{{ controller_inventory_hosts }}"
    aap_url: "{{ aap_url }}"
  register: node_metrics

- name: Use the result
  ansible.builtin.set_fact:
    report_node_metrics_data:
      metrics: "{{ node_metrics.metrics }}"
      organizations_count: "{{ node_metrics.organizations_count }}"
      nodes_count: "{{ node_metrics.nodes_count }}"
...
'''

RETURN = r'''
metrics:
    description: Metrics structure (generated_at, aap_url, subscription_details, organizations, totals, nodes, organization_names).
    returned: always
    type: dict
organizations_count:
    description: Number of organizations (from input).
    returned: always
    type: int
nodes_count:
    description: Number of distinct nodes in the built node list.
    returned: always
    type: int
'''


from datetime import datetime
from ansible.module_utils.basic import AnsibleModule


def build_subscription_details(config_json):
    if not config_json:
        return None
    try:
        license_info = config_json.get("license_info") or {}
        version = config_json.get("version") or "(placeholder)"
        compliant = license_info.get("compliant", True)
        status = "Out of compliance" if not compliant else "Compliant"
        status_description = (
            "You have automated against more hosts than your subscription allows."
            if not compliant
            else "The number of hosts you have automated against is below your subscription count."
        )
        free_instances = license_info.get("free_instances")
        if free_instances is not None:
            free_instances = int(free_instances)
        license_date_raw = license_info.get("license_date")
        expires_on = expires_on_utc = ""
        if license_date_raw is not None and str(license_date_raw).strip():
            try:
                ts = int(license_date_raw)
                if ts > 1000000000:
                    expires_on = datetime.utcfromtimestamp(ts).strftime("%m/%d/%Y, %I:%M:%S %p")
                    expires_on_utc = datetime.utcfromtimestamp(ts).strftime("%m/%d/%Y, %I:%M:%S %p UTC")
                else:
                    expires_on = str(license_date_raw)
                    expires_on_utc = "(placeholder)"
            except (ValueError, TypeError, OSError):
                expires_on = str(license_date_raw)
                expires_on_utc = "(placeholder)"
        if not expires_on:
            expires_on = "(placeholder)"
        if not expires_on_utc:
            expires_on_utc = "(placeholder)"
        time_remaining = license_info.get("time_remaining")
        days_remaining = None
        if time_remaining is not None:
            try:
                days_remaining = max(0, int(time_remaining) // 86400)
            except (ValueError, TypeError):
                pass
        automated_instances = license_info.get("automated_instances")
        automated_since = license_info.get("automated_since")
        if automated_instances is not None:
            automated_instances = int(automated_instances)
        if automated_since is not None:
            try:
                ts = int(automated_since)
                since_str = datetime.utcfromtimestamp(ts).strftime("%m/%d/%Y, %I:%M:%S %p") if ts > 1000000000 else "(placeholder)"
                hosts_automated = "%s since %s" % (automated_instances, since_str)
            except (ValueError, TypeError, OSError):
                hosts_automated = "%s since (placeholder)" % automated_instances if automated_instances is not None else "(placeholder)"
        else:
            hosts_automated = "%s since (placeholder)" % automated_instances if automated_instances is not None else "(placeholder)"
        subscription_sku = (
            license_info.get("product_name") or license_info.get("subscription_name")
            or license_info.get("sku") or "(placeholder)"
        )
        deleted_instances = license_info.get("deleted_instances")
        deleted_instances = int(deleted_instances) if deleted_instances is not None else "(placeholder)"
        reactivated = license_info.get("reactivated_instances")
        active_hosts_previously_deleted = int(reactivated) if reactivated is not None else "(placeholder)"
        current_instances = license_info.get("current_instances")
        current_instances = int(current_instances) if current_instances is not None else "(placeholder)"
        trial = license_info.get("trial")
        trial = "True" if trial else "False" if trial is not None else "(placeholder)"
        return {
            "status": status,
            "status_description": status_description,
            "hosts_remaining": free_instances if free_instances is not None else "(placeholder)",
            "subscription_type": license_info.get("license_type") or "(placeholder)",
            "expires_on": expires_on,
            "expires_on_utc": expires_on_utc,
            "automation_controller_version": version,
            "hosts_automated": hosts_automated,
            "hosts_deleted": deleted_instances,
            "subscription_sku": subscription_sku,
            "hosts_imported": current_instances,
            "active_hosts_previously_deleted": active_hosts_previously_deleted,
            "trial": trial,
            "days_remaining": days_remaining,
        }
    except Exception:
        return None


def calculate_percentage(value, total):
    if total == 0:
        return 0.0
    return round((value / total) * 100, 1)


def build_metrics(config, organizations, host_metrics, inventories, inventory_hosts, aap_url):
    organizations = organizations or []
    host_metrics = host_metrics or []
    inventories = inventories or []
    inventory_hosts = inventory_hosts or {}
    aap_url = aap_url or ""

    subscription_details = build_subscription_details(config)
    org_id_to_name = {org["id"]: org["name"] for org in organizations}
    inventory_org_map = {inv["id"]: inv["organization"] for inv in inventories}

    inventory_nodes = {}
    for inv in inventories:
        inv_id = inv["id"]
        hosts = inventory_hosts.get(str(inv_id), inventory_hosts.get(inv_id, []))
        for node in hosts:
            nodename = node.get("name") if isinstance(node, dict) else None
            if nodename:
                inventory_nodes["%s:%s" % (inv_id, nodename)] = True

    org_nodes_set = {}
    node_to_orgs_set = {}
    for key in inventory_nodes.keys():
        inv_id, nodename = key.split(":", 1)
        org_id = inventory_org_map.get(int(inv_id))
        if org_id is not None:
            nodename_lower = nodename.lower()
            if org_id not in org_nodes_set:
                org_nodes_set[org_id] = set()
            org_nodes_set[org_id].add(nodename_lower)
            if nodename_lower not in node_to_orgs_set:
                node_to_orgs_set[nodename_lower] = set()
            node_to_orgs_set[nodename_lower].add(org_id)

    host_metrics_by_node = {}
    for metric in host_metrics:
        nodename = metric.get("hostname")
        if nodename:
            nodename_lower = nodename.lower()
            host_metrics_by_node[nodename_lower] = {
                "first_automation": metric.get("first_automation"),
                "last_automation": metric.get("last_automation"),
                "last_deleted": metric.get("last_deleted"),
                "automated_counter": metric.get("automated_counter"),
                "deleted_counter": metric.get("deleted_counter"),
            }

    license_nodes_set = {}
    for metric in host_metrics:
        nodename = metric.get("hostname")
        deleted = metric.get("deleted", False)
        if nodename and not deleted:
            license_nodes_set[nodename.lower()] = True

    org_license_nodes_set = {}
    for nodename_lower in license_nodes_set.keys():
        if nodename_lower in node_to_orgs_set:
            for org_id in node_to_orgs_set[nodename_lower]:
                if org_id not in org_license_nodes_set:
                    org_license_nodes_set[org_id] = set()
                org_license_nodes_set[org_id].add(nodename_lower)

    totals = {"total_nodes": 0, "unique_nodes": 0, "shared_nodes": 0, "unique_licenses": 0, "shared_licenses": 0}
    org_list = []

    for org in organizations:
        org_id = org["id"]
        org_name = org["name"]
        max_hosts = org.get("max_hosts", 0)
        total_nodes = len(org_nodes_set.get(org_id, set()))
        unique_nodes = shared_nodes = 0
        for nodename in org_nodes_set.get(org_id, set()):
            if len(node_to_orgs_set.get(nodename, set())) > 1:
                shared_nodes += 1
            else:
                unique_nodes += 1
        unique_licenses = shared_licenses = 0
        for nodename in org_license_nodes_set.get(org_id, set()):
            if len(node_to_orgs_set.get(nodename, set())) > 1:
                shared_licenses += 1
            else:
                unique_licenses += 1
        totals["total_nodes"] += total_nodes
        totals["unique_nodes"] += unique_nodes
        totals["unique_licenses"] += unique_licenses
        org_list.append({
            "id": org_id,
            "name": org_name,
            "max_hosts": max_hosts,
            "total_nodes": total_nodes,
            "unique_nodes": unique_nodes,
            "shared_nodes": shared_nodes,
            "unique_licenses": unique_licenses,
            "shared_licenses": shared_licenses,
        })

    orphaned_license_nodes = [n for n in license_nodes_set if n not in node_to_orgs_set]
    orphaned_licenses_count = len(orphaned_license_nodes)
    if orphaned_licenses_count > 0:
        org_list.append({
            "id": None,
            "name": "Orphaned Nodes (No Organization)",
            "max_hosts": None,
            "total_nodes": 0,
            "unique_nodes": orphaned_licenses_count,
            "shared_nodes": None,
            "unique_licenses": orphaned_licenses_count,
            "shared_licenses": None,
        })
        totals["unique_nodes"] += orphaned_licenses_count
        totals["unique_licenses"] += orphaned_licenses_count

    for nodename_lower in node_to_orgs_set:
        if len(node_to_orgs_set[nodename_lower]) > 1:
            totals["shared_nodes"] += 1
    for nodename_lower in license_nodes_set:
        if nodename_lower in node_to_orgs_set and len(node_to_orgs_set[nodename_lower]) > 1:
            totals["shared_licenses"] += 1

    for org_entry in org_list:
        org_entry["total_nodes_pct"] = calculate_percentage(org_entry["total_nodes"], totals["total_nodes"])
        org_entry["unique_nodes_pct"] = calculate_percentage(org_entry["unique_nodes"], totals["unique_nodes"])
        org_entry["shared_nodes_pct"] = (
            calculate_percentage(org_entry["shared_nodes"], totals["shared_nodes"])
            if org_entry["shared_nodes"] is not None else None
        )
        org_entry["unique_licenses_pct"] = calculate_percentage(org_entry["unique_licenses"], totals["unique_licenses"])
        org_entry["shared_licenses_pct"] = (
            calculate_percentage(org_entry["shared_licenses"], totals["shared_licenses"])
            if org_entry["shared_licenses"] is not None else None
        )

    org_list.append({
        "id": -1,
        "name": "TOTAL",
        "max_hosts": None,
        "total_nodes": totals["total_nodes"],
        "unique_nodes": totals["unique_nodes"],
        "shared_nodes": totals["shared_nodes"],
        "unique_licenses": totals["unique_licenses"],
        "shared_licenses": totals["shared_licenses"],
        "total_nodes_pct": 0.0,
        "unique_nodes_pct": 0.0,
        "shared_nodes_pct": 0.0,
        "unique_licenses_pct": 0.0,
        "shared_licenses_pct": 0.0,
    })

    regular_orgs = [o for o in org_list if o["id"] is not None and o["id"] != -1]
    special_orgs = [o for o in org_list if o["id"] is None or o["id"] == -1]
    regular_orgs.sort(key=lambda x: x["name"].lower())
    special_orgs.sort(key=lambda x: (0 if x["id"] is None else 1, x["name"].lower()))
    org_list = regular_orgs + special_orgs

    all_nodes_set = set(node_to_orgs_set.keys()) | set(license_nodes_set.keys())
    nodes_list = []
    for nodename_lower in sorted(all_nodes_set):
        org_ids = [int(oid) for oid in node_to_orgs_set[nodename_lower]] if nodename_lower in node_to_orgs_set else []
        hm = host_metrics_by_node.get(nodename_lower, {})
        nodes_list.append({
            "nodename": nodename_lower,
            "license": nodename_lower in license_nodes_set,
            "organizations": sorted(org_ids),
            "first_automation": hm.get("first_automation"),
            "last_automation": hm.get("last_automation"),
            "last_deleted": hm.get("last_deleted"),
            "automated_counter": hm.get("automated_counter"),
            "deleted_counter": hm.get("deleted_counter"),
        })

    metrics = {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "aap_url": aap_url,
        "subscription_details": subscription_details,
        "organizations": org_list,
        "totals": totals,
        "nodes": nodes_list,
        "organization_names": org_id_to_name,
    }

    return {
        "metrics": metrics,
        "organizations_count": len(organizations),
        "nodes_count": len(nodes_list),
    }


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            config=dict(type="dict", default=None),
            organizations=dict(type="list", elements="dict", default=[]),
            host_metrics=dict(type="list", elements="dict", default=[]),
            inventories=dict(type="list", elements="dict", default=[]),
            inventory_hosts=dict(type="dict", default={}),
            aap_url=dict(type="str", default=""),
        ),
        supports_check_mode=True,
    )

    config = module.params["config"]
    organizations = module.params["organizations"]
    host_metrics = module.params["host_metrics"]
    inventories = module.params["inventories"]
    inventory_hosts = module.params["inventory_hosts"]
    aap_url = module.params["aap_url"]

    result = build_metrics(config, organizations, host_metrics, inventories, inventory_hosts, aap_url)
    module.exit_json(changed=False, **result)


if __name__ == "__main__":
    run_module()
