from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
import requests
import os

app = FastAPI(title="ADP Financial Data API")

@app.get("/")
def root():
    return {"message": "API is live"}

SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK0000008670.json"
HEADERS = {"User-Agent": "alexlynnhoops@gmail.com"}

@app.get("/documents")
def get_documents(type: str = Query(..., regex="^(10-K|10-Q|8-K)$"), year: int = None):
    resp = requests.get(SEC_SUBMISSIONS_URL, headers=HEADERS)
    data = resp.json()
    results = []

    filings = data["filings"]["recent"]
    for i, form in enumerate(filings["form"]):
        if form != type:
            continue
        filing_year = int(filings["filingDate"][i].split("-")[0])
        if year and filing_year != year:
            continue
        results.append({
            "id": filings["accessionNumber"][i],
            "type": form,
            "date": filings["filingDate"][i],
            "url": f"https://www.sec.gov/Archives/edgar/data/8670/{filings['accessionNumber'][i].replace('-', '')}/{filings['primaryDocument'][i]}"
        })

    return {"status": "ok", "count": len(results), "data": results}

# Serve your hand-written OpenAPI spec
@app.get("/custom-openapi.json")
def get_custom_openapi_spec():
    return FileResponse(os.path.join(os.path.dirname(__file__), "openapi.json"))
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = {
        "openapi": "3.0.1",
        "info": {
            "title": "ADP Financial Data API",
            "version": "1.0.0"
        },
        "servers": [
            {"url": "https://adp-api-87sj.onrender.com"}
        ],
        "paths": {
            "/documents": {
                "get": {
                    "summary": "Fetch ADP filings from SEC EDGAR",
                    "parameters": [
                        {
                            "name": "type",
                            "in": "query",
                            "required": true,
                            "schema": {"type": "string", "enum": ["10-K", "10-Q", "8-K"]}
                        },
                        {
                            "name": "year",
                            "in": "query",
                            "required": false,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "List of filings",
                            "content": {"application/json": {}}
                        }
                    }
                }
            }
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
