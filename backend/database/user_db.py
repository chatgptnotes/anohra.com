import aiosqlite
from typing import Optional, Dict
from auth.jwt_handler import get_password_hash, UserInDB

DB_PATH = "deepguard.db"


async def init_user_db():
    """Initialize the user database table"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                full_name TEXT,
                disabled BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def create_user(email: str, password: str, full_name: Optional[str] = None) -> Dict:
    """Create a new user"""
    hashed_password = get_password_hash(password)

    async with aiosqlite.connect(DB_PATH) as db:
        try:
            cursor = await db.execute("""
                INSERT INTO users (email, hashed_password, full_name)
                VALUES (?, ?, ?)
            """, (email, hashed_password, full_name))
            await db.commit()

            return {
                "id": cursor.lastrowid,
                "email": email,
                "full_name": full_name,
                "disabled": False
            }
        except aiosqlite.IntegrityError:
            raise ValueError("User with this email already exists")


async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Get a user by email"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return UserInDB(
                    email=row["email"],
                    hashed_password=row["hashed_password"],
                    full_name=row["full_name"],
                    disabled=bool(row["disabled"])
                )
            return None


async def update_user(email: str, updates: Dict) -> bool:
    """Update user information"""
    async with aiosqlite.connect(DB_PATH) as db:
        fields = []
        values = []

        if "full_name" in updates:
            fields.append("full_name = ?")
            values.append(updates["full_name"])

        if "disabled" in updates:
            fields.append("disabled = ?")
            values.append(int(updates["disabled"]))

        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(email)

        query = f"UPDATE users SET {', '.join(fields)} WHERE email = ?"
        await db.execute(query, values)
        await db.commit()
        return True


async def delete_user(email: str) -> bool:
    """Delete a user"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM users WHERE email = ?", (email,))
        await db.commit()
        return True
