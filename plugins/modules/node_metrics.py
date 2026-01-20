#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Lenny Shirley
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: node_metrics
short_description: Collect node metrics data from Ansible Automation Platform Controller
version_added: "1.0.0"
description:
    - This module connects to the AAP Controller API and collects organization-level node and subscription metrics.
    - Returns structured JSON data that can be used with Ansible templates to generate custom reports.
    - Automatically detects the correct API path (AAP 2.5+ uses /api/controller/v2/, AAP 2.4 and below use /api/v2/).
options:
    url:
        description:
            - AAP Controller base URL (required)
        required: true
        type: str
    token:
        description:
            - API token for authentication (optional if username/password provided)
        required: false
        type: str
    username:
        description:
            - Username for authentication (optional if token provided)
        required: false
        type: str
    password:
        description:
            - Password for authentication (optional if token provided)
        required: false
        type: str
    validate_certs:
        description:
            - Whether to validate SSL certificates
            - Set to C(false) to allow self-signed certificates
        required: false
        type: bool
        default: true
author:
    - Lenny Shirley
'''

EXAMPLES = r'''
# Collect node metrics data using token
- name: Collect node metrics data
  lennysh.aap_reports.node_metrics:
    url: https://aap.example.com
    token: "{{ aap_token }}"
  register: metrics_data

# Collect node metrics data using username/password
- name: Collect node metrics data
  lennysh.aap_reports.node_metrics:
    url: https://aap.example.com
    username: admin
    password: "{{ aap_password }}"
  register: metrics_data

# Collect node metrics data with self-signed certificate
- name: Collect node metrics data (self-signed cert)
  lennysh.aap_reports.node_metrics:
    url: https://aap.example.com
    token: "{{ aap_token }}"
    validate_certs: false
  register: metrics_data

# Generate markdown report using template
- name: Generate markdown report
  ansible.builtin.template:
    src: aap_node_metrics_report.md.j2
    dest: /tmp/aap_report.md
  vars:
    metrics: "{{ metrics_data.metrics }}"
'''

RETURN = r'''
organizations_count:
    description: Number of organizations processed
    returned: always
    type: int
    sample: 3
nodes_count:
    description: Total number of nodes found
    returned: always
    type: int
    sample: 10
metrics:
    description: Structured metrics data for generating reports
    returned: always
    type: dict
    contains:
        generated_at:
            description: Timestamp when data was collected
            type: str
            sample: "2026-01-19 20:00:00 UTC"
        aap_url:
            description: AAP Controller URL from which data was collected
            type: str
            sample: "https://aap.example.com"
        organizations:
            description: List of organization metrics
            type: list
            elements: dict
            contains:
                id:
                    description: Organization ID
                    type: int
                name:
                    description: Organization name
                    type: str
                total_nodes:
                    description: Total number of nodes in organization
                    type: int
                unique_nodes:
                    description: Nodes unique to this organization
                    type: int
                shared_nodes:
                    description: Nodes shared across multiple organizations
                    type: int
                unique_licenses:
                    description: Subscription-consuming nodes unique to this organization
                    type: int
                shared_licenses:
                    description: Subscription-consuming nodes shared across organizations
                    type: int
                total_nodes_pct:
                    description: Percentage of total nodes
                    type: float
                unique_nodes_pct:
                    description: Percentage of unique nodes
                    type: float
                shared_nodes_pct:
                    description: Percentage of shared nodes
                    type: float
                unique_licenses_pct:
                    description: Percentage of unique subscriptions
                    type: float
                shared_licenses_pct:
                    description: Percentage of shared subscriptions
                    type: float
        totals:
            description: Aggregate totals across all organizations
            type: dict
            contains:
                total_nodes:
                    description: Total nodes across all organizations
                    type: int
                unique_nodes:
                    description: Total unique nodes
                    type: int
                shared_nodes:
                    description: Total shared nodes
                    type: int
                unique_licenses:
                    description: Total unique subscriptions
                    type: int
                shared_licenses:
                    description: Total shared subscriptions
                    type: int
        nodes:
            description: Node details with organization membership
            type: list
            elements: dict
            contains:
                nodename:
                    description: Node name
                    type: str
                license:
                    description: Whether node consumes a subscription
                    type: bool
                organizations:
                    description: List of organization IDs this node belongs to
                    type: list
                    elements: int
        organization_names:
            description: Mapping of organization ID to name
            type: dict
    sample: {
        "generated_at": "2026-01-19 20:00:00 UTC",
        "organizations": [...],
        "totals": {...},
        "nodes": [...],
        "organization_names": {...}
    }
