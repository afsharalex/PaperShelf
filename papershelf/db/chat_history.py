"""
Chat history database module for PaperShelf.

This module handles SQLite database operations for storing and retrieving
chat history for the PaperShelf application.
"""

import os
import sqlite3
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from papershelf.utils.config import config


class ChatHistoryDB:
    """Class for managing the chat history database."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the chat history database.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path or config.CHAT_HISTORY_DB_PATH
        self._create_tables_if_not_exist()

    def _create_tables_if_not_exist(self):
        """Create the necessary tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create sessions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create chat_history table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            query TEXT,
            answer TEXT,
            retrieved_documents TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
        ''')

        conn.commit()
        conn.close()

    def create_session(self) -> str:
        """
        Create a new session and return the session ID.

        Returns:
            str: The UUID of the new session
        """
        session_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO sessions (session_id) VALUES (?)",
            (session_id,)
        )
        
        conn.commit()
        conn.close()
        
        return session_id

    def add_chat_entry(self, session_id: str, query: str, answer: str, retrieved_documents: List[Dict[str, Any]]):
        """
        Add a new chat entry to the database.

        Args:
            session_id: The session UUID
            query: The user's query
            answer: The system's answer
            retrieved_documents: List of retrieved documents
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert retrieved_documents to JSON string
        retrieved_documents_json = json.dumps(retrieved_documents)
        
        cursor.execute(
            "INSERT INTO chat_history (session_id, query, answer, retrieved_documents) VALUES (?, ?, ?, ?)",
            (session_id, query, answer, retrieved_documents_json)
        )
        
        conn.commit()
        conn.close()

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all chat entries for a specific session.

        Args:
            session_id: The session UUID

        Returns:
            List of chat entries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM chat_history WHERE session_id = ? ORDER BY created_at DESC",
            (session_id,)
        )
        
        rows = cursor.fetchall()
        result = []
        
        for row in rows:
            entry = dict(row)
            entry['retrieved_documents'] = json.loads(entry['retrieved_documents'])
            result.append(entry)
        
        conn.close()
        return result

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """
        Get all sessions with their creation dates.

        Returns:
            List of sessions
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT session_id, created_at FROM sessions ORDER BY created_at DESC"
        )
        
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
        
        conn.close()
        return result

    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get information about a specific session.

        Args:
            session_id: The session UUID

        Returns:
            Session information including creation date and number of queries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get session creation date
        cursor.execute(
            "SELECT created_at FROM sessions WHERE session_id = ?",
            (session_id,)
        )
        session_row = cursor.fetchone()
        
        if not session_row:
            conn.close()
            return {}
        
        # Count queries in this session
        cursor.execute(
            "SELECT COUNT(*) as query_count FROM chat_history WHERE session_id = ?",
            (session_id,)
        )
        count_row = cursor.fetchone()
        
        result = {
            'session_id': session_id,
            'created_at': session_row['created_at'],
            'query_count': count_row['query_count']
        }
        
        conn.close()
        return result