import os

from bson import ObjectId
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv


def serialize(doc):
	if isinstance(doc, list):
		return [serialize(d) for d in doc]
	if isinstance(doc, dict):
		return {k: serialize(v) for k, v in doc.items()}
	if isinstance(doc, ObjectId):
		return str(doc)
	return doc

app = FastAPI(title="training")
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "training")

if not MONGODB_URL:
	raise ValueError("MONGODB_URL is required")

mongo_client = AsyncIOMotorClient(MONGODB_URL)
db = mongo_client[MONGODB_DB_NAME]
training_types_collection = db["training_types"]
sessions_collection = db["sessions"]
exercises_collection = db["exercises"]


@app.get("/debug")
async def debug():
	collections = await db.list_collection_names()
	return {"database": MONGODB_DB_NAME, "collections": collections}


@app.get("/trainingTypes", responses={500: {"description": "Failed to fetch trainingTypes"}})
async def get_all_training_types():
	try:
		docs = await training_types_collection.find().to_list(length=None)
		return serialize(docs)
	except Exception as exc:
		raise HTTPException(status_code=500, detail=f"Failed to fetch trainingTypes: {exc}")


@app.get("/sessions", responses={500: {"description": "Failed to fetch sessions"}})
async def get_all_sessions():
	try:
		docs = await sessions_collection.find().to_list(length=None)
		return serialize(docs)
	except Exception as exc:
		raise HTTPException(status_code=500, detail=f"Failed to fetch sessions: {exc}")


@app.get("/exercises", responses={500: {"description": "Failed to fetch exercises"}})
async def get_all_exercises():
	try:
		docs = await exercises_collection.find().to_list(length=None)
		return serialize(docs)
	except Exception as exc:
		raise HTTPException(status_code=500, detail=f"Failed to fetch exercises: {exc}")
