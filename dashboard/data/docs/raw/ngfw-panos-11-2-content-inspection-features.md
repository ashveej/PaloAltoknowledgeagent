---
source_id: NGFW-PANOS-11-2-CONTENT-RN
title: Content Inspection Features Introduced in PAN-OS 11.2
url: https://docs.paloaltonetworks.com/pan-os/11-2/pan-os-release-notes/features-introduced-in-pan-os/content-inspection-features
source_type: release_notes
product: NGFW
feature: Content Inspection (Release Notes)
version: "11.2"
last_reviewed_date: 2026-04-12
---

# Content Inspection Features in PAN-OS 11.2

## Regional Service Domain Control for Advanced DNS Security
Introduced in PAN-OS 11.2.9 (September 2025). Allows users to specify preferred regional FQDN settings. Both DNS Security and Advanced DNS Security traffic (requests and responses) are now consistently routed to the default (or user-defined) regional service domain, creating unified routing for enhanced control over regional security infrastructure.

## Brotli Decompression Support
Added in PAN-OS 11.2.4 (November 2024). The Content-Based Threat Detection engine now decompresses Brotli-encoded content. Attackers use this Google-developed compression format to evade detection. The enhancement allows Advanced Threat Prevention, Advanced WildFire, and Advanced URL Filtering to inspect previously unsupported content types.

## Advanced DNS Security Service
Launched in PAN-OS 11.2 (May 2024). A subscription service that detects DNS hijacking and misconfiguration in real-time using cloud-based detection engines, analyzing DNS responses with ML-based analytics. Supports two initial analysis engines: DNS Misconfiguration Domains and Hijacking Domains. Requires active Advanced DNS Security and Advanced Threat Prevention licenses.

## Local Deep Learning for Advanced Threat Prevention
Released in PAN-OS 11.2 (May 2024). Provides local, deep learning-based analysis for zero-day threats without cloud latency. The module processes suspicious content locally using detection engines from the Advanced Threat Prevention cloud service, enabling fast local analysis while handling high threat volumes efficiently.
