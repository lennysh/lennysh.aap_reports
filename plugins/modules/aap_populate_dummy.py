#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Lenny Shirley
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: aap_populate_dummy
short_description: Populate an AAP Controller with dummy organizations, inventories, and hosts
version_added: "1.0.0"
description:
    - Creates dummy organizations, inventories, and hosts on an Ansible Automation Platform Controller.
    - Useful for testing reports and license/subscription behavior (e.g. same hostname in multiple
      orgs with different casing counts as one subscription).
    - Automatically detects API path (AAP 2.5+ uses /api/controller/v2/, AAP 2.4 and below use /api/v2/).
options:
    url:
        description:
            - AAP Controller base URL.
        required: true
        type: str
    username:
        description:
            - Username for authentication (optional if token provided).
        required: false
        type: str
    password:
        description:
            - Password for authentication (optional if token provided).
        required: false
        type: str
    token:
        description:
            - API token for authentication (optional if username/password provided).
        required: false
        type: str
    validate_certs:
        description:
            - Whether to validate SSL certificates.
        required: false
        type: bool
        default: true
    org_count:
        description:
            - Number of dummy organizations to create.
        required: true
        type: int
    hosts_count:
        description:
            - Total number of dummy hosts to create across all organizations/inventories.
        required: true
        type: int
    inventories_per_org:
        description:
            - Number of dummy inventories to create per organization. Hosts are distributed across these.
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
            - Percentage (0-100) of hosts that should appear in multiple organizations (same logical host,
              possibly different casing). Used to simulate shared nodes for license/report testing.
        required: false
        type: int
        default: 0
    allow_same_name_different_casing:
        description:
            - When a host is in multiple orgs, use different casing per org (e.g. HOST01 in org1,
              host01 in org2) to demonstrate AAP counts them as one subscription despite casing.
        required: false
        type: bool
        default: false
    even_host_distribution:
        description:
            - If C(true), spread hosts evenly across organizations (e.g. 30 hosts, 3 orgs → 10 each).
            - If C(false) (default), assign each host to a random org so counts per org vary but total is correct.
        required: false
        type: bool
        default: false
    disabled_host_percent:
        description:
            - Percentage (0-100) of created hosts to create with C(enabled) set to C(false).
            - Useful for testing reports that distinguish enabled vs disabled hosts.
        required: false
        type: int
        default: 0
author: "Lenny Shirley (@lennysh)"
'''

EXAMPLES = r'''
# Create 3 orgs, 2 inventories per org, 30 hosts (mixed casing), no multi-org
- name: Populate AAP with dummy data
  lennysh.aap_reports.aap_populate_dummy:
    url: https://aap.example.com
    token: "{{ aap_token }}"
    org_count: 3
    hosts_count: 30
    inventories_per_org: 2
    hostname_casing: mixed

# Create 5 orgs, 50 hosts, 20% in multiple orgs with different casing to show license dedup
- name: Populate with shared hosts (different casing per org)
  lennysh.aap_reports.aap_populate_dummy:
    url: https://aap.example.com
    username: admin
    password: "{{ aap_password }}"
    org_count: 5
    hosts_count: 50
    multi_org_percent: 20
    allow_same_name_different_casing: true
  register: populate_result

# 30 hosts across 3 orgs with even split (10 per org)
- name: Populate with even host distribution
  lennysh.aap_reports.aap_populate_dummy:
    url: https://aap.example.com
    token: "{{ aap_token }}"
    org_count: 3
    hosts_count: 30
    even_host_distribution: true
'''

RETURN = r'''
organizations_created:
    description: Number of organizations created
    returned: always
    type: int
inventories_created:
    description: Number of inventories created
    returned: always
    type: int
hosts_created:
    description: Number of host records created (may exceed unique hostnames when in multiple orgs)
    returned: always
    type: int
organization_ids:
    description: List of created organization IDs
    returned: always
    type: list
    elements: int
inventory_ids:
    description: List of created inventory IDs (org order preserved via inventory_org_map)
    returned: always
    type: list
    elements: int
inventory_org_map:
    description: Map of inventory ID to organization ID
    returned: always
    type: dict
