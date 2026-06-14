# Evaluation Report — 5 Easy / 5 Medium / 5 Hard

_Generated 2026-06-14 04:48 UTC · models: claude-opus-4-8 (facts/style), claude-haiku-4-5 (classify) · embeddings: all-MiniLM-L6-v2 (local) · MOCK_LLM=False_

Confidence is computed deterministically; brand-voice (Experience) is scored from `brand_voice.yaml`. 'Hard' questions are intentionally outside the knowledge base to exercise SME escalation.

## Tier outcomes
- **Easy** (expect High): {'High': 5}
- **Medium** (expect Medium): {'Medium': 5}
- **Hard** (expect escalation/Low): {'Low': 5}

## Summary
| # | Tier | Question | Confidence | Trust | Exp | Final | Escalated | Sources |
|---|------|----------|-----------|------:|----:|------:|-----------|---------|
| 1 | easy | How much bandwidth and how many connectors does a ZTNA Conne | 🟢 High | 100 | 100 | 100.0 | no | PA-ZTNA-CONNECTOR-REQUIREMENTS |
| 2 | easy | What is the supported PAN-OS upgrade path to 11.1 and can I  | 🟢 High | 100 | 100 | 100.0 | no | NGFW-PANOS-UPGRADE-PATH, NGFW-PANOS-UPGRADE-PATH, NGFW-PANOS-UPGRADE-PATH |
| 3 | easy | What new networking features arrived in PAN-OS 11.2? | 🟢 High | 100 | 100 | 100.0 | no | NGFW-PANOS-11-2-NETWORKING-RN, NGFW-PANOS-11-2-NETWORKING-RN, NGFW-PANOS-11-2-NETWORKING-RN, NGFW-PANOS-11-2-NETWORKING-RN |
| 4 | easy | How many monitored users does an ADEM tenant support and wha | 🟢 High | 100 | 100 | 100.0 | no | PA-ADEM-OVERVIEW |
| 5 | easy | What is the maximum number of BGP IP addresses per remote ne | 🟢 High | 97 | 100 | 97.6 | no | PA-REMOTE-NETWORKS-ONBOARD |
| 6 | medium | What are the decryption types on the NGFW and which is unsup | 🟡 Medium | 80 | 100 | 84.0 | no | NGFW-DECRYPTION-OVERVIEW |
| 7 | medium | What is SSL Forward Proxy decryption used for on the firewal | 🟡 Medium | 93 | 100 | 94.4 | no | NGFW-DECRYPTION-OVERVIEW, NGFW-DECRYPTION-OVERVIEW, NGFW-DECRYPTION-OVERVIEW |
| 8 | medium | What is the maximum bandwidth per tunnel on high-performance | 🟡 Medium | 93 | 100 | 94.4 | no | PA-REMOTE-NETWORKS-HIGH-PERFORMANCE |
| 9 | medium | How many service endpoint addresses do high-performance remo | 🟡 Medium | 93 | 100 | 94.4 | no | PA-REMOTE-NETWORKS-HIGH-PERFORMANCE |
| 10 | medium | How does App-ID identify evasive or encrypted traffic? | 🟡 Medium | 93 | 100 | 94.4 | no | NGFW-DECRYPTION-OVERVIEW, NGFW-DECRYPTION-OVERVIEW, NGFW-APP-ID-OVERVIEW, NGFW-APP-ID-OVERVIEW |
| 11 | hard | How do I configure a Behavioral Threat Protection exception  | 🔴 Low | 0 | 0 | 0.0 | yes | — |
| 12 | hard | What is the App-ID throughput sizing for a PA-5450 in a mult | 🔴 Low | 0 | 0 | 0.0 | yes | — |
| 13 | hard | Does Prisma Access integrate with SAP S/4HANA accounting mod | 🔴 Low | 0 | 0 | 0.0 | yes | — |
| 14 | hard | Does Cortex XSIAM support MITRE ATT&CK technique mapping? | 🔴 Low | 0 | 0 | 0.0 | yes | — |
| 15 | hard | What is the per-user list price of Prisma Access? | 🔴 Low | 0 | 0 | 0.0 | yes | — |

