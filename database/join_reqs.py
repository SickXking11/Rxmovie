import motor.motor_asyncio
from info import REQ_DB

class JoinReqs:

    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(REQ_DB)           
        self.db = self.client["JoinReqs"]
        self.col = self.db.chats
        
    async def add_user(self, id):
        is_user = await self.col.find_one({'id': int(id)})
        if not is_user:
            await self.col.insert_one({"id": int(id)})
        
    async def get_user(self, id):
        return await self.col.find_one({"id": int(id)})

    async def get_all_users(self):
        return await self.col.find({})

    async def delete_user(self, id):
        await self.col.delete_one({"id": int(id)})

    async def delete_all_users(self):
        await self.col.delete_many({})

    async def get_all_users_count(self):
        return await self.col.count_documents({})


req_db = JoinReqs()