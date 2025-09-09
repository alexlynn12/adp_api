from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
import requests
import os

app = FastAPI(title="ADP Financial Data API")

# Root route: quick test
@app.get("/")
def root():
    return {"message": "API is live"}

# SEC EDGAR filings for ADP
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK0000008670.json"
HEADERS = {"User-Agent": "alexlynnhoops@gmail.com"}

# /documents route
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

    return {"status": "ok", "count": len(results), "data": results