## Details
### 1. [EASY] How much bandwidth and how many connectors does a ZTNA Connector group support?

- **Confidence:** 🟢 High  (Trust 100/100 · Experience 100/100 · Final 100.0)
- **Escalated to SME:** no
- **Detected product:** Prisma Access
- **Why confidence:** Score 100/100 from cited source(s): ZTNA Connector Requirements and Guidelines. Freshest cited source reviewed 46 days ago.
- **Trust breakdown:** citation 40/40 · relevance 25/25 · authority 20/20 · freshness 15/15 → raw 100
- **Why brand voice:** Experience 100/100 — all brand-voice checks passed.
- **Brand-voice rubric:** ✓ Leads with a direct answer 20/20 · ✓ Correct Palo Alto product terminology 15/15 · ✓ Preserves source caveats 15/15 · ✓ Within length guideline 15/15 · ✓ Includes SE positioning / next step 15/15 · ✓ Citations attached to claims 10/10 · ✓ On-brand tone (no banned phrases / hype) 10/10
- **Citations:** [PA-ZTNA-CONNECTOR-REQUIREMENTS#chunk-002](https://docs.paloaltonetworks.com/prisma-access/administration/ztna-connector-in-prisma-access/ztna-connector-requirements-and-guidelines#scale-and-performance-limits)

> Yes — Prisma Access ZTNA connectors scale predictably, and here are the exact limits you can design against.
> 
> Each individual connector supports up to 2 Gbps bandwidth and 100,000 concurrent sessions. A connector group supports a maximum of 4 connectors, delivering 6 Gbps aggregate bandwidth and 400,000 concurrent connections.
> 
> At the tenant level, the system supports 20,000 applications per tenant, 1,000 applications per group, 200 connectors per tenant, and a maximum of 1,024 IP subnets.
> 
> How to position this: Use the per-connector and per-group figures to size deployments against the customer's expected throughput and session counts, then confirm the tenant-wide application, c

### 2. [EASY] What is the supported PAN-OS upgrade path to 11.1 and can I skip versions?

- **Confidence:** 🟢 High  (Trust 100/100 · Experience 100/100 · Final 100.0)
- **Escalated to SME:** no
- **Detected product:** NGFW
- **Why confidence:** Score 100/100 from cited source(s): Determine the Upgrade Path to PAN-OS 11.1 and Later Releases. Freshest cited source reviewed 19 days ago.
- **Trust breakdown:** citation 40/40 · relevance 25/25 · authority 20/20 · freshness 15/15 → raw 100
- **Why brand voice:** Experience 100/100 — all brand-voice checks passed.
- **Brand-voice rubric:** ✓ Leads with a direct answer 20/20 · ✓ Correct Palo Alto product terminology 15/15 · ✓ Preserves source caveats 15/15 · ✓ Within length guideline 15/15 · ✓ Includes SE positioning / next step 15/15 · ✓ Citations attached to claims 10/10 · ✓ On-brand tone (no banned phrases / hype) 10/10
- **Citations:** [NGFW-PANOS-UPGRADE-PATH#chunk-003](https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-upgrade/upgrade-pan-os/upgrade-the-firewall-pan-os/determine-the-upgrade-path#version-specific-paths); [NGFW-PANOS-UPGRADE-PATH#chunk-001](https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-upgrade/upgrade-pan-os/upgrade-the-firewall-pan-os/determine-the-upgrade-path#initial-assessment-steps); [NGFW-PANOS-UPGRADE-PATH#chunk-002](https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-upgrade/upgrade-pan-os/upgrade-the-firewall-pan-os/determine-the-upgrade-path#key-upgrade-rules)

> Yes — your PAN-OS upgrade path to 11.1 depends on your current version, and the Skip Software Version feature can streamline it.
> 
> From PAN-OS 10.1, use Skip Software Version to upgrade directly to PAN-OS 11.1.
> 
> From PAN-OS 10.0, upgrade to the latest 10.0 maintenance release, then 10.1.0, then the latest 10.1 maintenance release, then skip to 11.1.
> 
> From PAN-OS 9.1 or earlier, a sequential path through 10.0 and 10.1 maintenance releases is required before reaching 11.1.
> 
> For manual upgrades, Palo Alto Networks recommends installing and upgrading from the latest maintenance release for each PAN-OS release along the path, and not installing base images except for the target rel

### 3. [EASY] What new networking features arrived in PAN-OS 11.2?

- **Confidence:** 🟢 High  (Trust 100/100 · Experience 100/100 · Final 100.0)
- **Escalated to SME:** no
- **Detected product:** NGFW
- **Why confidence:** Score 100/100 from cited source(s): Networking Features Introduced in PAN-OS 11.2. Freshest cited source reviewed 64 days ago.
- **Trust breakdown:** citation 40/40 · relevance 25/25 · authority 20/20 · freshness 15/15 → raw 100
- **Why brand voice:** Experience 100/100 — all brand-voice checks passed.
- **Brand-voice rubric:** ✓ Leads with a direct answer 20/20 · ✓ Correct Palo Alto product terminology 15/15 · ✓ Preserves source caveats 15/15 · ✓ Within length guideline 15/15 · ✓ Includes SE positioning / next step 15/15 · ✓ Citations attached to claims 10/10 · ✓ On-brand tone (no banned phrases / hype) 10/10
- **Citations:** [NGFW-PANOS-11-2-NETWORKING-RN#chunk-001](https://docs.paloaltonetworks.com/pan-os/11-2/pan-os-release-notes/features-introduced-in-pan-os/networking-features#http-2-protocol-support); [NGFW-PANOS-11-2-NETWORKING-RN#chunk-004](https://docs.paloaltonetworks.com/pan-os/11-2/pan-os-release-notes/features-introduced-in-pan-os/networking-features#post-quantum-hybrid-key-exchange-vpn); [NGFW-PANOS-11-2-NETWORKING-RN#chunk-002](https://docs.paloaltonetworks.com/pan-os/11-2/pan-os-release-notes/features-introduced-in-pan-os/networking-features#enhanced-dos-and-packet-buffer-protection); [NGFW-PANOS-11-2-NETWORKING-RN#chunk-003](https://docs.paloaltonetworks.com/pan-os/11-2/pan-os-release-notes/features-introduced-in-pan-os/networking-features#encrypted-dns-options)

> Yes — PAN-OS 11.2 delivers meaningful management-plane, security, and cryptographic advances for the NGFW.
> 
> Starting in PAN-OS 11.2.8, the management plane supports HTTP/2 alongside HTTP/1.1, enabling multiplexing, header compression, and server push. When you manually enable HTTP/2 via CLI, HTTP/1.1 is disabled with no fallback, maintaining security compliance.
> 
> Starting with PAN-OS 11.2.3, you can configure edge zones using both source and destination IP addresses for improved attack mitigation — adding configurable DoS policies for destination IP-only classification, simultaneous buffer-based and latency-based activation, adjustable software block duration, and SNMP monitoring for

### 4. [EASY] How many monitored users does an ADEM tenant support and what license does ADEM need?

- **Confidence:** 🟢 High  (Trust 100/100 · Experience 100/100 · Final 100.0)
- **Escalated to SME:** no
- **Detected product:** —
- **Why confidence:** Score 100/100 from cited source(s): Prisma Access Autonomous DEM (ADEM) Overview. Freshest cited source reviewed 26 days ago.
- **Trust breakdown:** citation 40/40 · relevance 25/25 · authority 20/20 · freshness 15/15 → raw 100
- **Why brand voice:** Experience 100/100 — all brand-voice checks passed.
- **Brand-voice rubric:** ✓ Leads with a direct answer 20/20 · ✓ Correct Palo Alto product terminology 15/15 · ✓ Preserves source caveats 15/15 · ✓ Within length guideline 15/15 · ✓ Includes SE positioning / next step 15/15 · ✓ Citations attached to claims 10/10 · ✓ On-brand tone (no banned phrases / hype) 10/10
- **Citations:** [PA-ADEM-OVERVIEW#chunk-001](https://docs.paloaltonetworks.com/prisma-access/adem#page-1)

> Yes — Autonomous Digital Experience Management (ADEM) scales to large deployments, with a single tenant supporting up to 200,000 monitored users.
> 
> Keep the licensing model in mind: ADEM requires a per-user ADEM license in addition to the Prisma Access license. That per-user model is what underpins the monitored-user count toward the 200,000-user tenant limit.
> 
> How to position this: For large-enterprise opportunities, confirm the customer's monitored-user count fits within the 200,000-per-tenant ceiling, then size the per-user ADEM licenses alongside their existing Prisma Access entitlement so the quote reflects both components.
> 
> Important caveats:
> Licensing and limits:
> - ADEM

### 5. [EASY] What is the maximum number of BGP IP addresses per remote network?

- **Confidence:** 🟢 High  (Trust 97/100 · Experience 100/100 · Final 97.6)
- **Escalated to SME:** no
- **Detected product:** Prisma Access
- **Why confidence:** Score 97/100 from cited source(s): Onboard a Remote Network. Freshest cited source reviewed 123 days ago.
- **Trust breakdown:** citation 40/40 · relevance 25/25 · authority 20/20 · freshness 12/15 → raw 97
- **Why brand voice:** Experience 100/100 — all brand-voice checks passed.
- **Brand-voice rubric:** ✓ Leads with a direct answer 20/20 · ✓ Correct Palo Alto product terminology 15/15 · ✓ Preserves source caveats 15/15 · ✓ Within length guideline 15/15 · ✓ Includes SE positioning / next step 15/15 · ✓ Citations attached to claims 10/10 · ✓ On-brand tone (no banned phrases / hype) 10/10
- **Citations:** [PA-REMOTE-NETWORKS-ONBOARD#chunk-004](https://docs.paloaltonetworks.com/prisma-access/administration/prisma-access-remote-networks/onboard-a-remote-network#limits-and-constraints)

> Yes — Prisma Access supports up to 250 local BGP IP addresses per remote network. In practical terms, that scales to 250 remote networks with a primary tunnel only, 125 networks using ECMP with 2 links, or 62 networks using ECMP with 4 links.
> 
> Keep these conditions in mind when you design: ECMP load balancing requires BGP and supports up to 4 tunnels. If you're using tunnel monitoring, it requires a static route configuration on the customer premises equipment pointing to the monitoring IP address.
> 
> How to position this: Walk the customer through their resiliency goals first — single primary tunnel versus ECMP with 2 or 4 links — then map the resulting remote-network count against th

### 6. [MEDIUM] What are the decryption types on the NGFW and which is unsupported in Strata Cloud Manager?

- **Confidence:** 🟡 Medium  (Trust 80/100 · Experience 100/100 · Final 84.0)
- **Escalated to SME:** no
- **Detected product:** NGFW
- **Why confidence:** Score 80/100 from cited source(s): Decryption Overview. Freshest cited source reviewed 241 days ago. Confidence capped because: primary source reviewed over 180 days ago.
- **Trust breakdown:** citation 40/40 · relevance 12/25 · authority 20/20 · freshness 8/15 → raw 80 · caps: primary source reviewed over 180 days ago
- **Why brand voice:** Experience 100/100 — all brand-voice checks passed.
- **Brand-voice rubric:** ✓ Leads with a direct answer 20/20 · ✓ Correct Palo Alto product terminology 15/15 · ✓ Preserves source caveats 15/15 · ✓ Within length guideline 15/15 · ✓ Includes SE positioning / next step 15/15 · ✓ Citations attached to claims 10/10 · ✓ On-brand tone (no banned phrases / hype) 10/10
- **Citations:** [NGFW-DECRYPTION-OVERVIEW#chunk-002](https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/decryption/decryption-overview#three-decryption-types)

> Yes — the NGFW gives you three decryption types to inspect encrypted traffic across your environment: SSL Forward Proxy, SSL Inbound Inspection, and SSH Proxy.
> 
> SSL Forward Proxy inspects traffic leaving your internal network toward the internet, giving you visibility into outbound user activity. SSL Inbound Inspection examines traffic entering your internal network servers from external sources, protecting your published applications. SSH Proxy inspects and controls traffic within SSH tunnels.
> 
> One important condition to set expectations: SSH Proxy is not supported by Strata Cloud Manager.
> 
> How to position this: Lead with the three decryption types to address full visibility int

### 7. [MEDIUM] What is SSL Forward Proxy decryption used for on the firewall?

- **Confidence:** 🟡 Medium  (Trust 93/100 · Experience 100/100 · Final 94.4)
- **Escalated to SME:** no
- **Detected product:** NGFW
- **Why confidence:** Score 93/100 from cited source(s): Decryption Overview. Freshest cited source reviewed 241 days ago. Confidence capped because: primary source reviewed over 180 days ago.
- **Trust breakdown:** citation 40/40 · relevance 25/25 · authority 20/20 · freshness 8/15 → raw 93 · caps: primary source reviewed over 180 days ago
- **Why brand voice:** Experience 100/100 — all brand-voice checks passed.
- **Brand-voice rubric:** ✓ Leads with a direct answer 20/20 · ✓ Correct Palo Alto product terminology 15/15 · ✓ Preserves source caveats 15/15 · ✓ Within length guideline 15/15 · ✓ Includes SE positioning / next step 15/15 · ✓ Citations attached to claims 10/10 · ✓ On-brand tone (no banned phrases / hype) 10/10
- **Citations:** [NGFW-DECRYPTION-OVERVIEW#chunk-002](https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/decryption/decryption-overview#three-decryption-types); [NGFW-DECRYPTION-OVERVIEW#chunk-001](https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/decryption/decryption-overview#overview); [NGFW-DECRYPTION-OVERVIEW#chunk-003](https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/decryption/decryption-overview#how-ssl-decryption-works)

> Yes — the NGFW gives you full visibility into encrypted traffic through SSL Forward Proxy. SSL Forward Proxy inspects traffic leaving your internal network toward the internet, converting encrypted data into a readable format for inspection across SSL/TLS and SSH traffic. This lets the firewall examine both outbound and inbound encrypted communications.
> 
> Mechanically, the NGFW establishes itself as a trusted intermediary using keys and certificates between client and server. It decrypts SSL/TLS traffic to plaintext, inspects it, then re-encrypts before forwarding — maintaining data privacy throughout.
> 
> One caveat to note: SSH Proxy inspects and controls traffic within SSH tunnels, bu

### 8. [MEDIUM] What is the maximum bandwidth per tunnel on high-performance remote networks?

- **Confidence:** 🟡 Medium  (Trust 93/100 · Experience 100/100 · Final 94.4)
- **Escalated to SME:** no
- **Detected product:** Prisma Access
- **Why confidence:** Score 93/100 from cited source(s): Remote Networks—High Performance. Freshest cited source reviewed 248 days ago. Confidence capped because: primary source reviewed over 180 days ago.
- **Trust breakdown:** citation 40/40 · relevance 25/25 · authority 20/20 · freshness 8/15 → raw 93 · caps: primary source reviewed over 180 days ago
- **Why brand voice:** Experience 100/100 — all brand-voice checks passed.
- **Brand-voice rubric:** ✓ Leads with a direct answer 20/20 · ✓ Correct Palo Alto product terminology 15/15 · ✓ Preserves source caveats 15/15 · ✓ Within length guideline 15/15 · ✓ Includes SE positioning / next step 15/15 · ✓ Citations attached to claims 10/10 · ✓ On-brand tone (no banned phrases / hype) 10/10
- **Citations:** [PA-REMOTE-NETWORKS-HIGH-PERFORMANCE#chunk-001](https://docs.paloaltonetworks.com/prisma-access/administration/prisma-access-remote-networks/remote-networks-high-performance#bandwidth-capabilities)

> Yes — Prisma Access supports up to 2 Gbps of bandwidth per remote network tunnel from a remote site on high-performance remote networks. Keep two conditions in view as you size deployments: each remote network tunnel from a remote site delivers up to 2 Gbps, and aggregate bandwidth per node in a compute region is capped at up to 3 Gbps. Plan tunnel and node allocation accordingly so customer throughput expectations align with both limits.
> 
> How to position this: For high-bandwidth branch sites, walk the customer through both the 2 Gbps per-tunnel and 3 Gbps per-node ceilings to validate the architecture meets their throughput requirements before sizing.
> 
> Important caveats:
> - Up to 3

### 9. [MEDIUM] How many service endpoint addresses do high-performance remote networks use per Gbps?

- **Confidence:** 🟡 Medium  (Trust 93/100 · Experience 100/100 · Final 94.4)
- **Escalated to SME:** no
- **Detected product:** Prisma Access
- **Why confidence:** Score 93/100 from cited source(s): Remote Networks—High Performance. Freshest cited source reviewed 248 days ago. Confidence capped because: primary source reviewed over 180 days ago.
- **Trust breakdown:** citation 40/40 · relevance 25/25 · authority 20/20 · freshness 8/15 → raw 93 · caps: primary source reviewed over 180 days ago
- **Why brand voice:** Experience 100/100 — all brand-voice checks passed.
- **Brand-voice rubric:** ✓ Leads with a direct answer 20/20 · ✓ Correct Palo Alto product terminology 15/15 · ✓ Preserves source caveats 15/15 · ✓ Within length guideline 15/15 · ✓ Includes SE positioning / next step 15/15 · ✓ Citations attached to claims 10/10 · ✓ On-brand tone (no banned phrases / hype) 10/10
- **Citations:** [PA-REMOTE-NETWORKS-HIGH-PERFORMANCE#chunk-001](https://docs.paloaltonetworks.com/prisma-access/administration/prisma-access-remote-networks/remote-networks-high-performance#bandwidth-capabilities)

> Yes — Prisma Access high-performance remote networks allocate one Service Endpoint address for every 3 Gbps of bandwidth. Plan your IP addressing accordingly as you scale.
> 
> Keep these conditions in mind:
> - Up to 3 Gbps aggregate bandwidth per node in a compute region.
> - Up to 2 Gbps bandwidth per remote network tunnel from a remote site.
> 
> How to position this: Walk the customer through their per-site and per-region bandwidth requirements to size Service Endpoint allocations correctly, and confirm tunnel throughput stays within the 2 Gbps per-tunnel limit when designing high-performance remote network connectivity.
> 
> Important caveats:
> - Up to 3 Gbps aggregate bandwidth per n

### 10. [MEDIUM] How does App-ID identify evasive or encrypted traffic?

- **Confidence:** 🟡 Medium  (Trust 93/100 · Experience 100/100 · Final 94.4)
- **Escalated to SME:** no
- **Detected product:** NGFW
- **Why confidence:** Score 93/100 from cited source(s): App-ID Overview, Decryption Overview. Freshest cited source reviewed 241 days ago. Confidence capped because: primary source reviewed over 180 days ago.
- **Trust breakdown:** citation 40/40 · relevance 25/25 · authority 20/20 · freshness 8/15 → raw 93 · caps: primary source reviewed over 180 days ago
- **Why brand voice:** Experience 100/100 — all brand-voice checks passed.
- **Brand-voice rubric:** ✓ Leads with a direct answer 20/20 · ✓ Correct Palo Alto product terminology 15/15 · ✓ Preserves source caveats 15/15 · ✓ Within length guideline 15/15 · ✓ Includes SE positioning / next step 15/15 · ✓ Citations attached to claims 10/10 · ✓ On-brand tone (no banned phrases / hype) 10/10
- **Citations:** [NGFW-DECRYPTION-OVERVIEW#chunk-002](https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/decryption/decryption-overview#three-decryption-types); [NGFW-DECRYPTION-OVERVIEW#chunk-001](https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/decryption/decryption-overview#overview); [NGFW-APP-ID-OVERVIEW#chunk-002](https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/app-id/app-id-overview#the-app-id-identification-process); [NGFW-APP-ID-OVERVIEW#chunk-001](https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/app-id/app-id-overview#what-app-id-does)

> Yes — App-ID identifies applications regardless of port, protocol, encryption (SSH or SSL), or any other evasive tactic. Here's how it works across multiple mechanisms:
> 
> Signature matching scans allowed traffic against application signatures, including detection of non-standard port usage. When SSL/SSH encryption is detected and a decryption policy exists, sessions are decrypted so signatures can be re-applied. Protocol decoders then apply context-based signatures to detect applications tunneling within known protocols — for example, instant messaging over HTTP. For evasive applications that resist signature detection, behavioral analysis using heuristics determines application identity.

### 11. [HARD] How do I configure a Behavioral Threat Protection exception and exploit-protection ROP modules in Cortex XDR?

- **Confidence:** 🔴 Low  (Trust 0/100 · Experience 0/100 · Final 0.0)
- **Escalated to SME:** yes
- **Detected product:** Cortex XDR
- **Why confidence:** Blocked by gates: insufficient_evidence.

> I could not find enough approved source material to answer this confidently. I've routed this question to the appropriate SME group.

### 12. [HARD] What is the App-ID throughput sizing for a PA-5450 in a multi-vsys HA deployment?

- **Confidence:** 🔴 Low  (Trust 0/100 · Experience 0/100 · Final 0.0)
- **Escalated to SME:** yes
- **Detected product:** NGFW
- **Why confidence:** Blocked by gates: insufficient_evidence.

> I could not find enough approved source material to answer this confidently. I've routed this question to the appropriate SME group.

### 13. [HARD] Does Prisma Access integrate with SAP S/4HANA accounting modules?

- **Confidence:** 🔴 Low  (Trust 0/100 · Experience 0/100 · Final 0.0)
- **Escalated to SME:** yes
- **Detected product:** Prisma Access
- **Why confidence:** Blocked by gates: insufficient_evidence.

> I could not find enough approved source material to answer this confidently. I've routed this question to the appropriate SME group.

### 14. [HARD] Does Cortex XSIAM support MITRE ATT&CK technique mapping?

- **Confidence:** 🔴 Low  (Trust 0/100 · Experience 0/100 · Final 0.0)
- **Escalated to SME:** yes
- **Detected product:** Cortex XDR
- **Why confidence:** Blocked by gates: insufficient_evidence.

> I could not find enough approved source material to answer this confidently. I've routed this question to the appropriate SME group.

### 15. [HARD] What is the per-user list price of Prisma Access?

- **Confidence:** 🔴 Low  (Trust 0/100 · Experience 0/100 · Final 0.0)
- **Escalated to SME:** yes
- **Detected product:** Prisma Access
- **Why confidence:** Blocked by gates: insufficient_evidence.

> I could not find enough approved source material to answer this confidently. I've routed this question to the appropriate SME group.
