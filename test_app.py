import os
from main import campusai_extract_persons

def test_examples_from_prompt():
    examples = [
        "Ms Mette Frederiksen is in New York today.",
        "Einstein and von Neumann meet each other."
    ]
    expected = [
        ["Mette Frederiksen"],
        ["Einstein", "von Neumann"],
    ]
    for text, exp in zip(examples, expected):
        assert campusai_extract_persons(text) == exp