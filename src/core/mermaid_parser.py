#!/usr/bin/env python3
"""
Mermaid parser for D3-Mind-Flow-Editor
Handles Mermaid notation parsing and validation for flowcharts
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from ..utils.logger import logger


class MermaidParseError(Exception):
    """Mermaid parsing error"""
    pass


@dataclass
class MermaidNode:
    """Represents a Mermaid diagram node"""
    id: str
    text: str
    shape: str
    style: Optional[Dict[str, str]] = None


@dataclass
class MermaidEdge:
    """Represents a Mermaid diagram edge"""
    source: str
    target: str
    text: Optional[str] = None
    style: Optional[Dict[str, str]] = None


class MermaidParser:
    """Parser for Mermaid notation diagrams"""
    
    # Supported diagram types
    SUPPORTED_TYPES = ['flowchart', 'graph']
    
    # Direction mappings
    DIRECTIONS = {
        'TD': 'top-down',
        'TB': 'top-bottom', 
        'BT': 'bottom-top',
        'RL': 'right-left',
        'LR': 'left-right'
    }
    
    # Node shape patterns
    NODE_PATTERNS = {
        r'\[([^\]]+)\]': 'rect',           # [text] -> rectangle
        r'\(([^)]+)\)': 'round',           # (text) -> rounded rectangle
        r'\{([^}]+)\}': 'rhombus',         # {text} -> diamond
        r'\(\(([^)]+)\)\)': 'circle',      # ((text)) -> circle
        r'\[\(([^)]+)\)\]': 'stadium',     # [(text)] -> stadium
        r'\[\[([^\]]+)\]\]': 'subroutine', # [[text]] -> subroutine
        r'\[/([^/]+)/\]': 'rhombus',       # [/text/] -> rhombus
        r'\[\\([^\\]+)\\\]': 'rhombus',    # [\text\] -> rhombus
    }
    
    # Arrow patterns
    ARROW_PATTERNS = {
        '-->': 'arrow',
        '---': 'line',
        '-.-': 'dotted',
        '==>': 'thick',
        '===': 'thick_line',
        '-.->': 'dotted_arrow'
    }
    
    @staticmethod
    def parse_mermaid(mermaid_text: str) -> Dict[str, Any]:
        """Parse Mermaid notation text
        
        Args:
            mermaid_text: Mermaid formatted text
            
        Returns:
            Dictionary containing parsed diagram structure
            
        Raises:
            MermaidParseError: If parsing fails
        """
        try:
            # Clean and normalize input
            mermaid_text = MermaidParser._clean_mermaid_text(mermaid_text)
            
            # Parse diagram header
            lines = mermaid_text.split('\n')
            diagram_info = MermaidParser._parse_diagram_header(lines[0])
            
            # Parse nodes and edges
            nodes = {}
            edges = []
            
            for line_num, line in enumerate(lines[1:], 2):
                line = line.strip()
                if not line or line.startswith('%'):  # Skip empty lines and comments
                    continue
                
                try:
                    # Try to parse as edge (connection)
                    edge = MermaidParser._parse_edge(line, nodes)
                    if edge:
                        edges.append(edge)
                    else:
                        # Try to parse as standalone node definition
                        node = MermaidParser._parse_node_definition(line)
                        if node:
                            nodes[node.id] = node
                
                except Exception as e:
                    logger.warning(f"Error parsing line {line_num}: '{line}' - {e}")
                    continue
            
            # Build result structure
            result = {
                'type': diagram_info['type'],
                'direction': diagram_info['direction'],
                'nodes': [
                    {
                        'id': node.id,
                        'text': node.text,
                        'shape': node.shape,
                        'style': node.style or {}
                    }
                    for node in nodes.values()
                ],
                'edges': [
                    {
                        'source': edge.source,
                        'target': edge.target,
                        'text': edge.text,
                        'style': edge.style or {}
                    }
                    for edge in edges
                ],
                'metadata': {
                    'total_nodes': len(nodes),
                    'total_edges': len(edges),
                    'parsed_lines': len(lines) - 1
                }
            }
            
            logger.debug(f"Parsed Mermaid: {len(nodes)} nodes, {len(edges)} edges")
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse Mermaid: {e}")
            raise MermaidParseError(f"Mermaid parsing failed: {e}")
    
    @staticmethod
    def _clean_mermaid_text(mermaid_text: str) -> str:
        """Clean and normalize Mermaid text
        
        Args:
            mermaid_text: Raw Mermaid text
            
        Returns:
            Cleaned Mermaid text
        """
        # Remove BOM if present
        if mermaid_text.startswith('\ufeff'):
            mermaid_text = mermaid_text[1:]
        
        # Normalize line endings
        mermaid_text = mermaid_text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove leading/trailing whitespace
        mermaid_text = mermaid_text.strip()
        
        return mermaid_text
    
    @staticmethod
    def _parse_diagram_header(header_line: str) -> Dict[str, str]:
        """Parse diagram header line
        
        Args:
            header_line: First line of Mermaid diagram
            
        Returns:
            Dictionary with diagram type and direction
            
        Raises:
            MermaidParseError: If header is invalid
        """
        header_line = header_line.strip()
        
        # Match flowchart with direction
        flowchart_match = re.match(r'flowchart\s+(\w+)', header_line, re.IGNORECASE)
        if flowchart_match:
            direction = flowchart_match.group(1).upper()
            if direction not in MermaidParser.DIRECTIONS:
                logger.warning(f"Unknown direction '{direction}', using TD (top-down)")
                direction = 'TD'
            return {
                'type': 'flowchart',
                'direction': direction
            }
        
        # Match graph with direction
        graph_match = re.match(r'graph\s+(\w+)', header_line, re.IGNORECASE)
        if graph_match:
            direction = graph_match.group(1).upper()
            if direction not in MermaidParser.DIRECTIONS:
                logger.warning(f"Unknown direction '{direction}', using TD (top-down)")
                direction = 'TD'
            return {
                'type': 'graph',
                'direction': direction
            }
        
        # Default to flowchart TD
        if header_line.lower().startswith(('flowchart', 'graph')):
            return {
                'type': 'flowchart',
                'direction': 'TD'
            }
        
        raise MermaidParseError(f"Invalid diagram header: '{header_line}'. Expected 'flowchart <direction>' or 'graph <direction>'")
    
    @staticmethod
    def _parse_edge(line: str, nodes: Dict[str, MermaidNode]) -> Optional[MermaidEdge]:
        """Parse a line as an edge (connection between nodes)
        
        Args:
            line: Line to parse
            nodes: Dictionary to store discovered nodes
            
        Returns:
            MermaidEdge object if line represents an edge, None otherwise
        """
        # Find arrow pattern
        arrow_match = None
        arrow_type = None
        
        for pattern, arrow_name in MermaidParser.ARROW_PATTERNS.items():
            if pattern in line:
                # Find the arrow with optional label
                arrow_regex = re.escape(pattern)
                
                # Check for labeled arrow: -->|label|
                labeled_match = re.search(f'{arrow_regex}\\|([^|]+)\\|', line)
                if labeled_match:
                    arrow_match = labeled_match
                    arrow_type = arrow_name
                    break
                
                # Check for simple arrow: -->
                simple_match = re.search(arrow_regex, line)
                if simple_match:
                    arrow_match = simple_match
                    arrow_type = arrow_name
                    break
        
        if not arrow_match:
            return None
        
        # Split line by arrow
        arrow_pos = arrow_match.start()
        source_part = line[:arrow_pos].strip()
        target_part = line[arrow_match.end():].strip()
        
        # Parse source node
        source_node = MermaidParser._parse_node_from_part(source_part)
        if source_node:
            nodes[source_node.id] = source_node
        
        # Parse target node
        target_node = MermaidParser._parse_node_from_part(target_part)
        if target_node:
            nodes[target_node.id] = target_node
        
        # Extract edge label if present
        edge_text = None
        if '|' in arrow_match.group(0):
            label_match = re.search(r'\|([^|]+)\|', arrow_match.group(0))
            if label_match:
                edge_text = label_match.group(1).strip()
        
        return MermaidEdge(
            source=source_node.id if source_node else source_part,
            target=target_node.id if target_node else target_part,
            text=edge_text,
            style={'type': arrow_type}
        )
    
    @staticmethod
    def _parse_node_from_part(part: str) -> Optional[MermaidNode]:
        """Parse node from a part of the line
        
        Args:
            part: Part of line that might contain a node
            
        Returns:
            MermaidNode object if found, None otherwise
        """
        part = part.strip()
        
        # Try each node pattern
        for pattern, shape in MermaidParser.NODE_PATTERNS.items():
            match = re.search(pattern, part)
            if match:
                node_text = match.group(1).strip()
                
                # Extract node ID (everything before the shape)
                node_id = part[:match.start()].strip()
                if not node_id:
                    # If no ID before shape, use the text as ID
                    node_id = re.sub(r'[^a-zA-Z0-9_]', '_', node_text)
                
                return MermaidNode(
                    id=node_id,
                    text=node_text,
                    shape=shape
                )
        
        # If no shape pattern found, treat as simple node ID
        if re.match(r'^[a-zA-Z0-9_]+$', part):
            return MermaidNode(
                id=part,
                text=part,
                shape='rect'
            )
        
        return None
    
    @staticmethod
    def _parse_node_definition(line: str) -> Optional[MermaidNode]:
        """Parse a standalone node definition
        
        Args:
            line: Line containing node definition
            
        Returns:
            MermaidNode object if found, None otherwise
        """
        # Look for node definition pattern: nodeId[text] or nodeId(text), etc.
        for pattern, shape in MermaidParser.NODE_PATTERNS.items():
            match = re.search(f'([a-zA-Z0-9_]+)\\s*{pattern}', line)
            if match:
                node_id = match.group(1).strip()
                node_text = match.group(2).strip()
                
                return MermaidNode(
                    id=node_id,
                    text=node_text,
                    shape=shape
                )
        
        return None
    
    @staticmethod
    def validate_mermaid(mermaid_text: str) -> Tuple[bool, str]:
        """Validate Mermaid notation
        
        Args:
            mermaid_text: Mermaid text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            result = MermaidParser.parse_mermaid(mermaid_text)
            
            # Additional validation
            if not result['nodes']:
                return False, "No nodes found in diagram"
            
            if not result['edges']:
                return False, "No connections found in diagram"
            
            # Check for disconnected nodes
            connected_nodes = set()
            for edge in result['edges']:
                connected_nodes.add(edge['source'])
                connected_nodes.add(edge['target'])
            
            disconnected = [node['id'] for node in result['nodes'] if node['id'] not in connected_nodes]
            if disconnected:
                logger.warning(f"Disconnected nodes found: {disconnected}")
            
            return True, ""
            
        except MermaidParseError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Validation error: {e}"
    
    @staticmethod
    def get_sample_flowchart() -> str:
        """Get sample flowchart Mermaid code
        
        Returns:
            Sample Mermaid string
        """
        return """flowchart TD
    A[開始] --> B{条件確認}
    B -->|Yes| C[処理実行]
    B -->|No| D[エラー処理]
    C --> E[結果保存]
    D --> F[ログ出力]
    E --> G[終了]
    F --> G"""
    
    @staticmethod
    def get_sample_horizontal_flowchart() -> str:
        """Get sample horizontal flowchart
        
        Returns:
            Sample horizontal Mermaid string
        """
        return """flowchart LR
    Start([開始]) --> Input[データ入力]
    Input --> Validate{入力検証}
    Validate -->|Valid| Process[データ処理]
    Validate -->|Invalid| Error[エラー表示]
    Process --> Output[結果出力]
    Error --> Input
    Output --> End([終了])"""


