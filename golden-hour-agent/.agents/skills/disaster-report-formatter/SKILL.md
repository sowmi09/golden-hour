---
name: disaster-report-formatter
description: Formats all Golden Hour disaster situation reports into a consistent 5-packet structure for disaster response teams.
---
<!--
This is a custom Antigravity Agent Skill following the progressive disclosure pattern from Day 3.
It packages consistent report structures and formatting rules, ensuring they are only loaded
when the skill is active, minimizing context window footprint and reducing LLM instruction load.
-->

# Skill: disaster-report-formatter
## Description
Formats all Golden Hour disaster situation reports into a consistent 
5-packet structure for disaster response teams. Activate this skill 
whenever producing a disaster situation report.

## When to Use
Use this skill when:
- Producing a flood situation report
- Producing an earthquake situation report  
- Producing any natural disaster response brief

## Output Format
Always structure every disaster report exactly as follows:

---
GOLDEN HOUR [DISASTER TYPE] RESPONSE BRIEF
Event: [location, event description, magnitude if applicable]
Alert Level: [severity level]
Data Source: [cite exact API and data source]
Generated: [timestamp]
Mode: [Anticipate Mode for floods / Respond Mode for earthquakes]
---

PACKET 1 - FOR: District/Regional Commander
[decisions, population at risk, severity zones, resource activation]

PACKET 2 - FOR: Search & Rescue Field Commander
[deployment zones, building collapse risk, equipment, access routes]

PACKET 3 - FOR: Hospital & Medical Coordinator
[injury types, casualty estimates, hospitals to activate, blood bank alert]

PACKET 4 - FOR: Transport & Logistics Coordinator
[road damage, alternative routes, heavy machinery, helicopter needs]

PACKET 5 - FOR: Public Communication Officer
[draft public advisory, what NOT to do, helpline numbers, evacuation guidance]

---
DISCLAIMER: AI-generated assessment from public data [cite source].
Verify with official agencies before operational deployment.
---

## Rules
- Always use country-appropriate team names
- Never use Indian team names for non-Indian events
- Always cite the exact data source and event ID
- Always include the disclaimer
- Never claim to predict earthquakes
- Always state confidence level based on data quality
