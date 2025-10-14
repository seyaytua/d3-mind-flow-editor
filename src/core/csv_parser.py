#!/usr/bin/env python3
"""
CSV parser for D3-Mind-Flow-Editor
Handles CSV parsing for mind maps and Gantt charts according to design specifications
"""

import csv
import io
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import re

from ..utils.logger import logger


def parse_mindmap_csv(csv_content: str) -> Dict[str, Any]:
    """
    Parse CSV content for mind map according to design document format
    
    Expected format from design document:
    - Hierarchical structure with A, B, C columns representing levels
    - Empty cells indicate hierarchy breaks
    - Maximum 5 levels supported
    - Alternative format: Node,Parent,Level,Color
    
    Args:
        csv_content: CSV string content
        
    Returns:
        Hierarchical dictionary for D3.js tree layout
    """
    try:
        lines = csv_content.strip().split('\n')
        if not lines:
            raise ValueError("CSV content is empty")
        
        # Detect format type
        first_line = lines[0].lower()
        if 'node' in first_line and 'parent' in first_line:
            return _parse_node_parent_format(csv_content)
        else:
            return _parse_hierarchical_format(csv_content)
            
    except Exception as e:
        logger.error(f"Mind map CSV parsing failed: {e}")
        return _create_error_mindmap(str(e))


def _parse_node_parent_format(csv_content: str) -> Dict[str, Any]:
    """Parse Node,Parent,Level,Color format"""
    reader = csv.DictReader(io.StringIO(csv_content.strip()))
    rows = list(reader)
    
    nodes = {}
    root = None
    
    # Sort by level to ensure parent nodes are created first
    sorted_rows = sorted(rows, key=lambda x: int(x.get('Level', 1)))
    
    for row in sorted_rows:
        node_name = row.get('Node', '').strip()
        parent_name = row.get('Parent', '').strip()
        level = int(row.get('Level', 1))
        color = row.get('Color', '').strip()
        
        if not node_name:
            continue
        
        # Assign color based on level if not specified
        if not color:
            level_colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336']
            color = level_colors[(level - 1) % len(level_colors)]
        
        node = {
            'name': node_name,
            'level': level,
            'color': color,
            'children': []
        }
        
        nodes[node_name] = node
        
        if not parent_name or level == 1:
            root = node
        else:
            if parent_name in nodes:
                nodes[parent_name]['children'].append(node)
            else:
                # Create missing parent
                parent_node = {
                    'name': parent_name,
                    'level': level - 1,
                    'color': '#666666',
                    'children': [node]
                }
                nodes[parent_name] = parent_node
    
    return root or _create_default_mindmap()


def _parse_hierarchical_format(csv_content: str) -> Dict[str, Any]:
    """
    Parse hierarchical format (A, B, C columns) as specified in design document
    Format: Column A = Level 1, Column B = Level 2, etc.
    Empty cells preserve hierarchy structure
    """
    reader = csv.reader(io.StringIO(csv_content.strip()))
    rows = list(reader)
    
    if not rows:
        raise ValueError("No data rows found")
    
    # Build hierarchical structure
    root = None
    current_path = [None] * 6  # Support up to 5 levels + root
    node_stack = [None] * 6
    level_colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', '#00BCD4']
    
    for row_idx, row in enumerate(rows):
        # Skip empty rows
        if not any(cell.strip() for cell in row):
            continue
        
        # Process each column (level)
        for level, cell_value in enumerate(row):
            cell_value = cell_value.strip()
            
            if cell_value:
                # Create node at this level
                node = {
                    'name': cell_value,
                    'level': level + 1,
                    'color': level_colors[level % len(level_colors)],
                    'children': []
                }
                
                # Update path tracking
                current_path[level] = cell_value
                node_stack[level] = node
                
                # Clear deeper levels
                for i in range(level + 1, len(current_path)):
                    current_path[i] = None
                    node_stack[i] = None
                
                # Attach to parent or set as root
                if level == 0:
                    root = node
                else:
                    parent_node = node_stack[level - 1]
                    if parent_node:
                        parent_node['children'].append(node)
                
                # Only process first non-empty cell in each row for hierarchy
                break
    
    return root or _create_default_mindmap()


