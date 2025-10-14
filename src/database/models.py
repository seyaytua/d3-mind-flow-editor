#!/usr/bin/env python3
"""
Database models for D3-Mind-Flow-Editor
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Diagram:
    """Diagram model representing a saved diagram"""
    
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    diagram_type: str = ""  # mindmap, gantt, flowchart
    mermaid_data: str = ""
    node_styles: Optional[str] = None  # JSON format
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'diagram_type': self.diagram_type,
            'mermaid_data': self.mermaid_data,
            'node_styles': self.node_styles,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Diagram':
        """Create from dictionary"""
        created_at = None
        updated_at = None
        
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            updated_at = datetime.fromisoformat(data['updated_at'])
            
        return cls(
            id=data.get('id'),
            title=data.get('title', ''),
            description=data.get('description', ''),
            diagram_type=data.get('diagram_type', ''),
            mermaid_data=data.get('mermaid_data', ''),
            node_styles=data.get('node_styles'),
            created_at=created_at,
            updated_at=updated_at,
        )
    
    def __str__(self) -> str:
        return f"Diagram(id={self.id}, title='{self.title}', type='{self.diagram_type}')"


# Diagram type constants
class DiagramType:
    MINDMAP = "mindmap"
    GANTT = "gantt"
    FLOWCHART = "flowchart"
    
    @classmethod
    def all(cls) -> list[str]:
        """Get all diagram types"""
        return [cls.MINDMAP, cls.GANTT, cls.FLOWCHART]
    
    @classmethod
    def display_names(cls) -> dict[str, str]:
        """Get display names for diagram types"""
        return {
            cls.MINDMAP: "マインドマップ",
            cls.GANTT: "ガントチャート", 
            cls.FLOWCHART: "フローチャート"
        }