---
source_id: PA-REMOTE-NETWORKS-HIGH-PERFORMANCE
title: Remote Networks—High Performance
url: https://docs.paloaltonetworks.com/prisma-access/administration/prisma-access-remote-networks/remote-networks-high-performance
source_type: official_documentation
product: Prisma Access
feature: Remote Networks (High Performance)
version: "5.2"
last_reviewed_date: 2025-10-08
---

# Remote Networks—High Performance

## Bandwidth Capabilities
- Up to 3 Gbps aggregate bandwidth per node in a compute region.
- Up to 2 Gbps bandwidth per remote network tunnel from a remote site.
- One Service Endpoint address is allocated for every 3 Gbps of bandwidth.

## Key Requirements
- Minimum Prisma Access version 5.2 Innovation required.
- Internal Gateway support requires version 6.0 minimum.
- New deployments only.
- Minimum CIR of 1 Mbps, maximum 2000 Mbps per site.
- Minimum 50 Mbps bandwidth allocation per compute location.

## Configuration Essentials
Tunnel Modes:
- Active/Passive: one or two circuits with two to four tunnels.
- Active/Active: two to four circuits with four to eight tunnels.

QoS Profile Setup:
- Single QoS Profile per site (no guaranteed bandwidth ratios).
- Up to eight individual QoS classes supported.
- Classes support real-time, high, medium, or low priority.

Routing Options:
- Static or Dynamic (eBGP); supports BGP Private AS numbers per RFC 6996.

## Unsupported Features
IPv6, Multi-Exit Discriminator (MED) attributes, Traffic Replication, and IPSec Serviceability are not supported with high-performance remote networks.
