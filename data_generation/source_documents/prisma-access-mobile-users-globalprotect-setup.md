---
source_id: PA-MOBILE-USERS-SETUP
title: Set Up GlobalProtect Mobile Users
url: https://docs.paloaltonetworks.com/prisma-access/administration/prisma-access-mobile-users/mobile-users-globalprotect/set-up-globalprotect-mobile-users
source_type: official_documentation
product: Prisma Access
feature: Mobile Users / GlobalProtect
version: ""
last_reviewed_date: 2026-06-02
---

# Set Up GlobalProtect Mobile Users

## Core Requirements
Before configuration, you need:
- An active Prisma Access license for mobile users.
- Non-overlapping IP address pools for mobile users.
- A portal FQDN (fully qualified domain name).
- A GlobalProtect app deployment strategy.
- Security policy rule information.
- Mobile user geographic location data.

## IP Address Pool Specifications
The minimum subnet requirement is /23 (512 IP addresses) per location. For worldwide deployments, allocate pools equal to or exceeding the licensed mobile user count for simultaneous logins.

Reserved IP ranges (do not use): 169.254.0.0/16 and 100.64.0.0/10. RFC 1918-compliant addresses are recommended, though non-RFC 1918 public addresses are supported.

## Portal Configuration Options
- Default Domain: uses `.gpcloudservice.com` with automatic certificate and DNS publishing.
- Custom Domain: requires obtaining certificates, creating DNS CNAME entries mapping the default portal address to the custom portal address, and importing certificates in PKCS12 or PEM format.

## Version Requirements
The IP Optimization feature requires GlobalProtect client version 6.1.4 and later, 6.2.3 and later, or 6.3.0 and later, and does not support IPv6. This setting cannot be changed post-deployment.

## Deployment Timeline
Provisioning takes up to 15 minutes after pushing the initial configuration to Prisma Access.

## DNS Configuration
Clients require separate DNS resolution settings for internal and external domains. The maximum is 1,024 domain entries per rule. Specify domains with an asterisk prefix (e.g., `*.acme.com`).