'''

from datetime import datetime
from ansible.module_utils.basic import AnsibleModule

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def detect_api_path(module, url, auth=None, headers=None, verify=True):
    """Detect the correct API path by trying both 2.5+ and 2.4 paths.

    Args:
        module: Ansible module instance
        url: Base URL
        auth: Tuple of (username, password) for basic auth, or None
        headers: Dict of headers for token auth, or None
        verify: Whether to verify SSL certificates
    """
    # Try 2.5+ path first (/api/controller/v2/)
    test_endpoint = "/api/controller/v2/organizations/?page=1&page_size=1"
    try:
        if auth:
            response = requests.get(f"{url}{test_endpoint}", auth=auth, verify=verify, timeout=10)
        else:
            response = requests.get(f"{url}{test_endpoint}", headers=headers, verify=verify, timeout=10)
        if response.status_code == 200:
            return "/api/controller/v2"
    except Exception:
        pass

    # Fall back to 2.4 path (/api/v2/)
    test_endpoint = "/api/v2/organizations/?page=1&page_size=1"
    try:
        if auth:
            response = requests.get(f"{url}{test_endpoint}", auth=auth, verify=verify, timeout=10)
        else:
            response = requests.get(f"{url}{test_endpoint}", headers=headers, verify=verify, timeout=10)
        if response.status_code == 200:
            return "/api/v2"
    except Exception:
        pass

    # If both fail, default to 2.5+ path and let the actual call fail with a better error
    return "/api/controller/v2"


def get_all_pages(module, url, endpoint, api_base_path, auth=None, headers=None, verify=True):
    """Fetch all pages from a paginated API endpoint.

    Args:
        module: Ansible module instance
        url: Base URL
        endpoint: API endpoint path (e.g., "/organizations/")
        api_base_path: Base API path (e.g., "/api/controller/v2" or "/api/v2")
        auth: Tuple of (username, password) for basic auth, or None
        headers: Dict of headers for token auth, or None
        verify: Whether to verify SSL certificates
    """
    all_results = []
    page = 1

    while True:
        page_url = f"{url}{api_base_path}{endpoint}?page={page}&page_size=200"

        try:
            if auth:
                response = requests.get(page_url, auth=auth, verify=verify, timeout=30)
            else:
                response = requests.get(page_url, headers=headers, verify=verify, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            module.fail_json(msg=f"Failed to fetch {endpoint} page {page}: {str(e)}")

        if not data.get('results'):
            break

        all_results.extend(data['results'])

        if not data.get('next'):
            break

        page += 1

    return all_results


def calculate_percentage(value, total):
    """Calculate percentage."""
    if total == 0:
        return 0.0
    return round((value / total) * 100, 1)


def run_module():
    """Main module execution."""
    module_args = dict(
        url=dict(type='str', required=True),
        token=dict(type='str', required=False, no_log=True),
        username=dict(type='str', required=False),
        password=dict(type='str', required=False, no_log=True),
        validate_certs=dict(type='bool', required=False, default=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[['token', 'username']],
        required_together=[['username', 'password']],
        supports_check_mode=False
    )

    if not HAS_REQUESTS:
        module.fail_json(msg='The requests library is required for this module. Install it with: pip install requests')

    url = module.params['url'].rstrip('/')
    token = module.params.get('token')
    username = module.params.get('username')
    password = module.params.get('password')
    validate_certs = module.params.get('validate_certs', True)

    try:
        # Determine authentication method and detect API path
        # Prefer token if provided, otherwise use username/password
        auth = None
        headers = None
        api_base_path = None

        if token:
            # Use token authentication (preferred)
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            api_base_path = detect_api_path(module, url, headers=headers, verify=validate_certs)
        elif username and password:
            # Use basic authentication
            auth = (username, password)
            api_base_path = detect_api_path(module, url, auth=auth, verify=validate_certs)
        else:
            # This shouldn't happen due to required_one_of validation, but just in case
            module.fail_json(msg="Either token or username/password must be provided")

        # Fetch organizations
        organizations = get_all_pages(module, url, "/organizations/", api_base_path, auth=auth, headers=headers, verify=validate_certs)

        # Fetch host metrics
        host_metrics = get_all_pages(module, url, "/host_metrics/", api_base_path, auth=auth, headers=headers, verify=validate_certs)

        # Fetch inventories
        inventories = get_all_pages(module, url, "/inventories/", api_base_path, auth=auth, headers=headers, verify=validate_certs)

        # Build data structures
        org_id_to_name = {org['id']: org['name'] for org in organizations}
        inventory_org_map = {inv['id']: inv['organization'] for inv in inventories}

        # Fetch nodes for each inventory
        inventory_nodes = {}
        for inv in inventories:
            inv_id = inv['id']
            nodes = get_all_pages(module, url, f"/inventories/{inv_id}/hosts/", api_base_path, auth=auth, headers=headers, verify=validate_certs)
            for node in nodes:
                nodename = node.get('name')
                if nodename:
                    inventory_nodes[f"{inv_id}:{nodename}"] = True

        # Map nodes to organizations (convert all nodenames to lowercase)
        org_nodes_set = {}
        node_to_orgs_set = {}

        for key in inventory_nodes.keys():
            inv_id, nodename = key.split(':', 1)
            org_id = inventory_org_map.get(int(inv_id))

            if org_id:
                # Convert to lowercase for everything
                nodename_lower = nodename.lower()

                if org_id not in org_nodes_set:
                    org_nodes_set[org_id] = set()
                org_nodes_set[org_id].add(nodename_lower)

                if nodename_lower not in node_to_orgs_set:
                    node_to_orgs_set[nodename_lower] = set()
                node_to_orgs_set[nodename_lower].add(org_id)

        # Map subscription-consuming nodes (convert to lowercase)
        # Only nodes with deleted=False are currently consuming subscriptions
        # deleted=True means the node is NOT consuming a subscription/seat
        license_nodes_set = {}
        for metric in host_metrics:
            nodename = metric.get('hostname')
            deleted = metric.get('deleted', False)
            if nodename and not deleted:
                nodename_lower = nodename.lower()
                license_nodes_set[nodename_lower] = True

        org_license_nodes_set = {}
        for nodename_lower in license_nodes_set.keys():
            if nodename_lower in node_to_orgs_set:
                for org_id in node_to_orgs_set[nodename_lower]:
                    if org_id not in org_license_nodes_set:
                        org_license_nodes_set[org_id] = set()
                    org_license_nodes_set[org_id].add(nodename_lower)

        # Calculate organization metrics
        org_list = []
        totals = {
            'total_nodes': 0,
            'unique_nodes': 0,
            'shared_nodes': 0,
            'unique_licenses': 0,
            'shared_licenses': 0
        }

        # First pass: collect data and calculate totals
        for org in organizations:
            org_id = org['id']
            org_name = org['name']

            # Count nodes
            total_nodes = len(org_nodes_set.get(org_id, set()))
            unique_nodes = 0
            shared_nodes = 0

            for nodename in org_nodes_set.get(org_id, set()):
                if len(node_to_orgs_set.get(nodename, set())) > 1:
                    shared_nodes += 1
                else:
                    unique_nodes += 1

            # Count licenses
            unique_licenses = 0
            shared_licenses = 0

            for nodename in org_license_nodes_set.get(org_id, set()):
                if len(node_to_orgs_set.get(nodename, set())) > 1:
                    shared_licenses += 1
                else:
                    unique_licenses += 1

            totals['total_nodes'] += total_nodes
            totals['unique_nodes'] += unique_nodes
            # Don't sum shared_nodes here - we'll count unique shared nodes directly
            totals['unique_licenses'] += unique_licenses
            # Don't sum shared_licenses here - we'll count unique shared licenses directly

            # Store org data (percentages calculated in second pass)
            org_list.append({
                'id': org_id,
                'name': org_name,
                'total_nodes': total_nodes,
                'unique_nodes': unique_nodes,
                'shared_nodes': shared_nodes,
                'unique_licenses': unique_licenses,
                'shared_licenses': shared_licenses
            })

        # Count orphaned subscription-consuming nodes (consuming subscription but not in any inventory/org)
        orphaned_license_nodes = []
        for nodename_lower in license_nodes_set.keys():
            if nodename_lower not in node_to_orgs_set:
                orphaned_license_nodes.append(nodename_lower)

        orphaned_licenses_count = len(orphaned_license_nodes)
        if orphaned_licenses_count > 0:
            # Add orphaned nodes entry to org_list
            # Unique nodes count matches unique licenses (they're the same nodes)
            org_list.append({
                'id': None,  # No organization ID for orphaned nodes
                'name': 'Orphaned Nodes (No Organization)',
                'total_nodes': 0,  # Not in any inventory
                'unique_nodes': orphaned_licenses_count,  # Match unique licenses count
                'shared_nodes': None,  # Empty/blank for orphaned nodes
                'unique_licenses': orphaned_licenses_count,
                'shared_licenses': None  # Empty/blank for orphaned nodes
            })
            totals['unique_nodes'] += orphaned_licenses_count
            totals['unique_licenses'] += orphaned_licenses_count

        # Count unique shared nodes and licenses directly (not summing from orgs to avoid double-counting)
        # A shared node is one that appears in more than one organization
        for nodename_lower in node_to_orgs_set.keys():
            if len(node_to_orgs_set[nodename_lower]) > 1:
                totals['shared_nodes'] += 1

        # A shared subscription is a subscription-consuming node that appears in more than one organization
        for nodename_lower in license_nodes_set.keys():
            if nodename_lower in node_to_orgs_set and len(node_to_orgs_set[nodename_lower]) > 1:
                totals['shared_licenses'] += 1

        # Second pass: calculate percentages now that totals are known
        for org_entry in org_list:
            org_entry['total_nodes_pct'] = calculate_percentage(org_entry['total_nodes'], totals['total_nodes'])
            org_entry['unique_nodes_pct'] = calculate_percentage(org_entry['unique_nodes'], totals['unique_nodes'])
            # Handle None values for shared_nodes/shared_licenses (orphaned nodes)
            if org_entry['shared_nodes'] is not None:
                org_entry['shared_nodes_pct'] = calculate_percentage(org_entry['shared_nodes'], totals['shared_nodes'])
            else:
                org_entry['shared_nodes_pct'] = None
            org_entry['unique_licenses_pct'] = calculate_percentage(org_entry['unique_licenses'], totals['unique_licenses'])
            if org_entry['shared_licenses'] is not None:
                org_entry['shared_licenses_pct'] = calculate_percentage(org_entry['shared_licenses'], totals['shared_licenses'])
            else:
                org_entry['shared_licenses_pct'] = None

        # Add TOTAL row at the end (no percentages for totals row)
        org_list.append({
            'id': -1,  # Special ID for totals row
            'name': 'TOTAL',
            'total_nodes': totals['total_nodes'],
            'unique_nodes': totals['unique_nodes'],
            'shared_nodes': totals['shared_nodes'],
            'unique_licenses': totals['unique_licenses'],
            'shared_licenses': totals['shared_licenses'],
            'total_nodes_pct': 0.0,  # No percentage for totals row
            'unique_nodes_pct': 0.0,
            'shared_nodes_pct': 0.0,
            'unique_licenses_pct': 0.0,
            'shared_licenses_pct': 0.0
        })

        # Build node data (convert sets to lists for JSON serialization)
        # All nodenames are lowercase
        # Include all nodes from inventories, plus any subscription-consuming nodes not in inventories
        all_nodes_set = set(node_to_orgs_set.keys()) | set(license_nodes_set.keys())
        nodes_list = []
        for nodename_lower in sorted(all_nodes_set):
            # Ensure organization IDs are integers
            if nodename_lower in node_to_orgs_set:
                org_ids = [int(org_id) for org_id in node_to_orgs_set[nodename_lower]]
            else:
                # Node not in any inventory (orphaned but still consuming subscription)
                org_ids = []
            nodes_list.append({
                'nodename': nodename_lower,
                'license': nodename_lower in license_nodes_set,
                'organizations': sorted(org_ids)
            })

        # Build metrics data structure
        metrics = {
            'generated_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'aap_url': url,
            'organizations': org_list,
            'totals': totals,
            'nodes': nodes_list,
            'organization_names': org_id_to_name
        }

        module.exit_json(
            changed=True,
            organizations_count=len(organizations),
            nodes_count=len(nodes_list),
            metrics=metrics
        )

    except Exception as e:
        module.fail_json(msg=f"Error generating report: {str(e)}")


if __name__ == '__main__':
    run_module()
