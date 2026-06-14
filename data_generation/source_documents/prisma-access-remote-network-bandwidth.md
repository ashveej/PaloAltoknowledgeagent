---
source_id: PA-REMOTE-NETWORK-BANDWIDTH
title: Allocate Remote Network Bandwidth
url: https://docs.paloaltonetworks.com/prisma-access/administration/prisma-access-remote-networks/allocate-remote-network-bandwidth
source_type: official_documentation
product: Prisma Access
feature: Remote Networks
version: ""
last_reviewed_date: 2026-05-20
---

# Allocate Remote Network Bandwidth

## Core Concept
Bandwidth is allocated at the compute location level rather than per individual site. Prisma Access dynamically distributes allocated bandwidth among sites based on load and demand within each compute location. This applies only to deployments using the aggregate bandwidth model (Prisma Access 6.0+).

## Key Requirements
- Minimum bandwidth: 50 Mbps per compute location.
- Maximum bandwidth: limited by remaining licensed bandwidth.

## How It Works
Multiple geographically proximate Prisma Access locations are grouped into compute locations. For example, Singapore, Thailand, and Vietnam locations map to the Asia Southeast compute location. If 200 Mbps is allocated to this location, Prisma Access automatically divides that bandwidth among onboarded branch offices, reallocating dynamically as needed.

## Configuration Steps (Panorama)
1. Navigate to Panorama > Cloud Services > Configuration > Remote Networks.
2. Click the gear icon in the Bandwidth Allocation area.
3. Enter bandwidth allocation for each compute location.
4. Confirm with the checkmark; cancel with the x.
5. Wait for allocation to reflect in the Allocated Total field.
6. Click OK.

## Important Limitations
- Secure inbound access for remote network sites and Quality of Service (QoS) for remote networks is not supported when you allocate bandwidth across locations.
- Remote network names cannot be changed after initial entry.
