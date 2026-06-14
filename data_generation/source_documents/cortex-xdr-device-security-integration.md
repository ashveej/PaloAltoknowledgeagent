---
source_id: XDR-DEVICE-SECURITY-INTEGRATION
title: Integrate Device Security with Cortex XDR
url: https://docs.paloaltonetworks.com/iot/integration/endpoint-protection/integrate-iot-security-with-cortex-xdr
source_type: official_documentation
product: Cortex XDR
feature: Integrations
version: ""
last_reviewed_date: 2026-05-08
---

# Integrate Device Security with Cortex XDR

## Overview
Device Security integrates with Cortex XDR, a detection and response app that integrates endpoint, network, and cloud data to detect threats. The integration enables Device Security to import device attributes from XDR endpoints.

## Integration Methods
- Direct API Integration — requires no Cortex XSOAR instance.
- XSOAR-Based Integration — requires either a full-featured Cortex XSOAR server or a free cohosted instance.

## Data Imported
Device Security can import endpoint attributes including EDR isolation and operational status, EDR group name, OS type and version, MAC address, IP address, domain, and username.

The XSOAR integration additionally supports importing:
- Application inventory (installed applications).
- KB articles (Windows patches; automatically marks vulnerabilities as resolved when patches are detected).
- CVEs identified on endpoints.

If there is a conflict between Device Security and XDR about the OS type and version of a device, Device Security defers to the information from XDR.

## Requirements
- A Device Security subscription (Enterprise Plus, Industrial OT, Medical, or X tier).
- For XQL data options: a Cortex XDR Pro license, an Instance Administrator API key, and available XQL quota.
