# Mesh Network Deployments: Case Studies and Lessons for Vermont

This document summarizes documented real-world mesh network deployments, what worked, what didn't, and what they suggest for a Vermont deployment. All cases involve LoRa-based mesh technology (Meshtastic or MeshCore) deployed in response to or in anticipation of infrastructure failures.

<ul>
<li>Birmingham, Alabama: <a href="http://birminghammesh.org/">Birmingham Mesh</a></li>
<li>Calgary, Alberta: <a href="https://yycmesh.com">YYC Mesh</a></li>
<li>Asheville, North Carolina: <a href="https://meshavl.com/">MeshAVL</a></li>
<li>Charlotte, North Carolina: <a href="https://charlottemesh.org/">Charlotte Mesh</a></li>
<li>North Carolina <a href="https://ncmesh.net/">NC Mesh</a></li>
<li>Chicago, Illinois: <a href="https://chicagolandmesh.org/">Chicagoland Mesh</a></li>
<li>Colorado: <a href="https://coloradomesh.org/">Colorado Mesh</a></li>
<li>Hawaii: <a href="https://www.hawaiimesh.net/">Hawaii Mesh</a></li>
<li>Nashville, Tennessee: <a href="https://www.instagram.com/meshville.tn">Meshville</a></li>
<li>Northern Texas: <a href="https://ntxmesh.com">North Texas Mesh</a></li>
<li>Southern Texas: <a href="https://sanantoniogmrs.com/stxmesh/">South Texas Mesh</a></li>
<li>Northwest Arkansas: <a href="https://nwamesh.com/">Northwest Arkansas Mesh</a></li>
<li>Okmesh: <a href="https://okmesh.org/">Okmesh</a></li>
<li>Ohio: <a href="https://www.ohiomesh.net">Ohio Mesh</a></li>
<li>Philadelphia, Pennsylvania: <a href="https://iffybooks.net/">Iffy Books is leading the effort</a></li>
<li>San Francisco (Bay Area): <a href="https://bayme.sh">bayme.sh</a></li>
<li>Southern California: <a href="https://socalmesh.org/">SoCal Mesh</a></li>
<li>Wisconsin: <a href="https://meshconsin.org/">Meshconsin</a></li>
</ul>


# Mesh Network Deployments: Case Studies and Lessons for Vermont

This document summarizes documented real-world mesh network deployments, what worked, what didn't, and what they suggest for a Vermont deployment. All cases involve LoRa-based mesh technology (Meshtastic or MeshCore) deployed in response to or in anticipation of infrastructure failures.

---

## Case Study 1: Hurricane Helene — Western North Carolina (September 2024)

