---
source_id: PA-SERVICE-CONNECTION-ROUTING
title: Dynamic Routing Considerations for Service Connections
url: https://docs.paloaltonetworks.com/prisma-access/administration/prisma-access-service-connections/routing-for-service-connection-traffic
source_type: official_documentation
product: Prisma Access
feature: Service Connections / BGP Routing
version: ""
last_reviewed_date: 2026-05-11
---

# Dynamic Routing Considerations for Service Connections

## Overview
Prisma Access employs BGP for dynamic routing and path selection to direct service connection traffic to headquarters or data centers. The platform offers flexibility beyond its default routing model to accommodate diverse network topologies.

## Routing Modes Available
- Default Routing: Prisma Access applies BGP best path-selection mechanisms without adjusting any of the BGP attributes and honors CPE-advertised attributes. Mobile user routes are divided into /24 blocks before advertisement and include BGP community values for differentiation across regions.
- Hot Potato Routing: enables Prisma Access to egress traffic bound to service connections/data centers from its internal network as quickly as possible, shifting routing decisions to your organization's network.

## Key BGP Behaviors
- Prisma Access assigns AS number 65534 to route advertisements.
- Regional mobile user pools receive different IP blocks: 192.168.64.0/20 (Asia/Australia/Japan), 192.168.72.0/20 (Africa/Europe/Middle East), 192.168.48.0/20 (North/South America).
- AS-PATH prepending in hot potato mode ranges from 0 to 7 additional prepends depending on tunnel type and backup configuration.

## Important Considerations
Route summarization can cause asymmetric routing with default routing. For deployments using route aggregation with Mobile Users, hot potato routing with configured backup service connections is recommended to ensure deterministic behavior. When deploying new closer service connections, existing farther connections may experience routing issues requiring location adjustment.
