"""
Unit 2: decide whether an answer counts as correct.

run_eval.py looks for a function `judge(question, expects, answer, results)
-> bool` in this file. Once it exists, the Run columns in results/*.md carry
pass/fail instead of blanks.

A plain substring check (`expects.lower() in answer.lower()`) is too strict
for this corpus: the model sometimes writes "7:00 pm" where `expects` says
"7:00pm" — a formatting difference with the same length as a wrong digit
("8:00pm"), so raw partial_ratio scores them identically (~83) and can't
tell "reformatted" from "wrong" (verified this against actual model output
before picking a threshold — see README's Diagnoses section). Stripping
whitespace from both strings before comparing fixes the spacing case
without opening the door to the wrong-digit case, which still scores ~83
and stays below the threshold.

rapidfuzz's partial_ratio scores how well `expects` matches ANY substring
of the answer, so close rewordings still pass while an answer that never
mentions the expected fact still fails.
"""

import re

from rapidfuzz import fuzz

import gate

FUZZY_THRESHOLD = 85  # 0-100. Below this, call it a miss rather than a match.


def _normalize(text: str) -> str:
    return re.sub(r"\s+", "", text.lower())


def judge(question: str, expects: str, answer: str, results) -> bool:
    if answer == gate.REFUSAL:
        return False
    if not expects:
        return True
    return fuzz.partial_ratio(_normalize(expects), _normalize(answer)) >= FUZZY_THRESHOLD
