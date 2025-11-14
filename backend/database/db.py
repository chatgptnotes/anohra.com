import aiosqlite
import json
from typing import Dict
import os

DB_PATH = "deepguard.db"


async def init_db():
    """Initialize the database with required tables"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT UNIQUE NOT NULL,
                file_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                analysis_result TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def save_analysis_result(data: Dict):
    """Save analysis result to database"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO analysis_results (file_id, file_name, file_type, analysis_result, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data["file_id"],
            data["file_name"],
            data["file_type"],
            json.dumps(data["analysis_result"]),
            data["timestamp"]
        ))
        await db.commit()


async def get_analysis_result(file_id: str) -> Dict:
    """Retrieve analysis result by file ID"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM analysis_results WHERE file_id = ?",
            (file_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "file_id": row["file_id"],
                    "file_name": row["file_name"],
                    "file_type": row["file_type"],
                    "analysis_result": json.loads(row["analysis_result"]),
                    "timestamp": row["timestamp"]
                }
            return None


async def get_all_results(limit: int = 100) -> list:
    """Retrieve all analysis results"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM analysis_results ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "file_id": row["file_id"],
                    "file_name": row["file_name"],
                    "file_type": row["file_type"],
                    "analysis_result": json.loads(row["analysis_result"]),
                    "timestamp": row["timestamp"]
                }
                for row in rows
            ]
