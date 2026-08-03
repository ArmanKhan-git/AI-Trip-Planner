from fastapi import FastAPI
from api.routes import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Voyage AI",
    version="1.0"
)
allow_origins=[
    "http://localhost:5173",
    "https://voyageai-rust.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Voyage AI Backend Running 🚀"
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is awake!"}