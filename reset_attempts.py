import asyncio
from app.db.session import get_db
from app.services.user import reset_login_attempts, get_user_by_username

async def reset():
    async for db in get_db():
        user = await get_user_by_username(db, username="admin")
        if user:
            result = await reset_login_attempts(db, user_id=str(user.id))
            print(f"Login attempts reset for admin: {result}")
        else:
            print("Admin user not found")

if __name__ == "__main__":
    asyncio.run(reset()) 