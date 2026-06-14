# Sample Questions

Questions a Technical Sales rep would realistically ask, grounded in the **real
Palo Alto Networks docs** ingested into the knowledge base (`data/docs/raw/`).
Confidence is computed deterministically — older source docs are intentionally
present to exercise the freshness caps.

Ask them in the UI (http://localhost:8077) or via `POST /agent/ask`.

## Expected High confidence (fresh official sources)
| Question | Answered by |
| --- | --- |
| How much bandwidth and how many connectors does a ZTNA Connector group support? | `PA-ZTNA-CONNECTOR-REQUIREMENTS` |
| What is the supported PAN-OS upgrade path to 11.1, and can I skip versions? | `NGFW-PANOS-UPGRADE-PATH` |
| What new networking features arrived in PAN-OS 11.2? | `NGFW-PANOS-11-2-NETWORKING-RN` |
| What IP pool size do I need per location for GlobalProtect mobile users? | `PA-MOBILE-USERS-SETUP` |
| What AS number does Prisma Access advertise for service connections? | `PA-SERVICE-CONNECTION-ROUTING` |
| What's the max number of BGP IP addresses per remote network? | `PA-REMOTE-NETWORKS-ONBOARD` |
| What API key security level is needed to integrate Cortex XDR with another product? | `XDR-API-KEY-SETUP` |

## Expected Medium confidence (source reviewed > 180 days ago → freshness cap)
| Question | Answered by | Why capped |
| --- | --- | --- |
| What are the decryption types on the NGFW and which is unsupported in Strata Cloud Manager? | `NGFW-DECRYPTION-OVERVIEW` | reviewed ~Oct 2025 |
| What's the max bandwidth per tunnel on high-performance remote networks? | `PA-REMOTE-NETWORKS-HIGH-PERFORMANCE` | reviewed ~Oct 2025 |
| How does App-ID identify evasive or encrypted traffic? | `NGFW-APP-ID-OVERVIEW` | reviewed ~Apr 2025 |
| Why deploy the Cortex XDR agent on data-center servers? | `XDR-DATA-CENTER-ENDPOINTS` | reviewed ~Apr 2025 |

## Expected SME escalation (not in the knowledge base)
| Question | Why |
| --- | --- |
| How do I add a Behavioral Threat Protection exception and configure exploit-protection ROP modules in Cortex XDR? | KB has no exploit/BTP profile internals → Claude returns INSUFFICIENT_EVIDENCE |
| What is the App-ID throughput sizing for a PA-5450 in a multi-vsys HA deployment? | No hardware-sizing/datasheet content ingested |
| Does Prisma Access integrate with SAP S/4HANA accounting modules? | Off-topic; no supporting evidence |

> Tip: after escalating one of these, open the **SME Queue** tab, type an answer,
> and **Approve & Publish** — then re-ask the same question and it will be answered
> from the new SME-approved source.
