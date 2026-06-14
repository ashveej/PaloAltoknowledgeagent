---
source_id: NGFW-DECRYPTION-OVERVIEW
title: Decryption Overview
url: https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/decryption/decryption-overview
source_type: official_documentation
product: NGFW
feature: Decryption / SSL
version: "11.1"
last_reviewed_date: 2025-10-15
---

# Decryption Overview

## Overview
Decryption converts encrypted data into a readable format for inspection and visibility into SSL/TLS and SSH traffic. The process allows firewalls to examine both outbound and inbound encrypted communications.

## Three Decryption Types
- SSL Forward Proxy: inspects traffic leaving your internal network toward the internet.
- SSL Inbound Inspection: examines traffic entering internal network servers from external sources.
- SSH Proxy: inspects and controls traffic in SSH tunnels (note: not supported by Strata Cloud Manager).

## How SSL Decryption Works
The NGFW establishes itself as a trusted intermediary using keys and certificates to establish the firewall as a trusted third party between a client and a server. The firewall decrypts SSL/TLS traffic to plaintext, inspects it, then re-encrypts before forwarding, maintaining data privacy.

## Configuration Components
Deploy decryption policies containing one or more policy rules specifying the target traffic for decryption, the decryption type applied, and traffic handling procedures. Associate decryption profiles with rules to define protocol versions, cipher suites, and certificate verification settings.

## Security Considerations
Resource-intensive decryption of all traffic requires balancing inspection needs against performance, compliance, and resource constraints. Selective decryption strategies targeting high-risk URL categories or business-critical traffic optimize deployment efficiency.
