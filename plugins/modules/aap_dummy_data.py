#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Lenny Shirley
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: aap_dummy_data
short_description: Generate dummy AAP organization, inventory, and host data as JSON (no API calls)
version_added: "1.0.0"
description:
    - Generates the same dummy data structure that M(lennysh.aap_reports.aap_populate_dummy) would create,
      but returns it as JSON only. No connection to AAP is made; use the returned data to loop in
      playbooks (e.g. create resources via other modules or tools).
    - Uses 1-based numeric IDs for organizations and inventories so you can reference them when
      iterating over hosts.
options:
    org_count:
        description:
            - Number of dummy organizations to generate.
        required: true
        type: int
    hosts_count:
        description:
            - Total number of dummy host records to generate across all organizations/inventories.
        required: true
        type: int
    inventories_per_org:
        description:
            - Number of dummy inventories per organization.
        required: false
        type: int
        default: 1
    hostname_casing:
        description:
            - Casing style for hostnames. C(mixed) cycles lower, upper, and camel case with numbers.
        required: false
        type: str
        default: mixed
        choices: [ mixed, lower, upper, camel ]
    multi_org_percent:
        description:
            - Percentage (0-100) of hosts that should appear in multiple organizations (same logical
              host, possibly different casing).
        required: false
        type: int
        default: 0
    allow_same_name_different_casing:
        description:
            - When a host is in multiple orgs, use different casing per org (e.g. HOST01 in org1,
              host01 in org2).
        required: false
        type: bool
        default: false
    even_host_distribution:
        description:
            - If C(true), spread hosts evenly across organizations. If C(false), assign randomly.
        required: false
        type: bool
        default: false
    disabled_host_percent:
        description:
            - Percentage (0-100) of host records to mark as C(enabled) C(false).
        required: false
        type: int
        default: 0
author: "Lenny Shirley (@lennysh)"
'''

EXAMPLES = r'''
# Generate dummy data for 3 orgs, 30 hosts, then loop over it
- name: Generate dummy AAP data
  lennysh.aap_reports.aap_dummy_data:
    org_count: 3
    hosts_count: 30
    inventories_per_org: 2
    hostname_casing: mixed
  register: dummy

- name: Show organizations
  ansible.builtin.debug:
    msg: "Org {{ item.id }}: {{ item.name }}"
  loop: "{{ dummy.organizations }}"

- name: Show hosts (could create them via awx.awx.host or API later)
  ansible.builtin.debug:
    msg: "Host {{ item.name }} in inventory_id {{ item.inventory_id }}, enabled={{ item.enabled }}"
  loop: "{{ dummy.hosts }}"
'''

RETURN = r'''
organizations:
    description: List of dummy organizations (id, name). IDs are 1-based.
    returned: always
    type: list
    elements: dict
    sample: [ {"id": 1, "name": "DUMMY_ORG01"}, {"id": 2, "name": "DUMMY_ORG02"} ]
inventories:
    description: List of dummy inventories (id, name, organization_id). IDs are 1-based.
    returned: always
    type: list
    elements: dict
    sample: [ {"id": 1, "name": "DUMMY_ORG01_Inv01", "organization_id": 1} ]
hosts:
    description: List of dummy host records (name, inventory_id, organization_id, enabled, variables).
    returned: always
    type: list
    elements: dict
    sample: [ {"name": "host1", "inventory_id": 1, "organization_id": 1, "enabled": true, "variables": "{\\"ansible_connection\\": \\"local\\"}"} ]
