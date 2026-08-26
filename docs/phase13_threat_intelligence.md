# Phase 13 — Threat Intelligence Integration

## Architecture

The Threat Intelligence Service (`app/services/threat_intelligence_service.py`) provides IOC enrichment through a pluggable feed loader designed for future API integrations (AbuseIPDB, AlienVault OTX, ThreatFox, VirusTotal).

```
Log Event → enrich_ioc(ip, location) → Threat Feed Lookup → Context + Severity
```

## Feed Sources

| Type | Config | Description |
|------|--------|-------------|
| JSON | `THREAT_FEED_TYPE=json` | Default — `sample_data/threat_feed.json` |
| CSV | `THREAT_FEED_TYPE=csv` | Columnar feed with ip, threat_score, category, confidence |
| Mock | Fallback | Built-in IOCs when feed load fails |

## Capabilities

1. **IP Reputation Scoring** — 0–100 threat score per IOC
2. **IOC Enrichment** — Lookup by IP or location string
3. **Threat Severity Classification** — CRITICAL / HIGH / MEDIUM / LOW
4. **Threat Context Generation** — Human-readable context strings

## API Endpoints

| Method | Path | Response |
|--------|------|----------|
| GET | `/threat-intel` | Aggregate stats (total_iocs, malicious_ips, suspicious_ips) |
| GET | `/threat-intel/ip/{ip}` | Single IOC lookup with threat_score, category, confidence |

## Dashboard Components

- **ThreatIntelPanel** — Metrics cards, category pie chart, score distribution bar chart

## Use Cases

- Enrich log ingestion with threat context for known malicious IPs
- SOC analyst triage of high-risk geographies (Russia, China mappings)
- Portfolio demonstration of TI pipeline architecture
