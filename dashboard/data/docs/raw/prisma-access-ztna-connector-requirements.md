---
source_id: PA-ZTNA-CONNECTOR-REQUIREMENTS
title: ZTNA Connector Requirements and Guidelines
url: https://docs.paloaltonetworks.com/prisma-access/administration/ztna-connector-in-prisma-access/ztna-connector-requirements-and-guidelines
source_type: official_documentation
product: Prisma Access
feature: ZTNA Connector
version: "5.0"
last_reviewed_date: 2026-04-28
---

# ZTNA Connector Requirements and Guidelines

## Licensing Requirements
Prisma Access version 5.0 or later is required. The base license includes 10 connectors, 20,000 FQDNs, and 1024 IP subnets. The Private App add-on license provides 200 connectors, 20,000 FQDNs, and 1024 IP subnet functionality.

## Scale and Performance Limits
Each connector supports up to 2 Gbps bandwidth and 100,000 concurrent sessions. A connector group (maximum 4 connectors) handles 6 Gbps aggregate bandwidth and 400,000 concurrent connections. The system supports 20,000 applications per tenant, 1,000 applications per group, 200 connectors per tenant, and 1,024 maximum IP subnets.

## Deployment Platform Requirements
Minimum specifications include 4 vCPUs, 16 GB RAM, and 40 GB disk space. Supported platforms: AWS m5.xlarge, GCP n2-standard-4, Azure Standard_D4_v3, Oracle VM.Standard.E5.Flex, KVM, Hyper-V, and VMware ESXi. VMware deployments prohibit vMotion, snapshots, and migrations; KVM prohibits live migrations and snapshots.

## Network Configuration
Deploy connectors as either one-arm (single interface for all traffic) or two-arm (separate internet and data center interfaces on different subnets). One-arm requires unified security policies; two-arm enables granular access control.

## DNS Requirements
At least one DNS server must resolve public FQDNs (e.g., locator.cgnx.net); another must resolve private application FQDNs. Connectors query all configured DNS servers in parallel, using the first successful response. CNAME records resolving to multiple A records enable automatic load balancing.

## Security Policy Rules
Internet access requires TCP 443 to *.cgnx.net cloud controllers and UDP 500/4500 for IPsec tunnels. Data center access needs UDP/TCP 53 for DNS and protocols matching application requirements. Disable SSL decryption on connector-to-controller connections.

## Additional Constraints
Maximum UDP payload: 1,300 bytes to prevent fragmentation. No single FQDN/wildcard associates with more than four connectors per region. Source NAT occurs for all user traffic. IPv6 connectivity to controller FQDNs is unsupported.
