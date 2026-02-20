from fastapi import FastAPI, File, UploadFile

app = FastAPI()

@app.post("/v1/extract-persons")
async def campusai_extract_persons(text: str):
    