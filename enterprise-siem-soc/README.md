# Enterprise SIEM-SOC — Production Deployment Documentation

This repository documents a complete, reproducible build of an in-house SIEM/SOC
platform: **Wazuh** (SIEM/HIDS/FIM), **Falco** (container/host runtime security),
**Grafana + Loki + InfluxDB** (visualization and log aggregation), **Palo Alto** and
**UniFi** network telemetry, **Microsoft 365 / Entra ID / Defender** identity and
endpoint telemetry, and a custom **SOC Notification Engine** that turns raw alerts
into MITRE ATT&CK-enriched analyst emails.

It was first built and validated as a single-site lab (1 bare-metal Linux host,
1 Linux VM, ~10 onboarded endpoints) and is now being scaled to a company-wide
production deployment. This documentation is written so that **an engineer with no
prior context can rebuild the environment end-to-end**, part by part, and so that the
lab-to-production upgrade path is explicit at every step.

## How to use this repository

1. Read `docs/00-project-overview` and `docs/01-architecture` first — they explain
   *what* you're building and *why* it's shaped this way.
2. Follow `docs/02` through `docs/09` in order. Each part is self-contained but
   assumes the previous parts are done. Every part starts with **Prerequisites** and
   ends with **Validation** — do not move to the next part until validation passes.
3. `docs/12-production-scaling` is the delta between the lab build and a
   production-grade rollout (sizing, HA, hardening, change control). Read it *before*
   you start if you are building for production directly rather than replaying the
   lab.
4. `docs/10-troubleshooting` and `docs/11-testing-validation` are reference material —
   come back to them when something breaks or when you need a repeatable test.
5. `rules/`, `configs/`, `dashboards/`, `queries/`, and `scripts/` hold the actual
   artifacts (Wazuh rules, Grafana dashboard JSON, PowerShell/Bash scripts) referenced
   by the docs. Copy them, don't retype them.

## Repository map

```
enterprise-siem-soc/
├── README.md                          ← you are here
├── docs/
│   ├── 00-project-overview/           What this platform does and doesn't do
│   ├── 01-architecture/               Full data-flow architecture + component list
│   ├── 02-infrastructure-preparation/ Base OS, Docker, storage, backups
│   ├── 03-wazuh-core/                 Wazuh manager/indexer/dashboard + custom rules
│   ├── 04-windows-endpoints/          Agent, Sysmon, Defender, FIM, USB, Intune
│   ├── 05-linux-containers-falco/     Falco + Falcosidekick on the Docker host
│   ├── 06-grafana/                    Loki/Promtail, InfluxDB, dashboards, alerting
│   ├── 07-network-security/           Palo Alto + UniFi telemetry
│   ├── 08-microsoft-security/         Entra ID, Defender for Endpoint, M365 (Graph)
│   ├── 09-alerting-framework/         SOC Notification Engine (MITRE-enriched email)
│   ├── 10-troubleshooting/            Symptom → cause → fix, indexed by component
│   ├── 11-testing-validation/         Repeatable test-case catalogue (TC-001…)
│   ├── 12-production-scaling/         Lab → production delta: sizing, HA, hardening
│   ├── 13-incident-response/          IR workflow + case-study template
│   └── 14-decisions/                  Architecture Decision Records (ADRs)
├── configs/        Sanitized, working configuration files, by component
├── rules/          Wazuh custom rules (local_rules.xml fragments), catalogued
├── dashboards/     Grafana dashboard exports (JSON)
├── queries/        Wazuh/Grafana/Loki queries used for investigation
├── scripts/        PowerShell (Windows) and Bash (Linux) automation
└── examples/       Sanitized real alert/incident examples
```

## Architecture at a glance

```
 ENDPOINTS                              NETWORK                     CLOUD/IDENTITY
 Windows (Sysmon, FIM,        Palo Alto Firewall (syslog)      Microsoft 365 / Entra ID
 Defender, USB, PowerShell)   UniFi (CEF syslog)                Defender for Endpoint
 Linux hosts + Docker/Falco                                     (via Graph API)
        │                          │                                   │
        ▼                          ▼                                   ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                            WAZUH MANAGER                               │
 │   agents · decoders · rules · rule correlation · compliance mapping    │
 └───────────────┬───────────────────────────────────┬────────────────────┘
                 ▼                                   ▼
         Wazuh Indexer (OpenSearch)            Wazuh API
                 │                                   │
                 └───────────────┬───────────────────┘
                                  ▼
                          Grafana (+ Loki for
                        Palo Alto/UniFi syslog,
                         InfluxDB for metrics)
                                  │
                                  ▼
                       SOC Dashboards (5 max)
                                  │
                                  ▼
                     Grafana Alerting → Contact Point
                                  │
                                  ▼
                    SOC Notification Engine (Flask)
                     MITRE mapping · runbook lookup
                                  │
                                  ▼
                        Analyst / Management Email
```

## Current project status

| Layer | Status |
|---|---|
| Infrastructure (Docker, Grafana, InfluxDB, backups) | ✅ Complete |
| Wazuh core (manager, indexer, agents, custom rules) | ✅ Complete |
| Windows endpoint telemetry (Sysmon, FIM, USB, Defender) | ✅ Complete |
| Falco / container runtime security | ✅ Complete |
| Grafana SOC dashboards (5-dashboard model) | ✅ Complete |
| Palo Alto firewall integration | ⏳ In progress |
| UniFi wireless telemetry | ⏳ Planned |
| Microsoft 365 / Entra ID / Defender (Graph) | ⏳ In progress |
| SOC Notification Engine (MITRE-enriched email) | ✅ Complete, hardening in progress |
| Production scaling (HA, sizing, change control) | ⏳ This repository's current focus |

## Conventions used throughout

- Every configuration value that is site-specific is written as `<PLACEHOLDER>` —
  see `docs/01-architecture/03-naming-and-placeholders.md` for the full list and
  fill in your own inventory before you start.
- Every procedure that changes a production system is tagged with a status badge:
  `STATUS: Lab/Test only`, `STATUS: Production-safe`, `STATUS: Requires change
  control`, or `STATUS: Potentially disruptive`.
- Commands are given exactly as run; PowerShell blocks are single-paste blocks
  deliberately (fewer chances to fat-finger a change in a live environment).
- Every "Part" ends with a **Validation** section. Do not proceed until it passes.
