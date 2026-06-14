---
source_id: XDR-XSOAR-INTEGRATION-SETUP
title: Set up Device Security and XSOAR for Cortex XDR Integration
url: https://docs.paloaltonetworks.com/iot/integration/endpoint-protection/integrate-iot-security-with-cortex-xdr/set-up-iot-security-and-xsoar-for-xdr-integration
source_type: official_documentation
product: Cortex XDR
feature: XSOAR Integration
version: ""
last_reviewed_date: 2026-05-16
---

# Set up Device Security and XSOAR for Cortex XDR Integration

## Prerequisites
You need an advanced API key for Cortex XDR, the API key ID, and your XDR instance URL. Optional XQL features require a Cortex XDR Pro license and available query quota.

## Configuration Steps

### Step 1: Access XSOAR Integration Settings
Log into Device Security, navigate to Integrations, and launch Cortex XSOAR. In XSOAR, go to Settings and search for "xdr" to locate the integration instance.

### Step 2: Configure the XDR Instance
Click Add instance and enter:
- Instance name.
- Server URL (from your XDR account).
- API Key ID and API Key.
- "Last Seen" days (default: 7).
- Optional settings: Learn Multi Interfaces, Learn CVEs, Learn KBs, Learn Applications (for XQL data import).

Test the configuration; a success message confirms proper setup. Save and copy the instance name for later use.

### Step 3: Create XSOAR Jobs
Navigate to Jobs and create recurring jobs. For each playbook, specify:
- Frequency interval (Minutes, Hours, Days, or Weeks).
- Job name.
- Playbook selection: either "Import Cortex XDR Endpoints to PANW IoT" or "Import Cortex XDR XQL Data to Device Security."
- Integration instance name (paste the copied name).
- Site names (leave empty for all sites, or enter comma-separated names).

### Step 4: Enable and Monitor
Enable the integration instance and return to Device Security to verify that status changes from Disabled to Active, indicating successful setup.
