---
source_id: XDR-DATA-CENTER-ENDPOINTS
title: Use Cortex XDR Agent to Protect Data Center Endpoints
url: https://docs.paloaltonetworks.com/best-practices/10-2/data-center-best-practices/data-center-best-practice-security-policy/use-traps-to-protect-data-center-endpoints
source_type: official_documentation
product: Cortex XDR
feature: Endpoint Protection
version: ""
last_reviewed_date: 2025-04-22
---

# Use Cortex XDR Agent to Protect Data Center Endpoints

## Overview
The Cortex XDR Agent provides endpoint-level threat prevention that complements firewall protections. Cortex XDR Agent protects data center endpoints such as servers and VMs against malware and exploits on the endpoint itself.

## Protection Capabilities
- Threat Detection: the agent identifies threats within executables, document macros, dynamic-link library files, and similar executable formats on individual systems.
- Layered Defense: the firewall guards against network-based threats reaching endpoints, while the agent monitors and blocks threats already resident on endpoints. When malware or exploits are already on an endpoint or get onto an endpoint, and the endpoint executes the threat, the firewall does not see the threat — the agent does.
- Scope of Protection: Cortex XDR Agent operates independently from firewall policies. It governs endpoint-level security events, while firewall policies control network traffic traversal, ensuring no policy conflicts between the two systems.

## Deployment Guidance
Install the Cortex XDR Agent on all data center endpoints. Deployment best practices remain consistent across network locations; malware protection policies apply uniformly whether endpoints exist in data centers or other network segments.
