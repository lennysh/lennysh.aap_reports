==================================
lennysh.aap_reports Release Notes
==================================

.. contents:: Topics

v1.0.0
======

Release Summary
---------------

Initial release of the `lennysh.aap_reports` collection.

Major Changes
-------------

* Initial release of the `lennysh.aap_reports` collection
* Added `node_metrics` module for collecting node and subscription metrics from Ansible Automation Platform Controller
* Added `node_metrics` role for generating reports in multiple formats (markdown, CSV, HTML, JSON, YAML, XML, TXT)

Minor Changes
-------------

* Support for both token-based and username/password authentication
* Automatic API path detection for AAP 2.5+ and 2.4 compatibility
* SSL certificate validation control
* Support for self-signed certificates
* Organization-level metrics reporting
* Node-by-node breakdown with organization membership
* Orphaned node detection and reporting
* GitHub Actions workflow for automated collection building and publishing to Ansible Galaxy
