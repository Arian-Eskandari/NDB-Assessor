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

QUESTIONS = {
    # Gate 1 — Eligible data breach
    "g1_personal_info": (
        "Gate 1 — Eligible data breach\n"
        "Did the incident involve personal information held by your organisation?"
    ),
    "g1_unauthorised": (
        "Was there unauthorised access to, unauthorised disclosure of, "
        "or loss of that personal information?"
    ),

    # Gate 2 — Likely serious harm
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
    "g3_remedied": (
        "Gate 3 — Exemptions\n"
        "Has the organisation taken action that removes the likelihood of "
        "serious harm before individuals are affected?\n"
        "(e.g. data was encrypted and the key was not compromised)"
    ),
    "g3_law_enforcement": (
        "Has a law enforcement body requested that notification be delayed "
        "or not made?"
    ),
    "g3_other_law": (
        "Does another Australian law prohibit the disclosure "
        "(e.g. certain intelligence legislation)?"
    ),
}

DETAILS = {
    "organisation":   "Organisation name:",
    "incident_date":  "Date incident was discovered (DD/MM/YYYY):",
    "incident_desc":  "Brief description of the incident:",
    "data_types":     "What types of personal information were involved?",
    "individuals":    "Estimated number of individuals affected:",
    "assessor_name":  "Your name (assessor):",
}