import spacy
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List


def _load_model(name: str):
    try:
        return spacy.load(name)
    except OSError:
        print(f"Model not found. Downloading {name}...")
        import os
        os.system(f"python -m spacy download {name}")
        return spacy.load(name)


nlp_lg = _load_model("en_core_web_lg")
nlp_sm = _load_model("en_core_web_sm")
nlp_da = _load_model("da_core_news_lg")


app = FastAPI()


class ExtractPersonsRequest(BaseModel):
    text: str


class ExtractPersonsResponse(BaseModel):
    persons: List[str]


def _extract_with_model(nlp, text: str, titles: set) -> list[str]:
    doc = nlp(text)
    persons = []
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            start, end = ent.start_char, ent.end_char
            before = text[start - 1] if start > 0 else ""
            after = text[end] if end < len(text) else ""
            entity_text = ent.text
            if before in ('"', "'"):
                if after == before or entity_text.endswith(before):
                    continue

            preceding = text[:start].rstrip()
            if preceding.lower().endswith("the"):
                continue

            person_name = ent.text.strip()
            tokens = person_name.split()
            if tokens and tokens[0].lower() in titles:
                person_name = " ".join(tokens[1:])
            if person_name:
                persons.append(person_name)
    return persons


def campusai_extract_persons(text: str) -> list[str]:
    titles = {"mr", "mrs", "ms", "miss", "dr", "prof", "professor", "sir", "madam", "rev", "reverend", "hon", "honorable"}

    lg_results = _extract_with_model(nlp_lg, text, titles)
    sm_results = _extract_with_model(nlp_sm, text, titles)
    da_results = _extract_with_model(nlp_da, text, titles)

    combined = list(lg_results)
    seen = {name.lower() for name in combined}
    for name in sm_results + da_results:
        if name.lower() not in seen:
            combined.append(name)
            seen.add(name.lower())

    return combined


@app.post("/v1/extract-persons")
async def extract_persons_endpoint(request: ExtractPersonsRequest) -> ExtractPersonsResponse:
    persons = campusai_extract_persons(request.text)
    return ExtractPersonsResponse(persons=persons)