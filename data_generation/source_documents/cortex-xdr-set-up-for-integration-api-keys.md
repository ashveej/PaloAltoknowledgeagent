---
source_id: XDR-API-KEY-SETUP
title: Set up Cortex XDR for Integration
url: https://docs.paloaltonetworks.com/iot/integration/endpoint-protection/integrate-iot-security-with-cortex-xdr/set-up-cortex-xdr-for-integration
source_type: official_documentation
product: Cortex XDR
feature: API Keys / Integrations
version: ""
last_reviewed_date: 2026-06-04
---

# Set up Cortex XDR for Integration

## Prerequisites
You need Device Security (via Strata Cloud Manager or legacy IoT Security portal), an appropriate subscription (Enterprise Plus, Industrial OT, Medical, or Device Security X), and either a free cohosted or full-featured Cortex XSOAR instance.

## API Key Generation Steps

### Step 1: Create the API Key
Access Cortex XDR and navigate to Settings > Configurations > Integrations > API Keys. Create a new key with these settings:
- For direct API integration: Standard security level.
- For XSOAR integration: Advanced security level.
- Role: Instance Administrator.
- Views: Endpoint Administration (Viewer role is sufficient if not importing XQL data).

### Step 2: Store Credentials
After generation, copy the API key to a secure location and record its ID number from the API Keys table.

### Step 3: Obtain Server URL
Return to the API Keys section, right-click your key entry, and select the option to view examples. Extract the unique FQDN URL in the format: https://api-<fqdn>.

## Next Steps
With the API key, key ID, and server URL collected, proceed to configure Device Security for either direct API integration or XSOAR-based integration with Cortex XDR.
