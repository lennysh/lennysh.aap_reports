# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-20

### Added
- Initial release of the `lennysh.aap_reports` collection
- `node_metrics` module for collecting node and subscription metrics from Ansible Automation Platform Controller
- `node_metrics` role for generating reports in multiple formats (markdown, CSV, HTML, JSON, YAML, XML, TXT)
- Support for both token-based and username/password authentication
- Automatic API path detection for AAP 2.5+ and 2.4 compatibility
- SSL certificate validation control
- Support for self-signed certificates
- Organization-level metrics reporting
- Node-by-node breakdown with organization membership
- Orphaned node detection and reporting
- GitHub Actions workflow for automated collection building and publishing to Ansible Galaxy
