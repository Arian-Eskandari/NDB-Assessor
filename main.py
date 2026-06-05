import sys
import os
from datetime import date
from colorama import init, Fore, Style
from questions import QUESTIONS, DETAILS, INTRO
from assessor import assess
from reporter import generate_report

init(autoreset=True)


def ask_yn(prompt: str) -> bool:
    while True:
        raw = input(f"\n{Fore.CYAN}{prompt}{Style.RESET_ALL}\n> ").strip().lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print(f"{Fore.YELLOW}Please enter y or n.{Style.RESET_ALL}")


def ask_text(prompt: str) -> str:
    while True:
        raw = input(f"\n{Fore.CYAN}{prompt}{Style.RESET_ALL}\n> ").strip()
        if raw:
            return raw
        print(f"{Fore.YELLOW}This field cannot be empty.{Style.RESET_ALL}")


def print_outcome(notifiable: bool, summary: str):
    print("\n" + "=" * 50)
    if notifiable:
        print(f"{Fore.RED}{Style.BRIGHT}  RESULT: NOTIFIABLE DATA BREACH{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}{Style.BRIGHT}  RESULT: NOTIFICATION NOT REQUIRED{Style.RESET_ALL}")
    print(f"  {summary}")
    print("=" * 50)


def main():
    print(Fore.BLUE + INTRO + Style.RESET_ALL)

    # Collect incident details first
    details = {}
    for key, prompt in DETAILS.items():
        details[key] = ask_text(prompt)

    print(f"\n{Fore.BLUE}── Beginning eligibility assessment ──{Style.RESET_ALL}")

    # Collect gate answers
    answers = {}
    for key, prompt in QUESTIONS.items():
        answers[key] = ask_yn(prompt)

        # Early exit: if g1 gates fail, skip remaining questions
        if key == "g1_unauthorised" and not answers[key]:
            break
        if key == "g2_physical_risk":
            # Calculate preliminary harm score before asking Gate 3
            harm_keys = ["g2_sensitive","g2_volume","g2_malicious",
                         "g2_identity_risk","g2_financial_risk","g2_physical_risk"]
            score = sum(1 for k in harm_keys if answers.get(k))
            if score < 2:
                break  # Skip Gate 3 — harm threshold not met

    # Run assessment
    result = assess(answers)
    print_outcome(result.notifiable, result.outcome_summary)

    # Generate report
    filename = (
        f"NDB_Assessment_{details['organisation'].replace(' ', '_')}"
        f"_{date.today().strftime('%Y%m%d')}.docx"
    )
    generate_report(details, result, filename)

    print(f"\n{Fore.BLUE}Assessment complete. Retain the report for your incident register.{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()