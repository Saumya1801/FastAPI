import requests
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from datetime import datetime
import os
import bcrypt

from . import models, schemas, database
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

API_KEY = os.getenv("API_KEY")
API_KEY_HASH = bcrypt.hashpw(API_KEY.encode('utf-8'), bcrypt.gensalt())
LLM_API_KEY = os.getenv("LLM_API_KEY")  # Assuming you have an API key for the LLM
LLM_API_URL = "https://api.google.com/gemini/v1.5/pro"  # Replace with the actual API URL

API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_api_key(api_key_header: str = Depends(api_key_header)):
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="API key header missing"
        )
    
    if bcrypt.checkpw(api_key_header.encode('utf-8'), API_KEY_HASH.encode('utf-8')):
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )
    
def get_llm_response_from_api(query: str) -> dict:
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "input": query,
        
    }
    response = requests.post(LLM_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

@app.post("/query", response_model=schemas.QueryResponse)
async def get_llm_response(request: schemas.QueryRequest, api_key: APIKeyHeader = Depends(get_api_key), db: Session = Depends(get_db)):
    try:
        llm_response = get_llm_response_from_api(request.query)
        response_text = llm_response.get("response", "No response from LLM")  # Adjust based on actual API response structure
        tokens_charged = llm_response.get("tokens_charged", 100)  # Placeholder
        actual_cost = llm_response.get("cost", 0.01)  # Placeholder

        query_log = models.QueryLog(
            doctor_id=request.doctor_id,
            doctor_name=request.doctor_name,
            area_of_expertise=request.area_of_expertise,
            query=request.query,
            response=response_text,
            tokens_charged=tokens_charged,
            actual_cost=actual_cost,
        )

        db.add(query_log)
        db.commit()
        db.refresh(query_log)

        return schemas.QueryResponse(
            response=response_text,

        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
