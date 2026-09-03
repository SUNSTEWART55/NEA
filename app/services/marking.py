"""
marking.py

Wraps the ML marking logic behind a stable interface so the rest of
the app doesn't need to know how marking actually works.

STUB: currently returns a random result. Replace the body of
mark_answer() with a call into the real ML pipeline once it's ready
-- the rest of the app never needs to change, since it only relies
on this function's signature.
"""

import random


def mark_answer(expected_answer: int, image_path: str) -> bool:
    """
    Given the correct answer and a path to an image of the student's
    written work, return True if the answer is judged correct.
    """
    # TODO: replace with real marking once the CV/ML pipeline is fixed
    return random.choice([True, False])