'''


import json
import random
from ansible.module_utils.basic import AnsibleModule


def _hostname_variant(base_name, index, style):
    """Return hostname with numeric suffix in requested casing style."""
    num = str(index)
    if style == "lower":
        return (base_name + num).lower()
    if style == "upper":
        return (base_name + num).upper()
    if style == "camel":
        return (base_name + num).capitalize()
    styles = ["lower", "upper", "camel"]
    s = styles[index % 3]
    return _hostname_variant(base_name, index, s)


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            org_count=dict(type="int", required=True),
            hosts_count=dict(type="int", required=True),
            inventories_per_org=dict(type="int", default=1),
            hostname_casing=dict(type="str", default="mixed", choices=["mixed", "lower", "upper", "camel"]),
            multi_org_percent=dict(type="int", default=0),
            allow_same_name_different_casing=dict(type="bool", default=False),
            even_host_distribution=dict(type="bool", default=False),
            disabled_host_percent=dict(type="int", default=0),
        ),
        supports_check_mode=True,
    )

    org_count = module.params["org_count"]
    hosts_count = module.params["hosts_count"]
    inventories_per_org = module.params["inventories_per_org"]
    hostname_casing = module.params["hostname_casing"]
    multi_org_percent = max(0, min(100, module.params["multi_org_percent"]))
    allow_same_name_different_casing = module.params["allow_same_name_different_casing"]
    even_host_distribution = module.params["even_host_distribution"]
    disabled_host_percent = max(0, min(100, module.params["disabled_host_percent"]))

    if org_count < 1 or hosts_count < 1 or inventories_per_org < 1:
        module.fail_json(msg="org_count, hosts_count, and inventories_per_org must be >= 1")

    # Build organizations (1-based id)
    organizations = []
    for i in range(1, org_count + 1):
        organizations.append({"id": i, "name": "DUMMY_ORG%02d" % i})

    # Build inventories (1-based id, organization_id references org)
    inventories = []
    inv_id = 0
    invs_by_org = {}
    for org in organizations:
        oid = org["id"]
        invs_by_org[oid] = []
        for j in range(1, inventories_per_org + 1):
            inv_id += 1
            inv_name = "DUMMY_ORG%02d_Inv%02d" % (oid, j)
            inv_entry = {"id": inv_id, "name": inv_name, "organization_id": oid}
            inventories.append(inv_entry)
            invs_by_org[oid].append(inv_id)

    org_ids = [o["id"] for o in organizations]
    n_multi = int(round(hosts_count * multi_org_percent / 100.0))
    n_single = hosts_count - n_multi
    num_unique_logical = n_single + n_multi

    base_name = "host"
    host_variables = json.dumps({"ansible_connection": "local"})
    org_index_list = list(range(len(org_ids)))
    random.shuffle(org_index_list)

    hosts = []
    logical_index = 0

    # Single-org hosts
    for _ in range(n_single):
        if logical_index >= num_unique_logical:
            break
        if even_host_distribution:
            org_idx = org_index_list[logical_index % len(org_index_list)]
        else:
            org_idx = random.choice(org_index_list)
        org_id = org_ids[org_idx]
        inv_id = random.choice(invs_by_org[org_id])
        hostname = _hostname_variant(base_name, logical_index, hostname_casing)
        enabled = random.randint(1, 100) > disabled_host_percent
        hosts.append({
            "name": hostname,
            "inventory_id": inv_id,
            "organization_id": org_id,
            "enabled": enabled,
            "variables": host_variables,
        })
        logical_index += 1

    # Multi-org hosts
    for _ in range(n_multi):
        if logical_index >= num_unique_logical:
            break
        num_orgs_for_host = min(2 + (logical_index % 2), len(org_ids))
        chosen_org_idxs = random.sample(org_index_list, num_orgs_for_host)
        hostname_base_idx = logical_index
        for oidx in chosen_org_idxs:
            org_id = org_ids[oidx]
            inv_id = random.choice(invs_by_org[org_id])
            if allow_same_name_different_casing:
                style = ["upper", "lower", "camel"][oidx % 3]
                hostname = _hostname_variant(base_name, hostname_base_idx, style)
            else:
                hostname = _hostname_variant(base_name, hostname_base_idx, hostname_casing)
            enabled = random.randint(1, 100) > disabled_host_percent
            hosts.append({
                "name": hostname,
                "inventory_id": inv_id,
                "organization_id": org_id,
                "enabled": enabled,
                "variables": host_variables,
            })
        logical_index += 1

    module.exit_json(
        changed=False,
        organizations=organizations,
        inventories=inventories,
        hosts=hosts,
    )


if __name__ == "__main__":
    run_module()