class MermaidGenerator:
    """Mermaid notation generator for templates and examples"""
    
    @staticmethod
    def generate_flowchart_template(
        process_name: str = "業務プロセス",
        direction: str = "TD",
        steps: Optional[List[str]] = None
    ) -> str:
        """Generate flowchart template
        
        Args:
            process_name: Name of the process
            direction: Flow direction (TD, LR, etc.)
            steps: List of process steps
            
        Returns:
            Mermaid flowchart string
        """
        if steps is None:
            steps = ["開始", "入力", "処理", "判定", "出力", "終了"]
        
        lines = [f"flowchart {direction}"]
        
        # Add nodes
        for i, step in enumerate(steps):
            node_id = f"step{i+1}"
            
            if i == 0:  # Start node
                lines.append(f"    {node_id}([{step}])")
            elif i == len(steps) - 1:  # End node
                lines.append(f"    {node_id}([{step}])")
            elif "判定" in step or "確認" in step:  # Decision node
                lines.append(f"    {node_id}{{{step}}}")
            else:  # Process node
                lines.append(f"    {node_id}[{step}]")
        
        # Add connections
        for i in range(len(steps) - 1):
            source_id = f"step{i+1}"
            target_id = f"step{i+2}"
            
            if "判定" in steps[i]:
                lines.append(f"    {source_id} -->|Yes| {target_id}")
                if i > 0:
                    lines.append(f"    {source_id} -->|No| step{i}")
            else:
                lines.append(f"    {source_id} --> {target_id}")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_decision_flowchart() -> str:
        """Generate decision-heavy flowchart template
        
        Returns:
            Mermaid flowchart string with multiple decision points
        """
        return """flowchart TD
    Start([開始]) --> Input[データ入力]
    Input --> Check1{データ形式OK?}
    Check1 -->|No| Error1[形式エラー]
    Error1 --> Input
    Check1 -->|Yes| Check2{権限あり?}
    Check2 -->|No| Error2[権限エラー]
    Error2 --> End1([終了])
    Check2 -->|Yes| Process[データ処理]
    Process --> Check3{処理成功?}
    Check3 -->|No| Error3[処理エラー]
    Error3 --> Retry{再試行?}
    Retry -->|Yes| Process
    Retry -->|No| End2([終了])
    Check3 -->|Yes| Output[結果出力]
    Output --> End3([正常終了])"""
    
    @staticmethod
    def generate_workflow_template(workflow_type: str = "approval") -> str:
        """Generate workflow template based on type
        
        Args:
            workflow_type: Type of workflow (approval, review, etc.)
            
        Returns:
            Mermaid flowchart string
        """
        templates = {
            "approval": """flowchart TD
    Submit[申請提出] --> Review1{一次審査}
    Review1 -->|承認| Review2{二次審査}
    Review1 -->|差戻| Revise[修正]
    Revise --> Submit
    Review2 -->|承認| Approve[承認完了]
    Review2 -->|差戻| Revise
    Review2 -->|却下| Reject[却下]
    Approve --> End1([処理完了])
    Reject --> End2([終了])""",
            
            "review": """flowchart LR
    Create[文書作成] --> Submit[レビュー依頼]
    Submit --> Review[レビュー実施]
    Review --> Check{問題あり?}
    Check -->|Yes| Feedback[フィードバック]
    Feedback --> Revise[修正]
    Revise --> Submit
    Check -->|No| Approve[承認]
    Approve --> Publish[公開]""",
            
            "development": """flowchart TD
    Plan[企画] --> Design[設計]
    Design --> Dev[開発]
    Dev --> Test[テスト]
    Test --> Bug{バグあり?}
    Bug -->|Yes| Fix[修正]
    Fix --> Test
    Bug -->|No| Deploy[デプロイ]
    Deploy --> Monitor[監視]
    Monitor --> Maintain[保守運用]"""
        }
        
        return templates.get(workflow_type, templates["approval"])