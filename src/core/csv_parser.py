#!/usr/bin/env python3
"""
CSV parser for D3-Mind-Flow-Editor
Handles CSV data parsing for mind maps and Gantt charts
"""

import csv
import json
import re
from datetime import datetime, timedelta
from io import StringIO
from typing import Dict, List, Optional, Tuple, Any

from ..utils.logger import logger


class CSVParseError(Exception):
    """CSV parsing error"""
    pass


class CSVParser:
    """CSV parser for mind maps and Gantt charts"""
    
    @staticmethod
    def parse_mindmap_csv(csv_text: str) -> Dict[str, Any]:
        """Parse CSV data for mind map
        
        Args:
            csv_text: CSV formatted text
            
        Returns:
            Dictionary containing hierarchical data for D3.js
            
        Raises:
            CSVParseError: If CSV parsing fails
        """
        try:
            # Clean and normalize input
            csv_text = CSVParser._clean_csv_text(csv_text)
            
            # Parse CSV
            reader = csv.reader(StringIO(csv_text))
            rows = list(reader)
            
            if not rows:
                raise CSVParseError("CSV data is empty")
            
            # Build hierarchical structure
            root = CSVParser._build_mindmap_hierarchy(rows)
            
            logger.debug(f"Parsed mindmap CSV: {len(rows)} rows -> hierarchical structure")
            return root
            
        except Exception as e:
            logger.error(f"Failed to parse mindmap CSV: {e}")
            raise CSVParseError(f"Mindmap CSV parsing failed: {e}")
    
    @staticmethod
    def parse_gantt_csv(csv_text: str) -> Dict[str, Any]:
        """Parse CSV data for Gantt chart
        
        Args:
            csv_text: CSV formatted text with headers
            
        Returns:
            Dictionary containing tasks and timeline data
            
        Raises:
            CSVParseError: If CSV parsing fails
        """
        try:
            # Clean and normalize input
            csv_text = CSVParser._clean_csv_text(csv_text)
            
            # Parse CSV with headers
            reader = csv.DictReader(StringIO(csv_text))
            rows = list(reader)
            
            if not rows:
                raise CSVParseError("Gantt CSV data is empty")
            
            # Validate required columns
            required_columns = ['task', 'start', 'end']
            fieldnames = reader.fieldnames or []
            
            missing_columns = [col for col in required_columns if col not in fieldnames]
            if missing_columns:
                raise CSVParseError(f"Missing required columns: {', '.join(missing_columns)}")
            
            # Process tasks
            tasks = []
            for i, row in enumerate(rows):
                try:
                    task = CSVParser._process_gantt_task(row, i)
                    tasks.append(task)
                except Exception as e:
                    logger.warning(f"Error processing Gantt task row {i+1}: {e}")
                    continue
            
            if not tasks:
                raise CSVParseError("No valid tasks found in Gantt CSV")
            
            # Build result structure
            result = {
                'tasks': tasks,
                'start_date': min(task['startDate'] for task in tasks),
                'end_date': max(task['endDate'] for task in tasks),
                'total_tasks': len(tasks),
                'categories': list(set(task.get('category', 'Default') for task in tasks))
            }
            
            logger.debug(f"Parsed Gantt CSV: {len(tasks)} tasks")
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse Gantt CSV: {e}")
            raise CSVParseError(f"Gantt CSV parsing failed: {e}")
    
    @staticmethod
    def _clean_csv_text(csv_text: str) -> str:
        """Clean and normalize CSV text
        
        Args:
            csv_text: Raw CSV text
            
        Returns:
            Cleaned CSV text
        """
        # Remove BOM if present
        if csv_text.startswith('\ufeff'):
            csv_text = csv_text[1:]
        
        # Normalize line endings
        csv_text = csv_text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove leading/trailing whitespace
        csv_text = csv_text.strip()
        
        return csv_text
    
    @staticmethod
    def _build_mindmap_hierarchy(rows: List[List[str]]) -> Dict[str, Any]:
        """Build hierarchical structure from CSV rows
        
        Args:
            rows: List of CSV rows
            
        Returns:
            Root node of hierarchical structure
        """
        if not rows or not rows[0]:
            raise CSVParseError("Invalid mindmap CSV structure")
        
        # Find the root node (first non-empty cell in first row)
        root_name = None
        for cell in rows[0]:
            if cell and cell.strip():
                root_name = cell.strip()
                break
        
        if not root_name:
            raise CSVParseError("Root node not found in mindmap CSV")
        
        root = {
            'name': root_name,
            'children': []
        }
        
        # Process each row to build hierarchy
        for row_idx, row in enumerate(rows):
            CSVParser._process_mindmap_row(root, row, row_idx)
        
        return root
    
    @staticmethod
    def _process_mindmap_row(root: Dict[str, Any], row: List[str], row_idx: int):
        """Process a single mindmap CSV row
        
        Args:
            root: Root node to add to
            row: CSV row data
            row_idx: Row index for error reporting
        """
        # Skip empty rows
        if not any(cell.strip() for cell in row if cell):
            return
        
        # Find the path through the hierarchy
        path = []
        for cell in row:
            if cell and cell.strip():
                path.append(cell.strip())
        
        if len(path) < 2:  # Need at least root and one child
            return
        
        # Navigate/create the path
        current = root
        
        # Start from the second element (skip root)
        for i, node_name in enumerate(path[1:], 1):
            # Find existing child or create new one
            child = None
            
            if 'children' not in current:
                current['children'] = []
            
            # Look for existing child
            for existing_child in current['children']:
                if existing_child['name'] == node_name:
                    child = existing_child
                    break
            
            # Create new child if not found
            if child is None:
                child = {
                    'name': node_name,
                    'children': []
                }
                current['children'].append(child)
            
            current = child
    
    @staticmethod
    def _process_gantt_task(row: Dict[str, str], row_idx: int) -> Dict[str, Any]:
        """Process a single Gantt chart task
        
        Args:
            row: CSV row as dictionary
            row_idx: Row index for error reporting
            
        Returns:
            Processed task dictionary
            
        Raises:
            CSVParseError: If task processing fails
        """
        task_name = row.get('task', '').strip()
        if not task_name:
            raise CSVParseError(f"Row {row_idx+1}: Task name is required")
        
        # Parse dates
        start_date = CSVParser._parse_date(row.get('start', ''), f"Row {row_idx+1}: start")
        end_date = CSVParser._parse_date(row.get('end', ''), f"Row {row_idx+1}: end")
        
        if start_date > end_date:
            raise CSVParseError(f"Row {row_idx+1}: Start date must be before end date")
        
        # Parse progress
        progress = CSVParser._parse_progress(row.get('progress', '0'), f"Row {row_idx+1}: progress")
        
        # Process other fields
        category = row.get('category', 'Default').strip() or 'Default'
        dependencies = row.get('dependencies', '').strip()
        
        # Calculate duration
        duration = (end_date - start_date).days + 1
        
        task = {
            'task': task_name,
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d'),
            'startDate': start_date.isoformat(),
            'endDate': end_date.isoformat(),
            'category': category,
            'progress': progress,
            'duration': duration,
            'dependencies': dependencies if dependencies else None
        }
        
        return task
    
    @staticmethod
    def _parse_date(date_str: str, context: str) -> datetime:
        """Parse date string
        
        Args:
            date_str: Date string to parse
            context: Context for error reporting
            
        Returns:
            Parsed datetime object
            
        Raises:
            CSVParseError: If date parsing fails
        """
        date_str = date_str.strip()
        if not date_str:
            raise CSVParseError(f"{context}: Date is required")
        
        # Try different date formats
        date_formats = [
            '%Y-%m-%d',      # 2024-01-15
            '%Y/%m/%d',      # 2024/01/15
            '%m/%d/%Y',      # 01/15/2024
            '%d/%m/%Y',      # 15/01/2024
            '%Y-%m-%d %H:%M:%S',  # 2024-01-15 12:30:00
            '%Y-%m-%d %H:%M',     # 2024-01-15 12:30
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        raise CSVParseError(f"{context}: Invalid date format '{date_str}'. Use YYYY-MM-DD format")
    
    @staticmethod
    def _parse_progress(progress_str: str, context: str) -> float:
        """Parse progress value
        
        Args:
            progress_str: Progress string to parse
            context: Context for error reporting
            
        Returns:
            Progress as float between 0.0 and 1.0
            
        Raises:
            CSVParseError: If progress parsing fails
        """
        progress_str = progress_str.strip()
        
        if not progress_str:
            return 0.0
        
        try:
            # Handle percentage format
            if progress_str.endswith('%'):
                progress = float(progress_str[:-1]) / 100.0
            else:
                progress = float(progress_str)
            
            # Validate range
            if not (0.0 <= progress <= 1.0):
                raise ValueError(f"Progress must be between 0.0 and 1.0 (or 0% and 100%)")
            
            return progress
            
        except ValueError as e:
            raise CSVParseError(f"{context}: Invalid progress value '{progress_str}': {e}")
    
    @staticmethod
    def validate_mindmap_csv(csv_text: str) -> Tuple[bool, str]:
        """Validate mindmap CSV format
        
        Args:
            csv_text: CSV text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            CSVParser.parse_mindmap_csv(csv_text)
            return True, ""
        except CSVParseError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Validation error: {e}"
    
    @staticmethod
    def validate_gantt_csv(csv_text: str) -> Tuple[bool, str]:
        """Validate Gantt chart CSV format
        
        Args:
            csv_text: CSV text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            CSVParser.parse_gantt_csv(csv_text)
            return True, ""
        except CSVParseError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Validation error: {e}"
    
    @staticmethod
    def get_sample_mindmap_csv() -> str:
        """Get sample mindmap CSV data
        
        Returns:
            Sample CSV string
        """
        return """プロジェクト企画,,,
,市場調査,,
,,ターゲット分析,
,,競合調査,
,,トレンド分析,
,技術検討,,
,,フロントエンド,
,,,React
,,,Vue.js
,,バックエンド,
,,,Node.js
,,,Python
,リスク管理,,
,,技術リスク,
,,スケジュールリスク,"""
    
    @staticmethod
    def get_sample_gantt_csv() -> str:
        """Get sample Gantt chart CSV data
        
        Returns:
            Sample CSV string
        """
        return """task,start,end,category,progress,dependencies
企画・要件定義,2024-01-01,2024-01-15,Phase1,1.0,
UI/UX設計,2024-01-10,2024-01-25,Phase1,0.9,企画・要件定義
システム設計,2024-01-20,2024-02-05,Phase2,0.7,企画・要件定義
フロントエンド開発,2024-02-01,2024-02-28,Phase2,0.4,UI/UX設計
バックエンド開発,2024-02-01,2024-02-28,Phase2,0.4,システム設計
統合テスト,2024-02-25,2024-03-10,Phase3,0.1,フロントエンド開発;バックエンド開発
リリース準備,2024-03-05,2024-03-15,Phase3,0.0,統合テスト"""


class CSVGenerator:
    """CSV data generator for templates and examples"""
    
    @staticmethod
    def generate_mindmap_template(theme: str = "プロジェクト") -> str:
        """Generate mindmap CSV template
        
        Args:
            theme: Theme for the mindmap
            
        Returns:
            CSV template string
        """
        templates = {
            "プロジェクト": f"""{theme},,,
,企画,,
,,要件定義,
,,市場調査,
,開発,,
,,設計,
,,,UI設計
,,,システム設計
,,実装,
,テスト,,
,,単体テスト,
,,結合テスト,""",
            
            "学習": f"""{theme},,,
,基礎知識,,
,,理論学習,
,,実践演習,
,応用,,
,,プロジェクト,
,,発表準備,
,評価,,
,,自己評価,
,,フィードバック,""",
            
            "ビジネス": f"""{theme},,,
,戦略立案,,
,,市場分析,
,,競合分析,
,実行,,
,,マーケティング,
,,営業活動,
,評価,,
,,KPI測定,
,,改善案,"""
        }
        
        return templates.get(theme, templates["プロジェクト"])
    
    @staticmethod
    def generate_gantt_template(
        project_name: str = "新規プロジェクト",
        start_date: Optional[datetime] = None,
        duration_weeks: int = 12
    ) -> str:
        """Generate Gantt chart CSV template
        
        Args:
            project_name: Name of the project
            start_date: Project start date
            duration_weeks: Project duration in weeks
            
        Returns:
            CSV template string
        """
        if start_date is None:
            start_date = datetime.now()
        
        tasks = [
            ("企画フェーズ", 0, 2, "Phase1", 0.0),
            ("要件定義", 0, 3, "Phase1", 0.0),
            ("設計フェーズ", 2, 4, "Phase2", 0.0),
            ("開発フェーズ", 4, 8, "Phase2", 0.0),
            ("テストフェーズ", 8, 10, "Phase3", 0.0),
            ("リリース準備", 10, 12, "Phase3", 0.0),
        ]
        
        csv_lines = ["task,start,end,category,progress,dependencies"]
        
        for i, (task_name, start_week, end_week, category, progress) in enumerate(tasks):
            task_start = start_date + timedelta(weeks=start_week)
            task_end = start_date + timedelta(weeks=end_week)
            
            # Add dependencies
            dependencies = ""
            if i > 0 and i % 2 == 1:  # Every other task depends on previous
                dependencies = tasks[i-1][0]
            
            csv_lines.append(
                f"{task_name},"
                f"{task_start.strftime('%Y-%m-%d')},"
                f"{task_end.strftime('%Y-%m-%d')},"
                f"{category},"
                f"{progress},"
                f"{dependencies}"
            )
        
        return "\n".join(csv_lines)