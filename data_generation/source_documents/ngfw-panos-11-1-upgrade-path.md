---
source_id: NGFW-PANOS-UPGRADE-PATH
title: Determine the Upgrade Path to PAN-OS 11.1 and Later Releases
url: https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-upgrade/upgrade-pan-os/upgrade-the-firewall-pan-os/determine-the-upgrade-path
source_type: official_documentation
product: NGFW
feature: PAN-OS Upgrade
version: "11.1"
last_reviewed_date: 2026-05-25
---

# Determine the Upgrade Path to PAN-OS 11.1 and Later Releases

## Initial Assessment Steps
1. Identify your current installed version via Panorama (Panorama > Managed Devices) or the firewall (Device > Software).
2. For PAN-OS 11.1.3+, disable the Base Releases checkbox to view preferred releases.
3. Review the Release Notes and upgrade considerations for each intermediate version.

## Key Upgrade Rules
For manual upgrades, Palo Alto Networks recommends installing and upgrading from the latest maintenance release for each PAN-OS release along your upgrade path. Do not install base images except for your target release.

## Version-Specific Paths
- PAN-OS 10.2+: use the Skip Software Version feature to upgrade directly to PAN-OS 12.1.
- PAN-OS 10.1: use Skip Software Version to upgrade directly to PAN-OS 11.1.
- PAN-OS 10.0: upgrade to the latest 10.0 maintenance, then 10.1.0, then the latest 10.1 maintenance, then skip to 11.1.
- PAN-OS 9.1 or earlier: a sequential path through 10.0 and 10.1 maintenance releases is required before reaching 11.1.

## Downtime Minimization
Perform upgrades during non-business hours to minimize user impact. For HA pairs, ensure preemption is disabled to prevent failover during the upgrade.
