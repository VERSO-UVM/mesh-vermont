# Vermont Community Mesh Network — Project Description

**Proposed by:** VERSO (Vermont Research Open Source Program Office), University of Vermont  
**Program:** ORCA (Open Research Community Accelerator)  
**Status:** Concept / Pre-Implementation  

---

## Overview

This project proposes the design, deployment, and documentation of a community LoRa mesh network in Burlington, Vermont, using open-source Meshtastic and/or MeshCore firmware. The network would provide off-grid, infrastructure-independent communication for residents, community organizations, and emergency responders — functioning without cellular service, internet, or grid power.

The network is modeled on existing community deployments (notably the Oahu, Hawaii mesh) and designed as an open, unmanaged public commons: infrastructure built and documented by VERSO, with organic community adoption rather than a managed user roster.

---

## Problem Statement

Vermont communities face recurring infrastructure failures during weather events (Tropical Storm Irene, 2023 flooding, winter ice storms). During these events:

- Cellular networks become congested or fail entirely
- Internet-dependent communication systems go offline
- Rural and low-income residents are disproportionately isolated
- Emergency responders lack a resilient backup communication layer

Low-cost LoRa mesh networking addresses this gap at a fraction of the cost of traditional emergency communication infrastructure.

---

## Technology Stack

### Radio Protocol
- **LoRa (Long Range radio)** — 915MHz band, FCC Part 15 unlicensed operation, no ham license required
- Range: 1–3km urban, 5–15km elevated/open terrain, 15–30km+ line of sight over water (e.g. Lake Champlain corridor)
- AES-256 encryption on all channels

### Firmware Options
| Firmware | Best For | Notes |
|---|---|---|
| **Meshtastic** | Community/grassroots deployment, getting started | Larger community, better app ecosystem, flood routing |
| **MeshCore** | Municipal/managed deployments, scale 50+ nodes | Smarter routing, structured JSON telemetry, defined node roles |

**Recommendation:** Start with Meshtastic for Burlington pilot; evaluate MeshCore for any formal municipal deployment.

### Node Types
| Type | Role | Power |
|---|---|---|
| **Companion** | Personal handheld, paired to phone | Battery |
| **Repeater** | Infrastructure relay, standalone | Wall or solar |
| **Room Server** | Persistent group chat host, standalone | Wall or solar |

---

## Phase 1: Burlington Pilot

### Goal
Deploy a minimal viable mesh network covering central Burlington, establish a public channel, and appear on the global Meshtastic node map (meshmap.net) to drive organic adoption.

### Infrastructure Node Placement (3–5 nodes)
Candidate locations prioritizing elevation and line-of-sight:
- UVM campus (Waterman Building or similar roofline)
- Downtown Burlington rooftop or 4th floor window with external antenna
- South Burlington / Shelburne direction for lake corridor coverage
- Waterfront-facing node for Lake Champlain path to Charlotte/Shelburne

### Hardware — Fixed Infrastructure Nodes

**Option A: Indoor wall-powered (lowest friction)**
- Heltec V4 board (~$35–45)
- USB wall adapter
- SMA extension cable + 5–6dBi external antenna (~$25)
- Total per node: ~$60–70

**Option B: Outdoor solar-powered (set and forget)**
- RAKwireless WisMesh Repeater Mini ($100)
- IP67 rated, integrated solar panel, 3200mAh battery, pole/wall mount included
- Pre-flashed Meshtastic firmware, MeshCore-compatible
- Total per node: $100

### Hardware — Personal Companion Devices
- **Meshnology Heltec V4 2-pack with GPS** (~$93 for 2)
  - ESP32-S3, SX1262, 27dBm, L76 GNSS, 3000mAh battery, case, 915MHz antenna
  - Best for: initial testing, fixed nodes, MQTT-capable (WiFi)
- **Wio Tracker L1 / L1 Pro** (~$45–60 each)
  - nRF52840 chip, days of battery life vs hours
  - Best for: personal handheld carried daily
  - No WiFi — tradeoff for battery life

### Estimated Phase 1 Budget
| Item | Cost |
|---|---|
| 3–5 fixed infrastructure nodes | $200–500 |
| 2–4 personal companion devices | $90–200 |
| Antenna upgrades and cables | $50–100 |
| **Total** | **$340–800** |

---

## Phase 2: Community Launch

### Public Channel Setup
- Channel name: "BTV-Mesh" (or similar)
- Generate shared AES-256 encryption key
- Publish QR code publicly for open joining — no registration required
- Enable MQTT on at least one node → appears on meshmap.net

### Channel Structure
| Channel | Purpose | Access |
|---|---|---|
| Primary (BTV-Mesh) | Public community broadcast | Open — published QR code |
| Group channels | Neighborhood/organization groups | Key shared with specific groups |
| Direct messages | Person-to-person | End-to-end encrypted, always |

### Public Web Presence
A simple webpage (not a wiki — just a clean single page) containing:
- Plain-language explanation of the network
- Device purchasing recommendations with direct links
- QR code to join the BTV channel
- Approximate node locations on a map
- Link to meshmap.net centered on Burlington

### MQTT Configuration
- Enable MQTT on one internet-connected fixed node
- Use public Meshtastic broker (`mqtt.meshtastic.org`) initially
- Migrate to private Mosquitto broker (Raspberry Pi or VPS) for any municipal deployment
- Enable Store and Forward module on one fixed node for message persistence

