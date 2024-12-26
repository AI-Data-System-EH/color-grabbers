# FastAPI 서버 설정
from fastapi import FastAPI

app = FastAPI()


# Define FastAPI endpoints
@app.get("/capture")
def capture(name: str):
    return "success"


@app.get("/")
def main():
    return "success"
