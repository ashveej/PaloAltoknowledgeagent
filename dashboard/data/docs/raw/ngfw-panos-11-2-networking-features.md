---
source_id: NGFW-PANOS-11-2-NETWORKING-RN
title: Networking Features Introduced in PAN-OS 11.2
url: https://docs.paloaltonetworks.com/pan-os/11-2/pan-os-release-notes/features-introduced-in-pan-os/networking-features
source_type: release_notes
product: NGFW
feature: Networking (Release Notes)
version: "11.2"
last_reviewed_date: 2026-04-10
---

# Networking Features in PAN-OS 11.2

## HTTP/2 Protocol Support
Introduced in PAN-OS 11.2.8, the management plane now supports HTTP/2 alongside HTTP/1.1, enabling more efficient web communication via multiplexing, header compression, and server push. When manually enabled via CLI, HTTP/1.1 is disabled with no fallback to maintain security compliance.

## Enhanced DoS and Packet Buffer Protection
Starting with PAN-OS 11.2.3, administrators can configure edge zones using both source and destination IP addresses for improved attack mitigation. New capabilities include configurable DoS policies for destination IP-only classification, simultaneous buffer-based and latency-based activation, adjustable software block duration, and SNMP monitoring for buffer utilization.

## IPv6 Support on PA-415-5G Cellular Interface
Introduced in PAN-OS 11.2.3, the PA-415-5G firewall supports dynamic IPv6 addressing on its cellular interface, obtaining a dynamic IPv6 prefix from a cellular provider.

## Encrypted DNS Options
Available since PAN-OS 11.2.1, DNS proxies can accept encrypted communications via DNS-over-HTTP (DoH), DNS-over-TLS (DoT), or cleartext. The management interface also supports encrypted DNS with fallback options.

## Post Quantum Hybrid Key Exchange VPN
Released in PAN-OS 11.2, allows creation of hybrid cryptographic keys using NIST round 3 and 4 suites, supporting up to seven additional key exchange mechanisms to increase quantum resistance.

## PA-3400 Series Rule Expansion
Maximum security rules for PA-3410 and PA-3420 increased from 2,500 to 10,000.

## LSVPN Satellite Authentication
Serial number and IP address-based authentication enables automated satellite deployment without manual intervention.
