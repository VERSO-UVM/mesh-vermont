# Mesh Vermont

Vermont communities have experienced catastrophic communication failures during disasters three times in twelve years. A proven, open-source technology now exists that would provide a resilient backup communication layer for the entire state for under $5,000 in hardware — functioning without cellular service, internet, or grid power. No other state has built this. Vermont should be first.

# Vermont Community Mesh Network

A community LoRa mesh network for Burlington, Vermont — built on open-source [Meshtastic](https://meshtastic.org) and [MeshCore](https://github.com/ripplebiz/MeshCore) firmware to provide off-grid, infrastructure-independent communication for residents, community organizations, and emergency responders.

This is a [VERSO](https://github.com/VERSO-UVM) project at the University of Vermont, developed through the [ORCA](https://github.com/VERSO-UVM/ORCA) program.

---

## Why This Exists

Vermont has a documented, recurring problem: when major weather events hit, the communication infrastructure people depend on fails at the same time they need it most.

Tropical Storm Irene in 2011. The 2023 floods. Ice storms that knock out power for days at a time across rural communities. Each time, the same gap appears — cellular towers lose grid power and backhaul internet, roads wash out, and people have no way to communicate with neighbors, family, or emergency services.

There is currently no civilian backup communication layer between a Vermont resident's cell phone and a ham radio license. Mesh networking fills that gap.

A statewide backbone connecting Vermont's major population corridors costs an estimated $1,500–$3,000 in hardware. A city-wide mesh covering Burlington costs $300–$800. This technology is mature, the hardware is commodity, the software is open source, and the network self-organizes without ongoing management cost. The cost argument for doing nothing is hard to make.

---

## How It Works

[Meshtastic](https://meshtastic.org) and [MeshCore](https://github.com/ripplebiz/MeshCore) use inexpensive LoRa (Long Range radio) hardware to create a decentralized peer-to-peer mesh network. Devices rebroadcast messages they receive, so the network extends as far as there are nodes — no cellular service, no internet, no grid power required.

- **915MHz band** — FCC Part 15 unlicensed, no ham license needed
- **AES-256 encryption** on all channels
- **1–3km urban range**, 5–15km elevated, 15–30km+ line of sight over water
- **$35–100 per node** for hardware
- Works with a free iOS or Android app — no special software required

Each person carries a small device (roughly the size of a deck of cards) paired to their phone via Bluetooth. Fixed infrastructure nodes at elevation act as repeaters, stitching the mesh together across the city. When internet is available, nodes bridge to the global Meshtastic network via MQTT — when it's not, the local radio mesh keeps working on its own.

---

## Vermont's Geography Is an Advantage

The Green Mountains running north-south through the state are nearly ideal for this technology. A single solar-powered node on Camel's Hump serves the entire Champlain Valley to the west and the Winooski corridor toward Montpelier to the east simultaneously. Lake Champlain is an open water path where range extends dramatically — Burlington to Charlotte is a straightforward 15km link over flat water.

The terrain that makes Vermont logistically difficult during disasters is the same terrain that makes mesh networking particularly effective here.

---

## Project Structure

This is a phased deployment starting with a Burlington pilot and designed to grow into a statewide backbone.

### Phase 1 — Burlington Pilot

Deploy 3–5 fixed infrastructure nodes covering central Burlington, establish a public channel (BTV-Mesh), and appear on the global node map at [meshmap.net](https://meshmap.net) to drive organic community adoption.

**Infrastructure node candidates:**
- UVM campus roofline or 4th floor window with external antenna
- Downtown Burlington elevated location
- South Burlington / Shelburne corridor for lake coverage
- Waterfront-facing node for Lake Champlain path south

**Hardware:**

| Role | Device | Cost |
|---|---|---|
| Fixed indoor node | Heltec V4 + external antenna | ~$60–70 |
| Fixed outdoor node | RAKwireless WisMesh Repeater Mini | ~$100 |
| Personal handheld | Meshnology Heltec V4 2-pack with GPS | ~$93 for 2 |
| Personal handheld (battery priority) | Wio Tracker L1 Pro | ~$55–60 |

**Estimated Phase 1 budget: $340–800**

### Phase 2 — Community Launch

- Publish BTV-Mesh channel QR code openly — no registration, no account required
- Enable MQTT bridging on one node to appear on meshmap.net
- Launch a simple public webpage with device recommendations, QR code, and node map
- Enable Store and Forward on one fixed node for message persistence

This follows the Hawaii/Oahu model: build the infrastructure, publish how to join, let adoption happen organically. We're not managing users. Anyone with a $35–45 device and the free app can participate.

### Phase 3 — Statewide Backbone

A minimal ridgeline node network connecting Vermont's major population corridors — functioning without internet, designed to survive the exact conditions when it's needed most.

| Node Location | Coverage |
|---|---|
| Mt. Mansfield / Stowe | Northern Champlain Valley, Lamoille corridor |
| Camel's Hump | Central Champlain Valley, Winooski corridor to Montpelier |
| Killington / Pico | Central Vermont, White River / Route 4 corridor |
| Mt. Ascutney | Upper Connecticut River Valley |
| Hogback Mountain | Southern Vermont, Brattleboro area |
| Burke Mountain | Northeast Kingdom, St. Johnsbury |
| Jay Peak | Far northern Vermont |

**Estimated hardware cost for statewide backbone: $1,500–3,000**

---

## Research Extensions

This project has a research layer beyond the infrastructure deployment. VERSO is specifically interested in:

**Edge AI on gateway nodes** — running a local LLM (Llama 3 / Phi-3) on a Raspberry Pi at gateway nodes to answer queries about emergency procedures, shelter locations, and resource directories via mesh text message. No internet required. Knowledge base syncs from GitHub when connectivity is available and stays static during outages.

**Sensor network integration** — LoRaWAN flood sensors, weather stations, and road condition sensors feeding into a gateway Pi that processes data, applies AI-determined alert thresholds, and pushes actionable alerts to the communication mesh. Raw sensor data never floods the mesh — only meaningful alerts reach people.

**GIS coverage modeling** — SRTM terrain data and Python viewshed analysis to identify optimal node placement, validate coverage claims, and produce outputs usable in grant applications and municipal proposals.

**AI-assisted network management** — MQTT telemetry stream into InfluxDB, anomaly detection on battery drain and signal strength patterns to predict node failures before they happen.

---

## ORCA Student Projects

This project is designed around ORCA semester engagements. Current open project areas:

| Project | Skills | Deliverable |
|---|---|---|
| Network deployment + documentation | Hardware, Linux, Meshtastic/MeshCore | Live Burlington mesh |
| GIS coverage modeling | Python, QGIS, SRTM terrain data | Coverage maps + placement analysis |
| Public dashboard | Python or Node.js, MQTT, web dev | Live node status + map web app |
| Emergency knowledge base | Python, RAG, LLM, Raspberry Pi | Local AI query system |
| Sensor network integration | LoRaWAN, Python, data pipelines | Flood/weather sensor bridge |
| Municipal case study | Research, writing, stakeholder interviews | Publishable report |

If you're an ORCA student interested in any of these, open an issue or reach out directly.

---

## Partners and Stakeholders

We're actively building relationships with organizations that have a stake in Vermont's communication resilience:

| Organization | Role |
|---|---|
| Vermont Emergency Management | Emergency comms resilience, infrastructure placement |
| VCGI | GIS data, sensor network integration |
| Burlington DPW / City Hall | Node placement on city-owned buildings |
| Vermont State Parks | Ridgeline and summit node placement |
| Green Mountain Club | Trail network nodes, backcountry communication |
| UVM Facilities | Campus node placement and power access |
| Center for Rural Studies | Agricultural sensor network, rural resilience framing |

---

## Regulatory Notes

Standard Meshtastic and MeshCore operation on 915MHz falls under FCC Part 15 — the same category as WiFi routers and Bluetooth devices. No license required, no registration, no spectrum coordination. Devices run 100–250mW typical, well within the 1W legal limit. AES-256 encryption is permitted under Part 15.

---

## Funding

This project is fundable as community resilience infrastructure and as open research. Relevant programs:

- **FEMA BRIC** — Building Resilient Infrastructure and Communities
- **USDA Rural Development** — Rural connectivity and resilience
- **NSF** — Rural broadband resilience, community technology infrastructure
- **Vermont EPSCoR** — Research infrastructure with community benefit
- **Ford Foundation** — Rural equity framing (existing Leahy Institute connection)

---

## Getting Started

The fastest path to a working Burlington node:

1. Order the [Meshnology Heltec V4 2-pack with GPS](https://www.amazon.com/dp/B0G2LG9TK1) (~$93) — comes with battery, case, GPS, and antenna
2. Flash Meshtastic firmware at [flasher.meshtastic.org](https://flasher.meshtastic.org) — browser-based, takes 5 minutes per device
3. Install the [Meshtastic app](https://meshtastic.org/docs/software/android/) on your phone, pair via Bluetooth
4. Set region to US, configure BTV-Mesh channel
5. Enable WiFi and MQTT on your fixed node — it will appear on [meshmap.net](https://meshmap.net)

Total time from unboxing to live node: under an hour.

---

## Resources

| Resource | Link |
|---|---|
| Meshtastic docs | [meshtastic.org/docs](https://meshtastic.org/docs) |
| MeshCore project | [github.com/ripplebiz/MeshCore](https://github.com/ripplebiz/MeshCore) |
| Firmware flasher | [flasher.meshtastic.org](https://flasher.meshtastic.org) |
| Global node map | [meshmap.net](https://meshmap.net) |
| RF coverage modeling | [Meshtastic Site Planner](https://meshtastic.org/docs/software/other/meshtastic-site-planner) |
| Radio link analysis | [radiomobile.pe1mew.nl](https://radiomobile.pe1mew.nl) |
| Viewshed tool | [heywhatsthat.com](https://heywhatsthat.com) |
| VERSO GitHub | [github.com/VERSO-UVM](https://github.com/VERSO-UVM) |

---

*A VERSO / University of Vermont project. May 2026.*
