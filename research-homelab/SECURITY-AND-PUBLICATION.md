# Research publication and privacy checklist

This repository is a public, independent undergraduate research record, not a production SOC deployment. No employer or customer data is authorized for publication.

## Before each commit

- [ ] No passwords, API tokens, private keys, connection strings, or cloud credentials.
- [ ] No employer names, hostnames, internal addressing, topology, account names, or logs.
- [ ] No private home IPs, public-facing IPs identifying a private environment, device serial numbers, or MAC addresses.
- [ ] No BCIT student number, private academic correspondence, or local `file://` / home-directory paths.
- [ ] No raw audit/Sysmon/Falco/Wazuh events that could identify users or devices.
- [ ] Sanitize screenshots, PDF metadata, SVG comments, and embedded image text.
- [ ] Publish only minimal, reproducible examples with synthetic data and redacted figures.
- [ ] Label every claim as observed, interpreted, or planned; never imply that a manually built graph is an automated detector.

## Before external sharing

1. Review the **entire repository**, including root-level legacy material and the `main` branch, not just `research-homelab/`.
2. Inspect git history and earlier commits: deleting a secret in the latest commit does not remove it from history.
3. Scan all tracked files and history with a secrets scanner such as Gitleaks, then manually inspect PDFs, images, archives, notebooks, and logs.
4. If a real credential is discovered, revoke/rotate it first; assess history rewrite with care.
5. Check the published concept map for student ID, `file://` paths, document metadata, and research-content integrity before uploading.
6. Verify that every linked file exists on the public branch and that the repository renders correctly without authentication.

**Status:** This checklist is guidance, not a certification that all current or historical commits have passed a comprehensive privacy or secret scan.
