#!/usr/bin/env python3
"""
SQLite database manager for D3-Mind-Flow-Editor
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from .models import Diagram, DiagramType


class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database manager
        
        Args:
            db_path: Path to database file. If None, uses default location.
        """
        if db_path is None:
            # Default to user's home directory
            home_dir = Path.home()
            self.db_path = home_dir / ".d3_mind_flow_editor" / "diagrams.db"
            # Create directory if it doesn't exist
            self.db_path.parent.mkdir(exist_ok=True)
        else:
            self.db_path = Path(db_path)
            
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create diagrams table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS diagrams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    diagram_type TEXT NOT NULL,
                    mermaid_data TEXT NOT NULL,
                    node_styles TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_diagram_type 
                ON diagrams(diagram_type)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON diagrams(created_at)
            ''')
            
            conn.commit()
    
    def save_diagram(self, diagram: Diagram) -> int:
        """Save a diagram to database
        
        Args:
            diagram: Diagram object to save
            
        Returns:
            ID of the saved diagram
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            now = datetime.now()
            
            if diagram.id is None:
                # Insert new diagram
                cursor.execute('''
                    INSERT INTO diagrams (
                        title, description, diagram_type, mermaid_data, 
                        node_styles, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    diagram.title, diagram.description, diagram.diagram_type,
                    diagram.mermaid_data, diagram.node_styles, now, now
                ))
                diagram_id = cursor.lastrowid
            else:
                # Update existing diagram
                cursor.execute('''
                    UPDATE diagrams SET 
                        title=?, description=?, diagram_type=?, mermaid_data=?,
                        node_styles=?, updated_at=?
                    WHERE id=?
                ''', (
                    diagram.title, diagram.description, diagram.diagram_type,
                    diagram.mermaid_data, diagram.node_styles, now, diagram.id
                ))
                diagram_id = diagram.id
            
            conn.commit()
            return diagram_id
    
    def get_diagram(self, diagram_id: int) -> Optional[Diagram]:
        """Get a diagram by ID
        
        Args:
            diagram_id: ID of diagram to retrieve
            
        Returns:
            Diagram object or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, description, diagram_type, mermaid_data,
                       node_styles, created_at, updated_at
                FROM diagrams WHERE id=?
            ''', (diagram_id,))
            
            row = cursor.fetchone()
            if row is None:
                return None
            
            return Diagram(
                id=row[0],
                title=row[1],
                description=row[2],
                diagram_type=row[3],
                mermaid_data=row[4],
                node_styles=row[5],
                created_at=datetime.fromisoformat(row[6]) if row[6] else None,
                updated_at=datetime.fromisoformat(row[7]) if row[7] else None,
            )
    
    def get_all_diagrams(self, diagram_type: Optional[str] = None) -> List[Diagram]:
        """Get all diagrams, optionally filtered by type
        
        Args:
            diagram_type: Filter by diagram type (optional)
            
        Returns:
            List of Diagram objects
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if diagram_type is None:
                cursor.execute('''
                    SELECT id, title, description, diagram_type, mermaid_data,
                           node_styles, created_at, updated_at
                    FROM diagrams ORDER BY updated_at DESC
                ''')
            else:
                cursor.execute('''
                    SELECT id, title, description, diagram_type, mermaid_data,
                           node_styles, created_at, updated_at
                    FROM diagrams WHERE diagram_type=? ORDER BY updated_at DESC
                ''', (diagram_type,))
            
            diagrams = []
            for row in cursor.fetchall():
                diagrams.append(Diagram(
                    id=row[0],
                    title=row[1],
                    description=row[2],
                    diagram_type=row[3],
                    mermaid_data=row[4],
                    node_styles=row[5],
                    created_at=datetime.fromisoformat(row[6]) if row[6] else None,
                    updated_at=datetime.fromisoformat(row[7]) if row[7] else None,
                ))
            
            return diagrams
    
    def delete_diagram(self, diagram_id: int) -> bool:
        """Delete a diagram by ID
        
        Args:
            diagram_id: ID of diagram to delete
            
        Returns:
            True if deleted, False if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM diagrams WHERE id=?', (diagram_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def search_diagrams(self, query: str) -> List[Diagram]:
        """Search diagrams by title or description
        
        Args:
            query: Search query string
            
        Returns:
            List of matching Diagram objects
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            search_pattern = f'%{query}%'
            
            cursor.execute('''
                SELECT id, title, description, diagram_type, mermaid_data,
                       node_styles, created_at, updated_at
                FROM diagrams 
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY updated_at DESC
            ''', (search_pattern, search_pattern))
            
            diagrams = []
            for row in cursor.fetchall():
                diagrams.append(Diagram(
                    id=row[0],
                    title=row[1],
                    description=row[2],
                    diagram_type=row[3],
                    mermaid_data=row[4],
                    node_styles=row[5],
                    created_at=datetime.fromisoformat(row[6]) if row[6] else None,
                    updated_at=datetime.fromisoformat(row[7]) if row[7] else None,
                ))
            
            return diagrams
    
    def get_statistics(self) -> dict:
        """Get database statistics
        
        Returns:
            Dictionary with statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total count
            cursor.execute('SELECT COUNT(*) FROM diagrams')
            total_count = cursor.fetchone()[0]
            
            # Count by type
            type_counts = {}
            for diagram_type in DiagramType.all():
                cursor.execute('SELECT COUNT(*) FROM diagrams WHERE diagram_type=?', (diagram_type,))
                type_counts[diagram_type] = cursor.fetchone()[0]
            
            # Latest update
            cursor.execute('SELECT MAX(updated_at) FROM diagrams')
            latest_update = cursor.fetchone()[0]
            
            return {
                'total_count': total_count,
                'type_counts': type_counts,
                'latest_update': latest_update,
                'db_path': str(self.db_path),
            }
    
    def close(self):
        """Close database connection (not needed with context manager usage)"""
        pass