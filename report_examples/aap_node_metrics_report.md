# Ansible Automation Platform Node Metrics Report

**AAP Instance:** https://aap.example.com  
**Generated:** 2026-01-21 21:46:54 UTC

## Organization Node and Subscription Metrics

| Organization | Max Nodes | Unique Nodes | Shared Nodes | Unique Subscriptions | Shared Subscriptions |
|--------------|-----------|--------------|--------------|-----------------|-----------------|
| Default | 20 | 4 (44.4%) | 1 (100.0%) | 3 (37.5%) | 1 (100.0%) |
| DEMOLab | Unlimited | 4 (44.4%) | 1 (100.0%) | 4 (50.0%) | 1 (100.0%) |
| Orphaned Nodes (No Organization) |  | 1 (11.1%) |  | 1 (12.5%) |  |
| **TOTAL** |  | 9 | 1 | 8 | 1 |

## Node Details by Organization

Shows all nodes with their subscription consumption status (green ✓ = consuming subscription, red ✗ = not consuming) and organization membership (green ✓ = member, red ✗ = not a member).

| Node | Subscription | Organizations |
|------|---------|--------------|
| db | <span style="color: green;">✓</span> | DEMOLab |
| en | <span style="color: green;">✓</span> | DEMOLab |
| gw | <span style="color: green;">✓</span> | DEMOLab |
| localhost | <span style="color: green;">✓</span> | DEMOLab |
| rhel-demo-01 | <span style="color: green;">✓</span> | Default |
| rhel-demo-02 | <span style="color: green;">✓</span> | Default |
| rhel-demo-03 | <span style="color: green;">✓</span> | Default |
| windows2025-demo | <span style="color: green;">✓</span> | Default, DEMOLab |
| windows2025-demo-02 | <span style="color: red;">✗</span> | Default |
| windows2025-test | <span style="color: green;">✓</span> | None |

## Notes

- **Unique Nodes**: Nodes that exist only in this organization
- **Shared Nodes**: Nodes that exist in multiple organizations
- **Unique Subscriptions**: Subscription-consuming nodes (from node_metrics) that exist only in this organization
- **Shared Subscriptions**: Subscription-consuming nodes (from node_metrics) that exist in multiple organizations