---

## Phase 3: Statewide Backbone (Future)

### Concept
A minimal ridgeline node network connecting Vermont's major population corridors without requiring internet:

| Node Location | Coverage Area |
|---|---|
| Mt. Mansfield / Stowe area | Northern Champlain Valley, Lamoille corridor |
| Camel's Hump | Central Champlain Valley, Winooski corridor to Montpelier |
| Killington / Pico | Central Vermont, White River / Route 4 corridor |
| Mt. Ascutney | Upper Connecticut River Valley |
| Hogback Mountain | Southern Vermont, Brattleboro area |
| Burke Mountain | Northeast Kingdom, St. Johnsbury |
| Jay Peak | Far northern Vermont |

**Estimated hardware cost for statewide backbone: $1,500–3,000**

Node placement requires relationships with: Vermont State Parks, Green Mountain Club, ski resorts, cell tower operators, USFS.

---

## AI Integration (Research Extension)

### Edge AI on Gateway Nodes
- Local LLM (Llama 3 / Phi-3) on Raspberry Pi at gateway nodes
- Query emergency procedures, shelter locations, resource directories via mesh text message
- Functions without internet — inference runs locally
- Knowledge base synced from GitHub repo when internet available; static during outages

### AI-Assisted Network Management
- MQTT telemetry stream → InfluxDB → anomaly detection model
- Predict node failures from battery drain patterns
- Identify coverage gaps from signal strength (RSSI/SNR) data
- Alert administrators on critical node outages

### Sensor Network Intelligence
- Flood sensors, weather stations, road condition sensors on LoRaWAN
- Gateway Pi processes sensor data, generates alerts
- Alerts pushed to MeshCore communication mesh
- AI determines alert thresholds — raw sensor data never floods the communication mesh

### GIS Coverage Modeling
- SRTM terrain data + QGIS / Python viewshed analysis
- Identify optimal node placement for maximum population coverage
- Overlay population density, road networks, flood zones
- Output directly usable in grant applications

---

## ORCA Student Project Scope

This project is well-suited for one or more ORCA semester projects:

| Project | Skills | Output |
|---|---|---|
| Network deployment and documentation | Hardware, Linux, Meshtastic | Live Burlington mesh |
| Coverage modeling | Python, GIS, QGIS, SRTM data | Coverage maps, placement recommendations |
| Public dashboard | Python/Node.js, MQTT, web dev | Live node status and map web app |
| Emergency knowledge base | Python, RAG, LLM | Local AI query system on Pi |
| Sensor network integration | LoRaWAN, Python, data pipelines | Flood/weather sensor mesh bridge |
| Municipal case study | Research, writing, stakeholder interviews | Publishable report |

---

## Partner and Stakeholder Opportunities

| Organization | Angle |
|---|---|
| Vermont Emergency Management | Emergency communication resilience, node placement on state infrastructure |
| VCGI | GIS data for coverage modeling, potential sensor network integration |
| Burlington DPW / City Hall | Node placement on city-owned buildings |
| Vermont State Parks | Ridgeline and summit node placement |
| Green Mountain Club | Trail network nodes, backcountry communication |
| UVM Facilities | Campus node placement, power access |
| Center for Rural Studies | Agricultural sensor network, rural resilience framing |

---

## Regulatory Notes

- **FCC Part 15** — 915MHz operation requires no license for standard Meshtastic/MeshCore use
- Transmit power well within 1W legal limit (devices run 100–250mW typical, 500mW max)
- AES-256 encryption is permitted under Part 15 (unlike amateur radio operations)
- No registration, no spectrum coordination required

---

## Potential Funding Sources

- **NSF** — Rural broadband resilience, community technology infrastructure
- **USDA Rural Development** — Rural connectivity and resilience
- **FEMA BRIC** — Building Resilient Infrastructure and Communities
- **Vermont EPSCoR** — Research infrastructure with community benefit
- **Ford Foundation** — Rural equity framing (existing Leahy Institute connection)

---

## Key Resources

| Resource | URL |
|---|---|
| Meshtastic documentation | meshtastic.org/docs |
| MeshCore project | github.com/ripplebiz/MeshCore |
| Firmware flasher | flasher.meshtastic.org |
| Global node map | meshmap.net |
| RF coverage modeling | meshtastic.org/docs/software/other/meshtastic-site-planner |
| Radio link analysis | radiomobile.pe1mew.nl |
| Viewshed tool | heywhatsthat.com |
| VERSO GitHub | github.com/VERSO-UVM |

---

## Immediate Next Steps

1. Purchase Meshnology Heltec V4 2-pack with GPS (~$93) for initial testing
2. Flash firmware, configure BTV-Mesh channel, enable MQTT
3. Place one node at UVM / office, carry second as personal device
4. Run walk-test around Burlington to map actual coverage (log RSSI/SNR)
5. Use Meshtastic Site Planner to model 3 candidate fixed node locations
6. Contact Vermont Emergency Management to gauge existing interest
7. Publish simple project page with channel QR code
8. Recruit ORCA student for coverage modeling and dashboard projects

---

*Document generated from planning conversation, May 2026. VERSO / University of Vermont.*
