from pydantic import BaseModel


class AnalysisResponse(BaseModel):
    response: str


class UploadDocResponse(BaseModel):
    filename: str
    file_id: str
    assistant_id: str
    vector_store_id: str


class AnalyzeRequest(BaseModel):
    username: str
    filename: str
    assistant_id: str
    vector_store_id: str
    query: str
