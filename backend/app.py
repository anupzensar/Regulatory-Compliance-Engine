from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/run-test")
async def run_test(request: Request):
    data = await request.json()
    game_url = data.get("gameUrl")
    test_type = data.get("testType")
    print(f"Game URL: {game_url}")
    print(f"Test Type: {test_type}")
    return {"status": "received"}


# Run server on port 7000
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=7000, reload=True)