host_summary:
    description: Summary of host names and which inventories they were added to
    returned: always
    type: list
    elements: dict
'''


import json
import random
from ansible.module_utils.basic import AnsibleModule

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def _api_request(module, method, url_full, auth=None, headers=None, verify=True, json_body=None):
    """Perform API request and return response or fail."""
    kwargs = {"timeout": 30, "verify": verify}
    if auth:
        kwargs["auth"] = auth
    else:
        kwargs["headers"] = dict(headers) if headers else {}
    if json_body is not None and method.upper() in ("POST", "PUT", "PATCH"):
        kwargs["json"] = json_body
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"].setdefault("Content-Type", "application/json")
    try:
        if method.upper() == "GET":
            r = requests.get(url_full, **kwargs)
        elif method.upper() == "POST":
            r = requests.post(url_full, **kwargs)
        else:
            module.fail_json(msg="Unsupported method: %s" % method)
        r.raise_for_status()
        return r.json() if r.content else {}
    except requests.exceptions.RequestException as e:
        err_resp = getattr(e, "response", None)
        body = err_resp.text if err_resp is not None and err_resp.text else ""
        module.fail_json(msg="API request failed: %s. %s" % (str(e), body))


def detect_api_path(module, url, auth=None, headers=None, verify=True):
    """Detect Controller API base path (v2.5+ vs v2.4)."""
    for base_path, test_endpoint in [
        ("/api/controller/v2", "/api/controller/v2/organizations/?page=1&page_size=1"),
        ("/api/v2", "/api/v2/organizations/?page=1&page_size=1"),
    ]:
        try:
            full = url.rstrip("/") + test_endpoint
            if auth:
                resp = requests.get(full, auth=auth, verify=verify, timeout=10)
            else:
                resp = requests.get(full, headers=headers, verify=verify, timeout=10)
            if resp.status_code == 200:
                return base_path
        except Exception:
            continue
    return "/api/controller/v2"


def _hostname_variant(base_name, index, style):
    """Return hostname with numeric suffix in requested casing style. base_name is like 'host'."""
    num = str(index)
    if style == "lower":
        return (base_name + num).lower()
    if style == "upper":
        return (base_name + num).upper()
    if style == "camel":
        return (base_name + num).capitalize()
    # mixed: cycle lower, upper, camel
    styles = ["lower", "upper", "camel"]
    s = styles[index % 3]
    return _hostname_variant(base_name, index, s)


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            url=dict(type="str", required=True),
            username=dict(type="str", required=False),
            password=dict(type="str", required=False, no_log=True),
            token=dict(type="str", required=False, no_log=True),
            validate_certs=dict(type="bool", default=True),
            org_count=dict(type="int", required=True),
            hosts_count=dict(type="int", required=True),
            inventories_per_org=dict(type="int", default=1),
            hostname_casing=dict(type="str", default="mixed", choices=["mixed", "lower", "upper", "camel"]),
            multi_org_percent=dict(type="int", default=0),
            allow_same_name_different_casing=dict(type="bool", default=False),
            even_host_distribution=dict(type="bool", default=False),
            disabled_host_percent=dict(type="int", default=0),
        ),
        required_one_of=[["token", "username"]],
        required_together=[["username", "password"]],
        supports_check_mode=False,
    )

    if not HAS_REQUESTS:
        module.fail_json(msg="The requests library is required. Install with: pip install requests")

    url = module.params["url"].rstrip("/")
    username = module.params.get("username")
    password = module.params.get("password")
    token = module.params.get("token")
    validate_certs = module.params.get("validate_certs", True)
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

    auth = None
    headers = None
    if token:
        headers = {"Authorization": "Bearer %s" % token, "Content-Type": "application/json"}
    else:
        auth = (username, password)

    api_base_path = detect_api_path(module, url, auth=auth, headers=headers, verify=validate_certs)
    base_url = url + api_base_path

    org_ids = []
    inv_ids = []
    inventory_org_map = {}
    host_summary = []
    hosts_created_count = 0

    # Create organizations
    for i in range(1, org_count + 1):
        name = "DUMMY_ORG%02d" % i
        body = {"name": name}
        result = _api_request(module, "POST", base_url + "/organizations/", auth=auth, headers=headers, verify=validate_certs, json_body=body)
        org_id = result.get("id")
        if org_id is None:
            module.fail_json(msg="Created organization but no id in response: %s" % result)
        org_ids.append(org_id)

    # Create inventories (inventories_per_org per org)
    for oidx, org_id in enumerate(org_ids):
        for j in range(1, inventories_per_org + 1):
            name = "DUMMY_ORG%02d_Inv%02d" % (oidx + 1, j)
            body = {"name": name, "organization": org_id}
            result = _api_request(module, "POST", base_url + "/inventories/", auth=auth, headers=headers, verify=validate_certs, json_body=body)
            inv_id = result.get("id")
            if inv_id is None:
                module.fail_json(msg="Created inventory but no id in response: %s" % result)
            inv_ids.append(inv_id)
            inventory_org_map[inv_id] = org_id

    # Build list of inventory IDs per org (for placing hosts)
    invs_by_org = {}
    for inv_id in inv_ids:
        oid = inventory_org_map[inv_id]
        invs_by_org.setdefault(oid, []).append(inv_id)

    # How many unique logical hosts, and how many should be in multiple orgs
    n_multi = int(round(hosts_count * multi_org_percent / 100.0))
    n_single = hosts_count - n_multi
    # We'll create n_single hosts in one org each, and n_multi "shared" hosts (each in 2+ orgs, possibly different casing)
    num_unique_logical = n_single + n_multi

    base_name = "host"
    # AAP host API expects "variables" as a JSON string
    host_variables = json.dumps({"ansible_connection": "local"})
    org_index_list = list(range(len(org_ids)))
    random.shuffle(org_index_list)

    # Assign each logical host to one or more orgs; then pick an inventory per org and create host with optional casing variant
    created_per_inv = {inv_id: 0 for inv_id in inv_ids}
    logical_index = 0

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
        body = {"name": hostname, "variables": host_variables, "enabled": enabled}
        _api_request(module, "POST", base_url + "/inventories/%s/hosts/" % inv_id, auth=auth, headers=headers, verify=validate_certs, json_body=body)
        hosts_created_count += 1
        host_summary.append({"name": hostname, "inventory_id": inv_id, "organization_id": org_id})
        created_per_inv[inv_id] += 1
        logical_index += 1

    # Multi-org hosts: same logical name in 2+ orgs, optionally different casing per org
    for _ in range(n_multi):
        if logical_index >= num_unique_logical:
            break
        # Pick 2+ orgs for this logical host
        num_orgs_for_host = min(2 + (logical_index % 2), len(org_ids))
        chosen_org_idxs = random.sample(org_index_list, num_orgs_for_host)
        hostname_base_idx = logical_index
        for oidx in chosen_org_idxs:
            org_id = org_ids[oidx]
            inv_id = random.choice(invs_by_org[org_id])
            if allow_same_name_different_casing:
                # Cycle casing per org so same logical host appears as HOST01, host01, Host01
                style = ["upper", "lower", "camel"][oidx % 3]
                hostname = _hostname_variant(base_name, hostname_base_idx, style)
            else:
                hostname = _hostname_variant(base_name, hostname_base_idx, hostname_casing)
            enabled = random.randint(1, 100) > disabled_host_percent
            body = {"name": hostname, "variables": host_variables, "enabled": enabled}
            _api_request(module, "POST", base_url + "/inventories/%s/hosts/" % inv_id, auth=auth, headers=headers, verify=validate_certs, json_body=body)
            hosts_created_count += 1
            host_summary.append({"name": hostname, "inventory_id": inv_id, "organization_id": org_id})
            created_per_inv[inv_id] += 1
        logical_index += 1

    module.exit_json(
        changed=True,
        organizations_created=len(org_ids),
        inventories_created=len(inv_ids),
        hosts_created=hosts_created_count,
        organization_ids=org_ids,
        inventory_ids=inv_ids,
        inventory_org_map=inventory_org_map,
        host_summary=host_summary,
    )


if __name__ == "__main__":
    run_module()
