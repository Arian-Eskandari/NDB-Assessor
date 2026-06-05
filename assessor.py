from dataclasses import dataclass
from typing import Optional


@dataclass
class GateResult:
    passed: bool
    reason: str


@dataclass
class Assessment:
    gate1: GateResult
    gate2: Optional[GateResult]
    gate3: Optional[GateResult]
    notifiable: bool
    outcome_summary: str
    harm_score: int        # 0-6, drives risk rating in report


def assess(answers: dict) -> Assessment:
    """
    Apply the three NDB eligibility gates from Part IIIC
    of the Privacy Act 1988 (Cth) and the OAIC guidelines.
    """

    # ── Gate 1: Eligible data breach ──────────────────────────────
    if not answers["g1_personal_info"]:
        g1 = GateResult(
            passed=False,
            reason="No personal information was involved. "
                   "This is not an eligible data breach under the NDB scheme."
        )
        return Assessment(g1, None, None, False,
                          "Not notifiable — no personal information involved.", 0)

    if not answers["g1_unauthorised"]:
        g1 = GateResult(
            passed=False,
            reason="There was no unauthorised access, disclosure, or loss. "
                   "Gate 1 not satisfied."
        )
        return Assessment(g1, None, None, False,
                          "Not notifiable — Gate 1 not satisfied.", 0)

    g1 = GateResult(passed=True, reason="Unauthorised access/disclosure/loss of personal information confirmed.")

    # ── Gate 2: Likely to result in serious harm ──────────────────
    harm_factors = [
        answers["g2_sensitive"],
        answers["g2_volume"],
        answers["g2_malicious"],
        answers["g2_identity_risk"],
        answers["g2_financial_risk"],
        answers["g2_physical_risk"],
    ]
    harm_score = sum(1 for f in harm_factors if f)

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
    if answers["g3_remedied"]:
        g3 = GateResult(
            passed=False,
            reason="Organisation has taken remedial action that removes the "
                   "likelihood of serious harm. Exemption under s26WF applies."
        )
        return Assessment(g1, g2, g3, False,
                          "Not notifiable — remedial action exemption applies.", harm_score)

    if answers["g3_law_enforcement"]:
        g3 = GateResult(
            passed=False,
            reason="Law enforcement body has requested delay or non-notification. "
                   "Exemption under s26WN applies."
        )
        return Assessment(g1, g2, g3, False,
                          "Not notifiable — law enforcement exemption applies.", harm_score)

    if answers["g3_other_law"]:
        g3 = GateResult(
            passed=False,
            reason="Another Australian law prohibits notification. "
                   "Exemption applies."
        )
        return Assessment(g1, g2, g3, False,
                          "Not notifiable — legal prohibition exemption applies.", harm_score)

    g3 = GateResult(passed=True, reason="No exemptions identified.")

    return Assessment(g1, g2, g3, True,
                      "NOTIFIABLE — all three gates satisfied. "
                      "Notify OAIC and affected individuals within 30 days.", harm_score)