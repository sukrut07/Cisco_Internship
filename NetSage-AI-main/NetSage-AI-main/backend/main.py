import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, SessionLocal
from .models import Case
from .routes import cases, rule_check, reviews, verification, dashboard, responsible_ai
from .seed import seed_database

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Auto-seed database if empty on serverless deployment
db_session = SessionLocal()
try:
    if db_session.query(Case).count() == 0:
        seed_database()
except Exception as e:
    print("Auto-seed on startup note:", e)
finally:
    db_session.close()

app = FastAPI(
    title="NetSage AI API",
    description="AI-Powered Cisco Network Troubleshooting Assistant Backend API",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(cases.router)
app.include_router(rule_check.router)
app.include_router(reviews.router)
app.include_router(verification.router)
app.include_router(dashboard.router)
app.include_router(responsible_ai.router)

@app.get("/")
def root():
    return {
        "status": "online",
        "app": "NetSage AI",
        "version": "1.0.0",
        "ai_mode": "Live API" if os.getenv("AI_API_KEY") else "Mock Engine (Demo Mode)",
        "docs": "/docs"
    }
