"""Storage layer for Nexus CLI Assistant using SQLite."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from nexus_qa.models import Command, Category, HistoryEntry, CacheEntry


class Storage:
    """SQLite storage manager for commands, categories, history, and cache."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize storage with database path."""
        if db_path is None:
            db_dir = Path.home() / ".config" / "nexus" / "data"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "commands.db"
        
        self.db_path = db_path
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Commands table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT
            )
        """)
        
        # History table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                response TEXT,
                provider TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Cache table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT UNIQUE NOT NULL,
                query_text TEXT NOT NULL,
                response TEXT NOT NULL,
                provider TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        """)
        
        # Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON commands(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_created ON history(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_hash ON cache(query_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache(expires_at)")
        
        conn.commit()
        conn.close()
    
    # Command operations
    def save_command(self, command: str, category: str, description: Optional[str] = None) -> int:
        """Save a command to the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO commands (command, category, description) VALUES (?, ?, ?)",
            (command, category, description)
        )
        command_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return command_id
    
    def get_commands(self, category: Optional[str] = None) -> List[Command]:
        """Get commands, optionally filtered by category."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if category:
            cursor.execute(
                "SELECT * FROM commands WHERE category = ? ORDER BY created_at DESC",
                (category,)
            )
        else:
            cursor.execute("SELECT * FROM commands ORDER BY created_at DESC")
        
        rows = cursor.fetchall()
        conn.close()
        
        commands = []
        for row in rows:
            commands.append(Command(
                id=row["id"],
                command=row["command"],
                category=row["category"],
                description=row["description"],
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            ))
        return commands
    
    def search_commands(self, keyword: str) -> List[Command]:
        """Search commands by keyword."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM commands 
               WHERE command LIKE ? OR category LIKE ? OR description LIKE ?
               ORDER BY created_at DESC""",
            (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        )
        rows = cursor.fetchall()
        conn.close()
        
        commands = []
        for row in rows:
            commands.append(Command(
                id=row["id"],
                command=row["command"],
                category=row["category"],
                description=row["description"],
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            ))
        return commands
    
    def delete_command(self, command_id: int) -> bool:
        """Delete a command by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM commands WHERE id = ?", (command_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    # Category operations
    def get_categories(self) -> List[Category]:
        """Get all categories."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category as name FROM commands ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        
        return [Category(name=row["name"]) for row in rows]
    
    # History operations
    def save_history(self, query: str, response: Optional[str] = None, provider: Optional[str] = None) -> int:
        """Save a history entry."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO history (query, response, provider) VALUES (?, ?, ?)",
            (query, response, provider)
        )
        history_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return history_id
    
    def get_history(self, limit: int = 20) -> List[HistoryEntry]:
        """Get recent history entries."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM history ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append(HistoryEntry(
                id=row["id"],
                query=row["query"],
                response=row["response"],
                provider=row["provider"],
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            ))
        return history
    
    # Cache operations
    def get_cache(self, query_hash: str) -> Optional[CacheEntry]:
        """Get a cache entry by query hash."""
        conn = self._get_connection()
        cursor = conn.cursor()
        # Compare using ISO format to match how we store it
        cursor.execute(
            "SELECT * FROM cache WHERE query_hash = ?",
            (query_hash,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            expires_at = datetime.fromisoformat(row["expires_at"])
            # Check expiration in Python to ensure accurate comparison
            if expires_at > datetime.now():
                return CacheEntry(
                    id=row["id"],
                    query_hash=row["query_hash"],
                    query_text=row["query_text"],
                    response=row["response"],
                    provider=row["provider"],
                    created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
                    expires_at=expires_at,
                )
        return None
    
    def save_cache(self, query_hash: str, query_text: str, response: str, 
                   provider: Optional[str], expires_at: datetime) -> int:
        """Save a cache entry."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT OR REPLACE INTO cache 
               (query_hash, query_text, response, provider, expires_at) 
               VALUES (?, ?, ?, ?, ?)""",
            (query_hash, query_text, response, provider, expires_at.isoformat())
        )
        cache_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return cache_id
    
    def cleanup_expired_cache(self):
        """Remove expired cache entries."""
        conn = self._get_connection()
        cursor = conn.cursor()
        # Get all entries and filter in Python for accurate datetime comparison
        cursor.execute("SELECT * FROM cache")
        rows = cursor.fetchall()
        now = datetime.now()
        deleted_count = 0
        
        for row in rows:
            expires_at = datetime.fromisoformat(row["expires_at"])
            if expires_at <= now:
                cursor.execute("DELETE FROM cache WHERE id = ?", (row["id"],))
                deleted_count += 1
        
        conn.commit()
        conn.close()
        return deleted_count
    
    def get_cache_count(self) -> int:
        """Get total number of cache entries."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM cache")
        count = cursor.fetchone()["count"]
        conn.close()
        return count

