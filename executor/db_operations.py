from bson import ObjectId
import motor.motor_asyncio
from pymongo import ReturnDocument
import os
import dotenv
from fastapi import HTTPException


dotenv.load_dotenv()

client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("MONGODB_DB")]


async def get_automation(automation_id: str):
    automation = await db.automations.find_one({"_id": ObjectId(automation_id)})
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    return automation

async def get_blocks(automation_id: str):
    blocks = await db.blocks.find({"automationId": ObjectId(automation_id)}).to_list(length=None)
    if not blocks:
        raise HTTPException(status_code=404, detail="Blocks not found")
    return blocks

async  def get_telegram_account(account_id: str):
    account = await db.telegramaccounts.find_one({"_id": ObjectId(account_id)})
    if not account:
        raise HTTPException(status_code=404, detail="Telegram account not found")
    return account