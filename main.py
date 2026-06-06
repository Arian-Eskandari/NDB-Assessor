"""
# main.py
# ─────────────────────────────────────────────────────────────
# Entry point for the NDB Breach Assessor CLI tool.
# Responsibilities:
#   1. Print the intro banner
#   2. Collect free-text incident details from the user
#   3. Ask all yes/no gate questions in order
#   4. Apply early-exit logic to skip irrelevant questions
#   5. Pass answers to assessor.assess() for the verdict
#   6. Print the outcome to the terminal
#   7. Call reporter.generate_report() to produce the .docx file
# ─────────────────────────────────────────────────────────────

"""

import sys
import os
from datetime import date
from colorama import init, Fore, Style
from questions import QUESTIONS, DETAILS, INTRO
from assessor import assess
from reporter import generate_report

# Initialise colorama — enables ANSI colour codes on Windows terminals.
# autoreset=True means colour resets automatically after each print.

init(autoreset=True)


def ask_yn(prompt: str) -> bool:

    """
    Ask a yes/no question and return True for yes, False for no.
    Loops until the user enters a valid response (y/yes or n/no).
    Prompt is displayed in cyan to distinguish questions from system text.
    """

    while True:
        raw = input(f"\n{Fore.CYAN}{prompt}{Style.RESET_ALL}\n> ").strip().lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        
        # Invalid input — ask again without crashing
        print(f"{Fore.YELLOW}Please enter y or n.{Style.RESET_ALL}")


def ask_text(prompt: str) -> str:

    """
    Ask for free-text input and return the stripped string.
    Loops until the user enters a non-empty value.
    Used for incident detail fields (org name, description, etc.).
    """
    while True:
        raw = input(f"\n{Fore.CYAN}{prompt}{Style.RESET_ALL}\n> ").strip()
        if raw:
            return raw
        print(f"{Fore.YELLOW}This field cannot be empty.{Style.RESET_ALL}")


def print_outcome(notifiable: bool, summary: str):
    """
    Print the final verdict to the terminal with colour coding.
    Red for notifiable (action required), green for not notifiable.
    Surrounded by a separator line for visual clarity.
    """
    print("\n" + "=" * 50)
    if notifiable:
        print(f"{Fore.RED}{Style.BRIGHT}  RESULT: NOTIFIABLE DATA BREACH{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}{Style.BRIGHT}  RESULT: NOTIFICATION NOT REQUIRED{Style.RESET_ALL}")
    print(f"  {summary}")
    print("=" * 50)


def main():

    #Print the intro banner from quesstions.py
    print(Fore.BLUE + INTRO + Style.RESET_ALL)

     # ── Step 1: Collect incident details ──────────────────────
    # These free-text fields populate the Word report header
    # and the draft OAIC notification statement.

    details = {}
    for key, prompt in DETAILS.items():
        details[key] = ask_text(prompt)

    print(f"\n{Fore.BLUE}── Beginning eligibility assessment ──{Style.RESET_ALL}")

    # ── Step 2: Collect gate answers ──────────────────────────
    # Iterate through QUESTIONS in order, storing each answer
    # in the answers dict by its key (e.g. "g1_personal_info").
    answers = {}
    for key, prompt in QUESTIONS.items():
        answers[key] = ask_yn(prompt)

        # Early exit: if g1 gates fail, skip remaining questions
        # If either g1 answer is No, Gate 1 has failed.
        # There is no point asking Gate 2 or Gate 3 questions —
        # the assessment is already determined to be non-notifiable.
        if key == "g1_unauthorised" and not answers[key]:
            break

        # Early exit after all Gate 2 questions are answered:
        # Calculate a preliminary harm score. If fewer than 2
        # factors are present, Gate 2 has failed — skip Gate 3.
        if key == "g2_physical_risk":
            # Calculate preliminary harm score before asking Gate 3
            harm_keys = ["g2_sensitive","g2_volume","g2_malicious",
                         "g2_identity_risk","g2_financial_risk","g2_physical_risk"]
            score = sum(1 for k in harm_keys if answers.get(k))
            if score < 2:
                break  # Skip Gate 3 — harm threshold not met


    # ── Step 3: Run the assessment ────────────────────────────
    # Pass the collected answers to the assessment engine.
    # assessor.assess() applies the three-gate logic and returns
    # a fully populated Assessment dataclass.
    result = assess(answers)

    # ── Step 4: Print the terminal verdict ────────────────────
    print_outcome(result.notifiable, result.outcome_summary)

    # ── Step 5: Generate the Word report ──────────────────────
    # Build a filename using the organisation name and today's date.
    # Spaces in the org name are replaced with underscores for the filename.

    filename = (
        f"NDB_Assessment_{details['organisation'].replace(' ', '_')}"
        f"_{date.today().strftime('%Y%m%d')}.docx"
    )

    #reporter.generate_report() writes the .docx to the current directory.
    generate_report(details, result, filename)

    print(f"\n{Fore.BLUE}Assessment complete. Retain the report for your incident register.{Style.RESET_ALL}\n")

# Standard Python entry point guard.
# Ensures main() only runs when this file is executed directly,
# not when it is imported as a module by another script.
if __name__ == "__main__":
    main()