---
source_id: PA-REMOTE-NETWORKS-ONBOARD
title: Onboard a Remote Network
url: https://docs.paloaltonetworks.com/prisma-access/administration/prisma-access-remote-networks/onboard-a-remote-network
source_type: official_documentation
product: Prisma Access
feature: Remote Networks
version: ""
last_reviewed_date: 2026-02-10
---

# Onboard a Remote Network

This documentation covers procedures for onboarding remote networks to Prisma Access, with separate workflows for Strata Cloud Manager and Panorama management platforms.

## Key Requirements
- Prisma Access license
- Bandwidth pre-allocated to deployment locations
- IPSec-capable device at the remote network location
- BGP or static routing capability, depending on the configuration choice

## Configuration Steps (Strata Cloud Manager)
Launch the Prisma Access management interface and verify bandwidth allocation to the target location. Navigate to Configuration > NGFW and Prisma Access > Remote Networks, provide a descriptive site name, and select the Prisma Access location. Select the IPSec termination node for the location association.

## Routing Options
Static routing requires manual entry of the IP subnets and addresses needed at the branch location. Changes to HQ or data center networks require manual updates. Dynamic routing via BGP requires enabling the feature and configuring peer details including the autonomous system number, peer IP address, and an optional local IP address for BGP peering.

## Limits and Constraints
A maximum of 250 local BGP IP addresses is supported per remote network. This translates to 250 remote networks with a primary tunnel only, 125 networks using ECMP with 2 links, or 62 networks using ECMP with 4 links. The MRAI timer configuration range is 1 to 600 seconds, with a default of 30 seconds. ECMP load balancing requires BGP and supports up to 4 tunnels. Tunnel monitoring requires a static route configuration on customer premises equipment to the monitoring IP address.
