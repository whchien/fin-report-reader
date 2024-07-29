import os
import openai
from src.api_types import AnalysisResponse, AnalyzeRequest, UploadDocResponse
from src.config import DATA_DIR, DIMENSIONS, KEY_METRICS, SAVE_DIR, ASSISTANT_QUERY
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import time
from src.utils import text_to_uuid

from src.assistant import ReportAnalyst


app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to the specific domain of your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload_file/")
async def post_upload_file(file_upload: UploadFile = File(...)) -> UploadDocResponse:
    try:
        contents = await file_upload.read()
        logger.info(file_upload.filename)

        file_id = text_to_uuid(file_upload.filename)

        os.makedirs(DATA_DIR / file_id, exist_ok=True)
        os.makedirs(SAVE_DIR / file_id, exist_ok=True)

        save_to = DATA_DIR / file_id / file_upload.filename
        with open(save_to, "wb") as f:
            f.write(contents)

        analyst = ReportAnalyst()
        analyst.init_rag_assistant()
        _ = analyst.upload_file_to_vector_store(save_to)
        return UploadDocResponse(filename=file_upload.filename,
                                 file_id=file_id,
                                 assistant_id=analyst.assistant_id,
                                 vector_store_id=analyst.vector_store_id)
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")


@app.post("/analyze_report/")
def post_analyze(analyze_request: AnalyzeRequest) -> AnalysisResponse:
    logger.info("Starting the Financial Report Reader")
    analyst = ReportAnalyst()
    analyst.reinit(analyze_request.assistant_id, analyze_request.vector_store_id)

    query = analyze_request.query
    if len(query) < 5:
        query = ", ".join(KEY_METRICS)
    user_query = ASSISTANT_QUERY.format(query=query)
    logger.info(f"Query metrics: {query}")
    response = analyst.ask_document(user_query)
    return AnalysisResponse(response=response)
    # except Exception as e:
    #     logger.error(f"Error analyzing report: {e}")
    #     raise HTTPException(status_code=500, detail="Report analysis failed")
    #


@app.get("/")
def main():
    content = "Uvicorn running on http://127.0.0.1:8000/docs"
    return HTMLResponse(content=content)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
