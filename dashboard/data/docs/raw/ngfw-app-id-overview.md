---
source_id: NGFW-APP-ID-OVERVIEW
title: App-ID Overview
url: https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/app-id/app-id-overview
source_type: official_documentation
product: NGFW
feature: App-ID
version: "11.1"
last_reviewed_date: 2025-04-20
---

# App-ID Overview

## What App-ID Does
App-ID is Palo Alto Networks' proprietary traffic classification system that identifies applications regardless of port, protocol, encryption, or evasion tactics. It determines what an application is irrespective of port, protocol, encryption (SSH or SSL), or any other evasive tactic.

## Classification Mechanisms
The system employs three primary methods:
- Application signatures.
- Application protocol decoding.
- Heuristic analysis.

## The App-ID Identification Process
1. Policy Check — traffic is evaluated against security policies to determine if it is allowed.
2. Signature Matching — allowed traffic is scanned against application signatures, including detection of non-standard port usage.
3. Threat Scanning — allowed traffic undergoes threat analysis and granular application identification.
4. Decryption Analysis — when SSL/SSH encryption is detected and a decryption policy exists, sessions are decrypted for signature re-application.
5. Protocol Decoding — protocol decoders apply context-based signatures to detect applications tunneling within known protocols (e.g., instant messaging over HTTP).
6. Behavioral Analysis — for evasive applications resistant to signature detection, heuristics determine application identity.

## Policy Application
Once identified, policy determines treatment: blocking, allowing with threat scanning, monitoring unauthorized file transfers, or applying QoS-based traffic shaping.
