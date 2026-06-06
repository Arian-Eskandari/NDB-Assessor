"""
# This code centralises all user-facing text for the NDB assessor tool.
# Keeping questions separate from logic means you can update
# OAIC wording without touching the assessment engine.
# ─────────────────────────────────────────────────────────────


# Intro banner printed at the start of every assessment run.
# Gives the user legal context before any questions are asked.

"""


INTRO = """
=================================================
  AU Privacy Act NDB Scheme — Breach Assessor
  Based on Part IIIC, Privacy Act 1988 (Cth)
=================================================
This tool walks you through the three eligibility
gates and produces a draft assessment report.

Answer each question y (yes) or n (no).
Press Enter to confirm each answer.
"""

"""
QUESTIONS is an ordered dictionary of all yes/no prompts.

# Each key maps to a prompt string shown to the user in main.py.
# Keys are namespaced by gate (g1_, g2_, g3_) so the assessor
# logic in assessor.py can reference them unambiguously.

"""

QUESTIONS = {
    # Gate 1 — Eligible data breach
    # Both g1 questions must be answered Yes for Gate 1 to pass.
    # If either is No, the assessment ends — no notification required.

    "g1_personal_info": (
        "Gate 1 — Eligible data breach\n"
        "Did the incident involve personal information held by your organisation?"
    ),
    "g1_unauthorised": (
        "Was there unauthorised access to, unauthorised disclosure of, "
        "or loss of that personal information?"
    ),

    # Gate 2 — Likely serious harm

    # Six harm factors drawn from the OAIC's reasonable person test.
    # The assessor scores how many are present — 2+ triggers Gate 2.
    # Each factor independently raises the probability of serious harm.

    "g2_sensitive": (
        "Gate 2 — Likely serious harm\n"
        "Does the information include sensitive data?\n"
        "(health, financial, government ID, biometric, sexual orientation, etc.)"
    ),
    "g2_volume": (
        "Did the breach affect more than 50 individuals?"
    ),
    "g2_malicious": (
        "Was the breach the result of a malicious or criminal act "
        "(e.g. ransomware, hacking, insider theft)?"
    ),
    "g2_identity_risk": (
        "Could the information reasonably be used to commit identity fraud?"
    ),
    "g2_financial_risk": (
        "Could the information reasonably be used to cause financial harm "
        "to affected individuals?"
    ),
    "g2_physical_risk": (
        "Could the disclosure put any individual at risk of physical harm "
        "or harassment?"
    ),

    # Gate 3 — Exemptions

    # If any exemption applies, notification is not required even if Gates 1 and 2 were both satisfied.
    # Each maps to a specific section of the Privacy Act 1988.

    "g3_remedied": (
        "Gate 3 — Exemptions\n"
        "Has the organisation taken action that removes the likelihood of "
        "serious harm before individuals are affected?\n"
        "(e.g. data was encrypted and the key was not compromised)"

        # Exemption reference: s26WF Privacy Act 1988
    ),
    "g3_law_enforcement": (
        "Has a law enforcement body requested that notification be delayed "
        "or not made?"

        # Exemption reference: s26WN Privacy Act 1988
    ),
    "g3_other_law": (
        "Does another Australian law prohibit the disclosure "
        "(e.g. certain intelligence legislation)?"
    ),
}

# DETAILS holds prompts for the free-text incident fields.
# These are collected before the gate questions and injected
# into the Word report by reporter.py.

DETAILS = {
    "organisation":   "Organisation name:",
    "incident_date":  "Date incident was discovered (DD/MM/YYYY):",
    "incident_desc":  "Brief description of the incident:",
    "data_types":     "What types of personal information were involved?",
    "individuals":    "Estimated number of individuals affected:",
    "assessor_name":  "Your name (assessor):",
}