**What happened:**
[Hurricane Helene](https://www.ncdps.gov/our-organization/emergency-management/tropical-storm-helene) made landfall in September 2024 and caused catastrophic flooding across western North Carolina — washed-out highways, closed mountain passes, and weeks-long power outages across communities that rarely face hurricane-force conditions.

The communication failure was immediate and total. [The FCC reported 3,432 cell sites down across the Southeast](https://www.telecomstechnews.com/news/how-to-achieve-reliable-communication-in-emergency-scenarios/). In the hardest-hit counties of western North Carolina, [fewer than 10% of cell sites remained operational](https://www.telecomstechnews.com/news/how-to-achieve-reliable-communication-in-emergency-scenarios/). The Asheville region was widely described as a "blackout zone" — no power, no cell service, no internet, roads impassable.

**Why mesh was used:**
There was no pre-deployed mesh infrastructure in the affected area before Helene. What emerged was entirely organic and community-driven — people who already had Meshtastic devices began using them in the days and weeks following the storm. [In the weeks after Helene hit, local groups began adding off-grid radio options including Meshtastic to their emergency playbooks](https://ncmesh.net/learn/). The NC Mesh community at [ncmesh.net](https://ncmesh.net) grew directly from this experience, now building out [a state-wide network of grid and solar-powered Meshtastic radios across North Carolina](https://ncmesh.net/learn/).

In the mountains around Asheville, [MeshAVL](https://meshavl.com) emerged as a local hub specifically focused on MeshCore and Meshtastic for the mountain terrain — emphasizing that the Appalachian landscape creates the same radio propagation dynamics as Vermont's Green Mountains, where ridgeline nodes dramatically outperform valley placements.

**What worked:**
- [Mesh networks carried mutual-aid traffic for days when commercial networks were down](https://dev.to/noperai42eng/how-to-survive-an-infrastructure-meltdown-with-meshtastic-and-meshcore-2026-dej) — message types like "family safe at shelter," "route 19 closed," "water at community center," "medic needed at 41st and Oak"
- Devices with solar charging or large battery reserves operated for days without grid power
- The mesh continued functioning as a standalone local network even when internet was fully unavailable
- People who already had devices were able to coordinate mutual aid effectively

**What didn't work:**
- [During the response, the Western NC mesh briefly became unusable when newcomers spammed status updates every 30 seconds — the radios still worked but the network was full of low-value chatter that crowded out actual emergency traffic](https://dev.to/noperai42eng/how-to-survive-an-infrastructure-meltdown-with-meshtastic-and-meshcore-2026-dej)
- No pre-deployed infrastructure meant early adopters were island nodes with no mesh to connect to — they had to find each other organically
- Most of the value came in the days and weeks *after* the disaster, not immediately, because density of devices was too low at first
- No operating conventions meant no channel discipline — the network degraded under load from well-intentioned but untrained users

**Key lesson for Vermont:**
The infrastructure needs to exist *before* the disaster. The NC case shows that organic post-event adoption works eventually, but there's a critical gap in the immediate aftermath when people most need communication and node density is lowest. A pre-deployed Burlington mesh with documented operating conventions would have been immediately useful during Irene and the 2023 floods — not gradually useful over weeks.

---

## Case Study 2: Austin Mesh — Austin, Texas (2021–ongoing)

**What happened:**
[Austin Mesh](https://www.austinmesh.org) was founded in the wake of Winter Storm Uri in February 2021, when widespread power failures left Austin residents without electricity, heat, or communication for days. The stated goal from the beginning was to build [a city-wide text messaging system that functions without any external infrastructure — no power, no cell phone towers, no internet](https://www.austinmesh.org/learn/).

Austin Mesh is now one of the most thoroughly documented community mesh deployments in the United States, with [coverage across 2,600 square miles](https://dev.to/noperai42eng/how-to-survive-an-infrastructure-meltdown-with-meshtastic-and-meshcore-2026-dej) and published operating conventions, technical guides, and firmware comparison documentation.

**Why mesh was used:**
[While first responders have access to proprietary emergency communication systems, ordinary citizens have no equivalent](https://www.austinmesh.org/learn/). Austin Mesh explicitly frames this as the equity problem — commercial cellular and internet infrastructure failed exactly the people who could least afford alternatives. A community-owned, open-source mesh with no subscription fees and sub-$100 device costs was accessible where proprietary alternatives were not.

The 2024 Texas floods provided further validation — [real-world deployments during the 2025 Texas floods showed mesh networks carrying mutual-aid traffic for days when commercial networks were down](https://dev.to/noperai42eng/how-to-survive-an-infrastructure-meltdown-with-meshtastic-and-meshcore-2026-dej).

**What worked:**
- [A solar-powered repeater infrastructure on high points across Austin provides backbone coverage that personal devices connect to, rather than requiring device-to-device direct links](https://www.austinmesh.org/)
- Community-driven model with no central administration scaled organically as more residents added nodes
- Austin Mesh has [developed and published detailed operating conventions](https://www.austinmesh.org/learn/meshcore-vs-meshtastic/) covering channel discipline, firmware selection, and node configuration — directly applicable to other cities
- The transition from Meshtastic to hybrid Meshtastic/MeshCore is thoroughly documented, providing a roadmap for any community network planning for scale

**What didn't work / ongoing challenges:**
- [Austin Mesh explicitly discourages MQTT bridging because busy MQTT servers can quickly overwhelm nodes and flood the entire network with traffic rendering local communications difficult or impossible](https://www.austinmesh.org/learn/) — this has to be an intentional design decision, not an afterthought
- [Terrain creates hard limits — hill/valley terrain in Austin often needs many relays, and Meshtastic's default seven-hop ceiling has been a constraint for metro-scale coverage](https://www.austinmesh.org/learn/meshcore-vs-meshtastic/)
- Getting non-technical residents to understand and follow operating conventions is an ongoing challenge as the network grows

**Key lesson for Vermont:**
Austin Mesh's published operating conventions and firmware comparison documentation at [austinmesh.org](https://www.austinmesh.org) are worth reading before finalizing Vermont's deployment approach. Their experience transitioning from Meshtastic to a hybrid MeshCore architecture as the network scaled is directly applicable to Burlington's growth trajectory. Don't reinvent what Austin has already documented.

---

## Case Study 3: Jefferson County, Florida — Municipal CERT Proposal (March 2025)

**What happened:**
In March 2025, the [Jefferson County Community Emergency Response Team proposed Meshtastic to the Monticello City Council](https://www.wtxl.com/news/local-news/in-your-neighborhood/monticello/monticello-council-considers-new-emergency-communication-system-proposal) as a formal emergency communication backup system. This is one of the clearest documented examples of mesh networking moving from community hobby to official municipal emergency management proposal.

**Why mesh was used:**
The proposal explicitly cited [successful Meshtastic deployments in North Carolina and Tennessee after Hurricane Helene wiped out first responder communication systems](https://www.wtxl.com/news/local-news/in-your-neighborhood/monticello/monticello-council-considers-new-emergency-communication-system-proposal). The CERT program manager described the goal: ["small devices that we can deploy easily to reestablish a network within hours after a storm if we had lost all other methods of communication."](https://www.wtxl.com/news/local-news/in-your-neighborhood/monticello/monticello-council-considers-new-emergency-communication-system-proposal)

The proposed deployment method was novel — [solar-powered devices attached by drones to the tops of water towers throughout the county](https://www.wtxl.com/news/local-news/in-your-neighborhood/monticello/monticello-council-considers-new-emergency-communication-system-proposal), creating instant elevated infrastructure without needing building access agreements. Funding was proposed through [grants from Volunteer Florida and other organizations](https://www.wtxl.com/news/local-news/in-your-neighborhood/monticello/monticello-council-considers-new-emergency-communication-system-proposal).

**What worked:**
- The ~$100 per node cost made a compelling budget case to elected officials — this is infrastructure that fits within existing emergency management budgets
- Framing around documented disaster failures (Helene) rather than technology capabilities resonated with the council
- Grant funding through existing emergency management channels made this a $0 ask from the municipal budget
- Water towers as deployment infrastructure is an elegant solution — city-owned, elevated, already have access agreements, distributed across the service area

**What didn't work / open questions:**
- This is a proposal, not a completed deployment — the outcome of the council decision is not publicly documented
- Drone-based deployment is operationally interesting but adds complexity that a simpler pole-mount or rooftop installation avoids
- No published technical specifications for what was proposed — the news coverage is thin on implementation details

**Key lesson for Vermont:**
This is the template for the Vermont Emergency Management conversation. A CERT-style proposal framed around documented Vermont disasters (Irene, 2023 floods), citing the North Carolina and Jefferson County examples, funded through FEMA BRIC or Vermont Emergency Management grants, with node placement on city-owned infrastructure like water towers or DPW buildings — this is exactly the pitch. The municipal water tower deployment idea is directly applicable to Vermont towns without UVM-style institutional partners.

---

## Case Study 4: Iberian Peninsula Blackout — Spain and Portugal (April 2025)

**What happened:**
On April 28, 2025, [a substation failure in Granada, Spain triggered a cascading grid collapse across the Iberian Peninsula](https://en.wikipedia.org/wiki/2025_Iberian_Peninsula_blackout). Within five seconds, power failed across Spain and Portugal. Mobile networks failed almost immediately as battery backups ran out — [one Portuguese operator saw more than 90 percent of subscribers lose service for over 24 hours](https://broadbandbreakfast.com/iberian-blackout-highlights-gaps-in-telecom-network-resiliency/). [At least one person died when her home ventilator ran out of battery and emergency services couldn't reach her in time](https://en.wikipedia.org/wiki/2025_Iberian_Peninsula_blackout).

[Community posts reported active Meshtastic use during the blackout — people who had deployed solar-powered nodes stayed connected](https://aiv2.eu/blackout-meshtastic-off-grid-communication/) and coordinated emergency help when cellular was unavailable.

**Why mesh was relevant:**
[The April 2025 Iberian blackout showed how fragile connected infrastructure really is — millions lost communication for hours](https://www.wave-access.com/public_en/blog/when-the-grid-goes-dark-meshtastic-for-resilient-networks/). The key structural problem the blackout exposed is one that Vermont already knows well from its own experience: [communications depend on the availability of electricity, and even when telecommunications networks remain technically operational, service can fail simply because equipment in homes or mobile towers loses power](https://bip.inesctec.pt/en/inesctecwatch/energy-and-telecommunications-in-times-of-crisis-how-can-portugal-prepare-for-the-next-extreme-events/).

**What worked:**
- [Meshtastic nodes with solar charging and battery buffers remained operational throughout the outage, providing communication where cellular was unavailable](https://www.wave-access.com/public_en/blog/when-the-grid-goes-dark-meshtastic-for-resilient-networks/)
- [People who had pre-deployed solar nodes across cities stayed connected and could coordinate while neighbors with only cellular access were isolated](https://www.wave-access.com/public_en/blog/when-the-grid-goes-dark-meshtastic-for-resilient-networks/)
- The event drove significant growth in European Meshtastic adoption — the Netherlands, Germany, Poland, and Portugal all saw expanded community deployments in the months following

**What didn't work:**
- Mesh node density was too low in most areas to provide city-wide coverage — only the small percentage of people who already had devices benefited
- No public awareness of the technology meant most people didn't know mesh communication was available even in areas where nodes existed
- The event happened too fast for emergency deployment of new nodes — pre-deployment is the only viable strategy

**Key lesson for Vermont:**
This case makes the clearest argument for pre-deployment as a policy decision rather than a community hobby. Vermont's cellular infrastructure has the same dependency on grid power as the Iberian Peninsula. Solar-powered mesh nodes on fixed infrastructure are the only communication layer that survives a prolonged grid outage — and they need to be deployed and known about before the event, not after.

---

## Conclusions: What This Means for Vermont

These four cases, taken together, point toward a clear deployment strategy for Vermont. The lessons aren't theoretical — they're drawn from documented operational experience.

### What the cases agree on

**1. Pre-deployment is the only effective strategy.**
Every case shows the same pattern: mesh networks are immediately useful for people who already have devices and already know how to use them. They're gradually useful for everyone else, over days and weeks, as node density builds. Vermont's history of sudden infrastructure failures — Irene, the 2023 floods, ice storms — means there's no "days and weeks" to build a network after the event. The Burlington infrastructure needs to exist before the next disaster.

**2. Infrastructure nodes matter more than personal devices.**
The Austin Mesh model — solar-powered repeaters on high points as backbone, personal devices as endpoints — consistently outperforms the "everyone is a router" approach. Burlington needs 3–5 well-placed fixed nodes before distributing personal devices to anyone.

**3. Operating conventions are as important as hardware.**
The North Carolina case shows what happens when a mesh network grows without operating conventions — channel congestion from well-intentioned users renders the network unusable at the moment it's needed most. Austin Mesh's published conventions at [austinmesh.org](https://www.austinmesh.org) are worth adopting directly, with Vermont-specific modifications, before the Burlington network goes public.

**4. The municipal framing works.**
Jefferson County's CERT proposal demonstrates that local government will engage with this technology when it's framed around documented local disasters and presented with a credible cost and deployment plan. Vermont Emergency Management is the right first call — not because they'll fund the Burlington pilot, but because their involvement creates the institutional relationships needed for node placement on state and municipal infrastructure.

**5. Grant funding is available and proven.**
Jefferson County used Volunteer Florida grants. NC Mesh used community donations and ARPA funding. The pattern of using existing emergency preparedness grant programs to fund mesh infrastructure is established. FEMA BRIC, Vermont Emergency Management grants, and Vermont EPSCoR are all viable funding paths that don't require new programs or novel arguments.

### How this shapes Vermont's approach

**Start with Burlington, frame for the state.**
The Burlington pilot is the proof of concept. But design it from the beginning to be extensible to Montpelier, Barre, St. Johnsbury, and the ridgeline backbone. The documentation, operating conventions, and stakeholder relationships built during the Burlington pilot are the durable output — not just the nodes.

**Meshtastic first, MeshCore when we scale.**
Austin Mesh's firmware comparison documentation at [austinmesh.org/learn/meshcore-vs-meshtastic](https://www.austinmesh.org/learn/meshcore-vs-meshtastic/) makes the transition point clear: Meshtastic for getting started and building community adoption, MeshCore when the network grows past ~50 active nodes or when formal municipal deployment requires defined infrastructure roles. The hardware is the same either way.

**Use city-owned infrastructure for node placement.**
Jefferson County's water tower approach is directly applicable to Vermont municipalities. Burlington DPW buildings, Vermont Agency of Transportation maintenance facilities, Vermont State Police barracks, and Vermont State Parks fire towers are all city or state-owned elevated infrastructure that could host solar nodes through an interagency agreement rather than a lease negotiation.

**VERSO's role is infrastructure and documentation, not management.**
The Hawaii and Austin models are instructive: build the backbone, publish the channel key and joining instructions, let adoption happen organically. VERSO isn't managing a communications network — we're building and documenting open public infrastructure, the same way we build and document other open Vermont research infrastructure. ORCA students do the implementation work. The community does the rest.

**The research angle is real.**
None of the existing case studies include edge AI on gateway nodes, formal GIS coverage modeling with published methodology, or integration with LoRaWAN sensor networks for flood and weather monitoring. Vermont can be the first documented case of all three together — which is publishable, grant-fundable, and positions VERSO as a national reference for this specific infrastructure intersection.

---

## Further Reading

- [NC Mesh](https://ncmesh.net) — North Carolina's statewide community mesh, born from Helene
- [Austin Mesh](https://www.austinmesh.org) — Most thoroughly documented US city-scale deployment
- [MeshAVL](https://meshavl.com) — Asheville/Western NC mesh community, mountain terrain focus
- [Wave Access on Meshtastic resilience](https://www.wave-access.com/public_en/blog/when-the-grid-goes-dark-meshtastic-for-resilient-networks/) — Iberian blackout analysis
- [Broadband Breakfast: Iberian Blackout Telecom Analysis](https://broadbandbreakfast.com/iberian-blackout-highlights-gaps-in-telecom-network-resiliency/) — Infrastructure resilience analysis
- [DEV Community: Infrastructure Meltdown Guide](https://dev.to/noperai42eng/how-to-survive-an-infrastructure-meltdown-with-meshtastic-and-meshcore-2026-dej) — Practical deployment guide with Helene/Texas flood case summaries
- [NodakMesh](https://nodakmesh.org) — North Dakota rural mesh, comparable geography to rural Vermont

---

*Compiled by VERSO / University of Vermont, May 2026. Part of the Vermont Community Mesh Network project.*