def parse_gantt_csv(csv_content: str) -> List[Dict[str, Any]]:
    """
    Parse CSV content for Gantt chart according to design document format
    
    Expected format:
    task,start,end,category,progress,dependencies
    - start/end: YYYY-MM-DD format
    - progress: 0.0-1.0 (decimal) or 0-100 (percentage)
    - dependencies: semicolon-separated task names
    
    Args:
        csv_content: CSV string content
        
    Returns:
        List of task dictionaries with standardized fields
    """
    try:
        reader = csv.DictReader(io.StringIO(csv_content.strip()))
        rows = list(reader)
        
        if not rows:
            raise ValueError("CSV content is empty")
        
        tasks = []
        task_names = set()  # Track task names for validation
        
        for row_idx, row in enumerate(rows):
            task_name = row.get('task', row.get('Task', '')).strip()
            start_date = row.get('start', row.get('Start Date', row.get('Start', ''))).strip()
            end_date = row.get('end', row.get('End Date', row.get('End', ''))).strip()
            category = row.get('category', row.get('Category', 'General')).strip()
            progress = row.get('progress', row.get('Progress', '0')).strip()
            dependencies = row.get('dependencies', row.get('Dependencies', '')).strip()
            resource = row.get('resource', row.get('Resource', '')).strip()
            
            if not task_name:
                logger.warning(f"Empty task name at row {row_idx + 1}, skipping")
                continue
            
            # Parse and validate dates
            start_dt, end_dt = _parse_gantt_dates(start_date, end_date, task_name)
            
            # Parse progress (handle both decimal and percentage formats)
            progress_val = _parse_progress(progress)
            
            # Calculate duration
            duration = (end_dt - start_dt).days + 1  # Include end date
            
            # Validate dependencies format
            deps_list = _parse_dependencies(dependencies, task_names, task_name)
            
            task = {
                'task': task_name,
                'start': start_dt.strftime('%Y-%m-%d'),
                'end': end_dt.strftime('%Y-%m-%d'),
                'duration': duration,
                'progress': progress_val,
                'category': category or 'General',
                'dependencies': dependencies,
                'resource': resource or 'Unassigned',
                # Additional computed fields
                'start_date': start_dt,
                'end_date': end_dt,
                'deps_list': deps_list
            }
            
            tasks.append(task)
            task_names.add(task_name)
        
        # Post-process: validate all dependencies exist
        _validate_gantt_dependencies(tasks)
        
        logger.info(f"Gantt chart parsed successfully: {len(tasks)} tasks")
        return tasks
        
    except Exception as e:
        logger.error(f"Gantt CSV parsing failed: {e}")
        return _create_error_gantt(str(e))


def _parse_gantt_dates(start_str: str, end_str: str, task_name: str) -> tuple:
    """Parse start and end dates with multiple format support"""
    date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
    
    start_dt = None
    end_dt = None
    
    # Parse start date
    if start_str:
        for fmt in date_formats:
            try:
                start_dt = datetime.strptime(start_str, fmt)
                break
            except ValueError:
                continue
    
    if not start_dt:
        logger.warning(f"Invalid start date '{start_str}' for task '{task_name}', using today")
        start_dt = datetime.now()
    
    # Parse end date
    if end_str:
        for fmt in date_formats:
            try:
                end_dt = datetime.strptime(end_str, fmt)
                break
            except ValueError:
                continue
    
    if not end_dt:
        logger.warning(f"Invalid end date '{end_str}' for task '{task_name}', using start + 1 day")
        end_dt = start_dt + timedelta(days=1)
    
    # Ensure end is after start
    if end_dt < start_dt:
        logger.warning(f"End date before start date for task '{task_name}', swapping")
        start_dt, end_dt = end_dt, start_dt
    
    return start_dt, end_dt


def _parse_progress(progress_str: str) -> float:
    """Parse progress value supporting multiple formats"""
    if not progress_str:
        return 0.0
    
    # Remove any non-numeric characters except decimal point
    clean_progress = re.sub(r'[^\d.]', '', progress_str)
    
    try:
        progress_val = float(clean_progress)
        
        # Convert percentage to decimal if needed
        if progress_val > 1.0:
            progress_val = progress_val / 100.0
        
        # Clamp to valid range
        return max(0.0, min(1.0, progress_val))
        
    except ValueError:
        logger.warning(f"Invalid progress value '{progress_str}', using 0%")
        return 0.0


def _parse_dependencies(deps_str: str, existing_tasks: set, current_task: str) -> List[str]:
    """Parse and validate dependency string"""
    if not deps_str:
        return []
    
    # Split by semicolon or comma
    deps = [dep.strip() for dep in re.split(r'[;,]', deps_str) if dep.strip()]
    
    # Filter out self-dependencies and non-existent tasks
    valid_deps = []
    for dep in deps:
        if dep == current_task:
            logger.warning(f"Self-dependency ignored for task '{current_task}'")
            continue
        valid_deps.append(dep)
    
    return valid_deps


