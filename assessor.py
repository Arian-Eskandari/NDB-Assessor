"""
# assessor.py
# ─────────────────────────────────────────────────────────────
This is the core decision engine for the NDB scheme assessment.
# Implements the three-gate eligibility test defined in Part IIIC of the
  Privacy Act 1988 (Cth) and the OAIC's NDB scheme guidelines.

# No I/O happens here — this module only receives a dict of answers and 
returns structured result objects. This keeps the logic cleanly separated 
from the CLI (main.py) and the report generator (reporter.py).
# ─────────────────────────────────────────────────────────────

"""


from dataclasses import dataclass
from typing import Optional


# GateResult stores the outcome of a single gate evaluation.
# passed=True means the gate condition was satisfied.
# reason is a plain-English explanation written into the report.

@dataclass
class GateResult:
    passed: bool
    reason: str

# Assessment is the complete result object returned by assess().
# It holds the result of each gate and the final notifiability verdict.
# gate2 and gate3 are Optional because the assessment exits early
# if a prior gate fails — those gates are never evaluated.

@dataclass
class Assessment:
    gate1: GateResult
    gate2: Optional[GateResult]  #None if Gate 1 failed
    gate3: Optional[GateResult]  #None if Gaate 1 or Gate 2 failed
    notifiable: bool  #True only if all three gates pass
    outcome_summary: str  #One-line verdict for terminal output
    harm_score: int        # 0-6, drives risk rating in report


def assess(answers: dict) -> Assessment:
    """
    Apply the three NDB eligibility gates from Part IIIC
    of the Privacy Act 1988 (Cth) and the OAIC guidelines.

    Gate 1 — Eligible data breach (s26WE):
        Was personal information accessed, disclosed, or lost
        without authorisation?

    Gate 2 — Likely serious harm (s26WG):
        Would a reasonable person expect serious harm to result?
        Scored across six OAIC-defined harm factors; 2+ = threshold met.

    Gate 3 — No exemption applies:
        Remedial action (s26WF), law enforcement request (s26WN),
        or legal prohibition must NOT be present.

    Returns an Assessment dataclass with full gate-by-gate reasoning.

    """

    # ── Gate 1: Eligible data breach ──────────────────────────────
    """
    # If no personal information was involved, the incident cannot
    # be an eligible data breach under any circumstances — exit immediately.
    """

    if not answers["g1_personal_info"]:
        g1 = GateResult(
            passed=False,
            reason="No personal information was involved. "
                   "This is not an eligible data breach under the NDB scheme."
        )

        # gate2 and gate3 are None — they were never evaluated.
        # harm_score is 0 — no Gate 2 questions were reached.

        return Assessment(g1, None, None, False,
                          "Not notifiable — no personal information involved.", 0)

    # Personal info was present but no unauthorised event occurred.
    # An accidental internal view by an authorised employee, for example,
    # would not constitute unauthorised access.

    if not answers["g1_unauthorised"]:
        g1 = GateResult(
            passed=False,
            reason="There was no unauthorised access, disclosure, or loss. "
                   "Gate 1 not satisfied."
        )
        return Assessment(g1, None, None, False,
                          "Not notifiable — Gate 1 not satisfied.", 0)

    #Gate 1 passed - both conditions confirmed.
    g1 = GateResult(passed=True, reason="Unauthorised access/disclosure/loss of personal information confirmed.")

    # ── Gate 2: Likely to result in serious harm ──────────────────

    """
    # Count how many of the six OAIC harm factors are present.
    # Each factor independently increases the probability of serious harm.
    """
    harm_factors = [
        answers["g2_sensitive"],  #Sensitive categories of info involved
        answers["g2_volume"],  #Large number of individuals affected
        answers["g2_malicious"],  #Criminal or malicious intent behind breach
        answers["g2_identity_risk"],  #Information usable for identity fraud
        answers["g2_financial_risk"],  #Used for determine financial harm
        answers["g2_physical_risk"],  #Used to assess physical harm or harassment
    ]
    #Sum True values - each True answer contributes 1 to the score.
    harm_score = sum(1 for f in harm_factors if f)

    # Threshold: 2 or more factors = a reasonable person would likely
    # expect serious harm. Below 2 = threshold not met, exit early.
    # Note: This threshold is a practical interpretation of the OAIC's Act.
    # A reasonable person test: 2+ factors → likely serious harm
    if harm_score < 2:
        g2 = GateResult(
            passed=False,
            reason=f"Only {harm_score} harm factor(s) identified. "
                   "A reasonable person would likely not expect serious harm. "
                   "Gate 2 not satisfied."
        )
        return Assessment(g1, g2, None, False,
                          "Not notifiable — serious harm threshold not met.", harm_score)

    g2 = GateResult(
        passed=True,
        reason=f"{harm_score} of 6 harm factors present. "
               "A reasonable person would likely expect serious harm."
    )

    # ── Gate 3: No exemption applies ─────────────────────────────

    """
    # Exemption: remedial action (s26WF).
    # If the organisation acted quickly enough that no individualwas
    actually harmed (e.g. encrypted data, recalled email), notification 
    is not required.
    """
    if answers["g3_remedied"]:
        g3 = GateResult(
            passed=False,
            reason="Organisation has taken remedial action that removes the "
                   "likelihood of serious harm. Exemption under s26WF applies."
        )
        return Assessment(g1, g2, g3, False,
                          "Not notifiable — remedial action exemption applies.", harm_score)

    """
    # Exemption: law enforcement request (s26WN).
    # A police or intelligence body may request that notification
    be withheld to avoid compromising an active investigation.

    """
    if answers["g3_law_enforcement"]:
        g3 = GateResult(
            passed=False,
            reason="Law enforcement body has requested delay or non-notification. "
                   "Exemption under s26WN applies."
        )
        return Assessment(g1, g2, g3, False,
                          "Not notifiable — law enforcement exemption applies.", harm_score)

    """
    # Exemption: legal prohibition.
    # Certain Australian laws (e.g. intelligence legislation) may
    explicitly prohibit disclosure of breach information.
    """
    if answers["g3_other_law"]:
        g3 = GateResult(
            passed=False,
            reason="Another Australian law prohibits notification. "
                   "Exemption applies."
        )
        return Assessment(g1, g2, g3, False,
                          "Not notifiable — legal prohibition exemption applies.", harm_score)

    # No exceptions found - Gate 3 passes.
    g3 = GateResult(passed=True, reason="No exemptions identified.")

    """
    # All three gates satisfied — this is a notifiable data breach.
    # The organisation must notify the OAIC and affected individuals
    # within 30 days of becoming aware (s26WK).
    
    """
    return Assessment(g1, g2, g3, True,
                      "NOTIFIABLE — all three gates satisfied. "
                      "Notify OAIC and affected individuals within 30 days.", harm_score)