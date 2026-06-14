---
source_id: NGFW-GLOBALPROTECT-MULTI-GATEWAY
title: GlobalProtect Multiple Gateway Configuration
url: https://docs.paloaltonetworks.com/globalprotect/administration/globalprotect-quick-configs/globalprotect-multiple-gateway-configuration
source_type: official_documentation
product: NGFW
feature: GlobalProtect
version: ""
last_reviewed_date: 2026-05-30
---

# GlobalProtect Multiple Gateway Configuration

## Overview
This configuration adds a second external gateway to enable redundancy and load distribution. Clients attempt connections to all listed gateways, using priority and response time to determine the active gateway.

## Key Requirements
- NGFW or Prisma Access (managed by Panorama or Strata Cloud Manager).
- GlobalProtect Gateway license or Prisma Access with Mobile User subscription.

## Configuration Steps

### Interface and Zone Setup
On the portal/gateway firewall (gw1): configure ethernet1/2 as a Layer 3 interface with IP 198.51.100.42; create a DNS A record mapping 198.51.100.42 to gp1.acme.com; add tunnel.2 to the corp-vpn security zone; enable User Identification on the corp-vpn zone.

On the second gateway firewall (gw2): configure ethernet1/5 as a Layer 3 interface with IP 192.0.2.4; create a DNS A record mapping 192.0.2.4 to gp2.acme.com; add tunnel.1 to the corp-vpn security zone; enable User Identification.

### Licensing
Install a GlobalProtect subscription on each gateway after receiving the activation code.

### Security Policies
Create policy rules enabling traffic between corp-vpn and l3-trust zones for internal resource access.

### Server Certificates
- gp1: use a third-party CA certificate; CN must match gp1.acme.com.
- gp2: a self-signed certificate is acceptable; CN must match gp2.acme.com.

### Authentication
Configure certificate profiles and/or authentication profiles for user authentication to portal and gateways.

### Gateway, Portal, App, and Commit
Configure each gateway with its assigned interface, IP address, server certificate, tunnel interface, and IP pool ranges. Set up portal access and agent configurations supporting multiple gateways. Host app updates on the portal. Commit changes on all firewalls hosting portal and gateways.