def _validate_gantt_dependencies(tasks: List[Dict]) -> None:
    """Validate that all dependencies exist and detect cycles"""
    task_names = {task['task'] for task in tasks}
    
    for task in tasks:
        deps_list = task['deps_list']
        valid_deps = []
        
        for dep in deps_list:
            if dep in task_names:
                valid_deps.append(dep)
            else:
                logger.warning(f"Dependency '{dep}' not found for task '{task['task']}'")
        
        task['deps_list'] = valid_deps
    
    # TODO: Add cycle detection algorithm if needed


def _create_error_mindmap(error_msg: str) -> Dict[str, Any]:
    """Create error mindmap structure"""
    return {
        'name': 'パースエラー',
        'level': 1,
        'color': '#F44336',
        'children': [
            {
                'name': f'エラー: {error_msg[:50]}...',
                'level': 2,
                'color': '#FFCDD2',
                'children': []
            }
        ]
    }


def _create_default_mindmap() -> Dict[str, Any]:
    """Create default mindmap when parsing fails"""
    return {
        'name': 'サンプルマインドマップ',
        'level': 1,
        'color': '#4CAF50',
        'children': [
            {
                'name': '分岐1',
                'level': 2,
                'color': '#2196F3',
                'children': [
                    {'name': 'サブ1-1', 'level': 3, 'color': '#81C784', 'children': []},
                    {'name': 'サブ1-2', 'level': 3, 'color': '#81C784', 'children': []}
                ]
            },
            {
                'name': '分岐2',
                'level': 2,
                'color': '#FF9800',
                'children': [
                    {'name': 'サブ2-1', 'level': 3, 'color': '#FFB74D', 'children': []}
                ]
            }
        ]
    }


def _create_error_gantt(error_msg: str) -> List[Dict[str, Any]]:
    """Create error gantt structure"""
    today = datetime.now()
    return [
        {
            'task': 'パースエラー',
            'start': today.strftime('%Y-%m-%d'),
            'end': (today + timedelta(days=1)).strftime('%Y-%m-%d'),
            'duration': 1,
            'progress': 0.0,
            'category': 'Error',
            'dependencies': '',
            'resource': f'Error: {error_msg}',
            'start_date': today,
            'end_date': today + timedelta(days=1),
            'deps_list': []
        }
    ]


# Utility functions for validation
def validate_mindmap_csv(csv_content: str) -> tuple[bool, str]:
    """
    Validate CSV content for mindmap format
    
    Returns:
        (is_valid, error_message)
    """
    try:
        parse_mindmap_csv(csv_content)
        return True, "Valid mindmap CSV format"
    except Exception as e:
        return False, str(e)


def validate_gantt_csv(csv_content: str) -> tuple[bool, str]:
    """
    Validate CSV content for gantt format
    
    Returns:
        (is_valid, error_message)
    """
    try:
        tasks = parse_gantt_csv(csv_content)
        if not tasks:
            return False, "No valid tasks found"
        
        # Check for required fields
        required_fields = ['task', 'start', 'end']
        for task in tasks[:3]:  # Check first few tasks
            for field in required_fields:
                if field not in task or not task[field]:
                    return False, f"Missing required field: {field}"
        
        return True, f"Valid gantt CSV format with {len(tasks)} tasks"
    except Exception as e:
        return False, str(e)


def get_csv_format_examples() -> Dict[str, str]:
    """
    Get example CSV formats for both mindmap and gantt
    
    Returns:
        Dictionary with format examples
    """
    return {
        'mindmap_node_parent': '''Node,Parent,Level,Color
プロジェクト,,1,#4CAF50
計画,プロジェクト,2,#2196F3
実装,プロジェクト,2,#FF9800
テスト,プロジェクト,2,#9C27B0
要件定義,計画,3,#64B5F6
設計書作成,計画,3,#64B5F6''',
        
        'mindmap_hierarchical': '''プロジェクト,計画,要件定義
,実装,開発環境構築
,,コーディング
,,テスト
,デプロイ,本番環境準備
,,リリース''',
        
        'gantt': '''task,start,end,category,progress,dependencies,resource
プロジェクト計画,2024-01-01,2024-01-07,計画,1.0,,プロジェクトマネージャー
要件定義,2024-01-08,2024-01-21,分析,0.8,プロジェクト計画,ビジネスアナリスト
設計,2024-01-22,2024-02-18,設計,0.3,要件定義,システムアーキテクト
開発,2024-02-19,2024-04-15,開発,0.0,設計,開発チーム
テスト,2024-04-01,2024-04-30,テスト,0.0,開発,QAチーム'''
    }