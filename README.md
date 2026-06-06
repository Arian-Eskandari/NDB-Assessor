---- NDB Breach Assessor ----

A command-line and web-based assessment tool that determines whether a data incident meets the mandatory notification threshold under Australia's Notifiable Data Breaches (NDB) scheme — Part IIIC of the Privacy Act 1988 (Cth).

---- Overview ----

When an organisation suffers a data incident, Australian privacy law requires a structured eligibility assessment before any notification decision is made. This process is time-sensitive, legally consequential,
and often handled without formal tooling — particularly in small-to-medium organisations without a dedicated privacy team.
This tool operationalises the OAIC's three-gate eligibility test into a guided interview.
It scores harm severity across six risk factors, applies all statutory exemptions, and produces a documented assessment report with a pre-filled draft OAIC notification statement
— giving privacy officers and GRC analysts a defensible, auditable record of their decision.

The assessment has three sequential gates:
- Gate 1 (based on s26WE): Was personal information accessed, disclosed, or lost without authorisation?
- Gate 2 (based on s26WG): Would a reasonable person expect serious harm to result?
- Gate 3 (based on s26WE and s26WN): Does an exemption apply?

NOTE: If the assessment exits a gate with a negative finding, subsequent gates are skipped and the tool immediately returns a non-notifiable determination.
If all three gates are satisfied, the tool flags the incident as a notifiable data breach and generates the required documentation.


---- Output ----

Non-notifiable outcome:

Gate-by-gate determination with plain-English reasoning
Documented record suitable for the organisation's incident register

Notifiable outcome:

Gate-by-gate determination with plain-English reasoning
Harm severity rating (Low / Medium / High / Critical) scored across six OAIC-defined factors
Mandatory action checklist with statutory deadlines
Draft OAIC notification statement pre-populated with incident details, ready for legal review before submission.

---- Project structure ----

ndb-assessor/
├── main.py          — CLI entry point, user interview and flow control
├── assessor.py      — Three-gate decision engine, returns Assessment dataclass
├── reporter.py      — Word report generator using python-docx
├── questions.py     — All question text and field prompts, centralised
├── requirements.txt
│
├── index.html       — Web interface markup, six-step guided form
├── styles.css       — Styling, layout, and component design
├── app.js           — Assessment logic, validation, and result rendering
│
└── README.md


Tech stack
- CLI: Python 3, colorama
- Report generation: python-docx
- Web interface: HTML, CSS, JavaScript — no frameworks or build tools
- AI: Claude (free tier is sufficient)

---- Legal basis ----

Built against the OAIC's Notifiable Data Breaches scheme guidelines and the following provisions of the Privacy Act 1988 (Cth):

s26WE — definition of an eligible data breach
s26WF — remedial action exemption
s26WG — serious harm assessment criteria
s26WK — 30-day notification deadline
s26WN — law enforcement exemption

---- Disclaimer ----

This tool is built for educational and portfolio purposes. 
It does not constitute legal advice. Consult a qualified privacy lawyer or the OAIC before making any notification decisions in a real incident.

