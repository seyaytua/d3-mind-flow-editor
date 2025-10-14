#!/usr/bin/env python3
"""
Sample data loader for D3-Mind-Flow-Editor
Provides initial demonstration data for different diagram types
"""

from ..database.models import DiagramType


class SampleLoader:
    """Sample data loader for demonstration purposes"""
    
    def __init__(self):
        """Initialize sample loader"""
        self.samples = {
            DiagramType.MINDMAP: self._get_mindmap_sample(),
            DiagramType.FLOWCHART: self._get_flowchart_sample(),
            DiagramType.GANTT: self._get_gantt_sample()
        }
    
    def get_sample(self, diagram_type: str) -> str:
        """Get sample data for specified diagram type"""
        return self.samples.get(diagram_type, "")
    
    def _get_mindmap_sample(self) -> str:
        """Get mindmap sample data"""
        return """# D3-Mind-Flow-Editor デモ
## 主な機能
### マインドマップ作成
- D3.js による可視化
- リアルタイムプレビュー
- インタラクティブ操作
### エクスポート機能
- HTML形式
- PNG画像
- SVG形式
- PDF文書
## 技術スタック
### フロントエンド
- D3.js v7
- HTML5/CSS3
- JavaScript ES6+
### バックエンド  
- Python 3.8+
- PySide6/Qt6
- SQLite3
### その他
- Playwright
- CSV解析
- Mermaid記法"""

    def _get_flowchart_sample(self) -> str:
        """Get flowchart sample data"""
        return """graph TD
    A[開始] --> B{条件分岐}
    B -->|Yes| C[処理1]
    B -->|No| D[処理2]
    C --> E[結合点]
    D --> E
    E --> F[終了]
    
    subgraph "サブプロセス"
    G[サブ処理1]
    H[サブ処理2] 
    G --> H
    end
    
    C --> G
    H --> E"""

    def _get_gantt_sample(self) -> str:
        """Get gantt chart sample data"""
        return """task,start_date,end_date,progress,dependencies
プロジェクト企画,2024-01-01,2024-01-15,100,
要件定義,2024-01-10,2024-01-25,100,プロジェクト企画
基本設計,2024-01-20,2024-02-10,80,要件定義
詳細設計,2024-02-05,2024-02-25,60,基本設計
フロントエンド開発,2024-02-20,2024-03-20,40,詳細設計
バックエンド開発,2024-02-20,2024-03-25,30,詳細設計
テスト,2024-03-15,2024-04-05,10,フロントエンド開発
デプロイ,2024-04-01,2024-04-10,0,テスト"""