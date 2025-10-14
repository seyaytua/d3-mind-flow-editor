#!/usr/bin/env python3
"""
Input panel for D3-Mind-Flow-Editor
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton,
    QTextEdit, QLabel, QSplitter, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

from ..database.models import Diagram, DiagramType
from ..database.db_manager import DatabaseManager
from ..utils.config import Config
from ..utils.logger import logger
from ..utils.clipboard import ClipboardManager


class InputPanel(QWidget):
    """Input panel for diagram data entry"""
    
    # Signals
    content_changed = Signal()
    diagram_type_changed = Signal(str)
    
    def __init__(self, config: Config, db_manager: DatabaseManager):
        super().__init__()
        
        self.config = config
        self.db_manager = db_manager
        self.clipboard = ClipboardManager()
        
        # Debounce timer for content changes
        self.change_timer = QTimer()
        self.change_timer.setSingleShot(True)
        self.change_timer.timeout.connect(self._emit_content_changed)
        
        self._setup_ui()
        self._setup_connections()
        
        logger.debug("Input panel initialized")
    
    def _setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header section
        header_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("入力エリア")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)
        
        # Diagram type selection
        type_layout = QHBoxLayout()
        type_label = QLabel("図の種類:")
        type_layout.addWidget(type_label)
        
        self.type_combo = QComboBox()
        display_names = DiagramType.display_names()
        for type_key, display_name in display_names.items():
            self.type_combo.addItem(display_name, type_key)
        type_layout.addWidget(self.type_combo)
        
        type_layout.addStretch()
        header_layout.addLayout(type_layout)
        
        # AI Prompt button
        self.ai_prompt_button = QPushButton("📋 AIプロンプト")
        self.ai_prompt_button.setToolTip("AI用のプロンプトテンプレートをコピー")
        header_layout.addWidget(self.ai_prompt_button)
        
        layout.addLayout(header_layout)
        
        # Text input area
        input_label = QLabel("データ入力 (Mermaid記法 / CSV形式):")
        input_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(input_label)
        
        # Text editor
        self.text_edit = QTextEdit()
        self.text_edit.setMinimumHeight(200)
        
        # Set monospace font for better formatting
        font = QFont("Courier New", 10)  # Fallback to system monospace
        font.setFamily("Monaco")  # macOS
        font.setFamily("Consolas")  # Windows
        font.setFamily("DejaVu Sans Mono")  # Linux
        self.text_edit.setFont(font)
        
        # Enable line numbers if configured
        if self.config.get('editor.show_line_numbers', True):
            self.text_edit.setLineWrapMode(QTextEdit.NoWrap)
        
        # Enable word wrap if configured
        if self.config.get('editor.word_wrap', True):
            self.text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        
        layout.addWidget(self.text_edit)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("クリア")
        self.clear_button.setToolTip("入力内容をクリア")
        button_layout.addWidget(self.clear_button)
        
        self.copy_button = QPushButton("コピー")
        self.copy_button.setToolTip("入力内容をクリップボードにコピー")
        button_layout.addWidget(self.copy_button)
        
        self.paste_button = QPushButton("貼り付け")
        self.paste_button.setToolTip("クリップボードから貼り付け")
        button_layout.addWidget(self.paste_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Set placeholder text
        self._set_placeholder_text()
        
        # Set initial sample data for demonstration
        self._set_initial_sample_data()
    
    def _setup_connections(self):
        """Setup signal connections"""
        # Diagram type change
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        
        # Text change with debouncing
        self.text_edit.textChanged.connect(self._on_text_changed)
        
        # Button connections
        self.ai_prompt_button.clicked.connect(self._copy_ai_prompt)
        self.clear_button.clicked.connect(self.clear)
        self.copy_button.clicked.connect(self.copy_content)
        self.paste_button.clicked.connect(self.paste_content)
    
    def _set_placeholder_text(self):
        """Set appropriate placeholder text based on diagram type"""
        diagram_type = self.get_diagram_type()
        
        placeholders = {
            DiagramType.MINDMAP: """CSV形式でマインドマップを入力してください。

例:
プロジェクト,,,
,企画,,
,,市場調査,
,,競合分析,
,開発,,
,,設計,
,,,UI設計
,,,DB設計
,,実装,""",
            
            DiagramType.FLOWCHART: """Mermaid記法でフローチャートを入力してください。

例:
flowchart TD
    A[開始] --> B{条件分岐}
    B -->|Yes| C[処理1]
    B -->|No| D[処理2]
    C --> E[終了]
    D --> E""",
            
            DiagramType.GANTT: """CSV形式でガントチャートを入力してください。

例:
task,start,end,category,progress,dependencies
要件定義,2024-01-01,2024-01-15,Phase1,1.0,
基本設計,2024-01-10,2024-01-25,Phase1,0.8,要件定義
詳細設計,2024-01-20,2024-02-10,Phase2,0.5,基本設計"""
        }
        
        self.text_edit.setPlaceholderText(placeholders.get(diagram_type, ""))
    
    def _on_type_changed(self):
        """Handle diagram type change"""
        diagram_type = self.get_diagram_type()
        self._set_placeholder_text()
        
        # Set sample data if content is empty
        if not self.get_content().strip():
            self._set_initial_sample_data()
        
        self.diagram_type_changed.emit(diagram_type)
        logger.debug(f"Diagram type changed to: {diagram_type}")
    
    def _set_initial_sample_data(self):
        """Set initial sample data for demonstration"""
        if self.get_content().strip():
            return  # Don't override existing content
            
        diagram_type = self.get_diagram_type()
        
        sample_data = {
            DiagramType.MINDMAP: """プロジェクト企画,,,
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
,,スケジュールリスク,""",
            
            DiagramType.FLOWCHART: """flowchart TD
    A[ユーザー登録開始] --> B{メールアドレス入力}
    B -->|有効| C[パスワード設定]
    B -->|無効| D[エラー表示]
    D --> B
    C --> E{パスワード強度チェック}
    E -->|弱い| F[強化要求]
    F --> C
    E -->|強い| G[利用規約確認]
    G -->|同意| H[アカウント作成]
    G -->|拒否| I[登録中止]
    H --> J[確認メール送信]
    J --> K[登録完了]
    I --> L[トップページへ]""",
            
            DiagramType.GANTT: """task,start,end,category,progress,dependencies
企画・要件定義,2024-01-01,2024-01-15,Phase1,1.0,
UI/UX設計,2024-01-10,2024-01-25,Phase1,0.9,企画・要件定義
システム設計,2024-01-20,2024-02-05,Phase2,0.7,企画・要件定義
フロントエンド開発,2024-02-01,2024-02-28,Phase2,0.4,UI/UX設計
バックエンド開発,2024-02-01,2024-02-28,Phase2,0.4,システム設計
統合テスト,2024-02-25,2024-03-10,Phase3,0.1,フロントエンド開発;バックエンド開発
リリース準備,2024-03-05,2024-03-15,Phase3,0.0,統合テスト"""
        }
        
        self.set_content(sample_data.get(diagram_type, ""))
        logger.debug(f"Set initial sample data for {diagram_type}")
    
    def _on_text_changed(self):
        """Handle text change with debouncing"""
        # Restart timer to debounce rapid changes
        self.change_timer.start(500)  # 500ms delay
    
    def _emit_content_changed(self):
        """Emit content changed signal"""
        self.content_changed.emit()
    
    def _copy_ai_prompt(self):
        """Copy AI prompt template to clipboard"""
        diagram_type = self.get_diagram_type()
        
        # Get appropriate prompt template
        prompt_templates = self._get_ai_prompt_templates()
        prompt = prompt_templates.get(diagram_type, "")
        
        if prompt and self.clipboard.copy_text(prompt):
            QMessageBox.information(self, "成功", 
                                   f"{DiagramType.display_names().get(diagram_type)}用のAIプロンプトをクリップボードにコピーしました。")
        else:
            QMessageBox.warning(self, "エラー", "プロンプトのコピーに失敗しました。")
    
    def _get_ai_prompt_templates(self) -> dict:
        """Get AI prompt templates for each diagram type"""
        return {
            DiagramType.MINDMAP: """以下のCSV形式でマインドマップを作成してください:

【形式】
- A列に親ノード、B列に子ノード、C列に孫ノード...という階層構造で記述
- 空白セルで階層を表現
- 1行目はヘッダーなしで直接データを記述してください

【例】
プロジェクト,,,
,企画,,
,,市場調査,
,,競合分析,
,開発,,
,,設計,
,,,UI設計
,,,DB設計
,,実装,

【ルール】
- 各ノードは簡潔に（10文字以内推奨）
- 階層は最大5レベルまで
- 空白セルは必ず保持してください

【テーマ】
（ここにテーマを記入）についてのマインドマップを作成してください。""",
            
            DiagramType.GANTT: """以下のCSV形式でガントチャートを作成してください:

【形式】
task,start,end,category,progress,dependencies
タスク名,開始日,終了日,カテゴリ名,進捗率,依存タスク

【ルール】
- 日付形式: YYYY-MM-DD（例: 2024-01-15）
- 進捗率: 0.0〜1.0の小数（0%=0.0, 50%=0.5, 100%=1.0）
- 依存関係: タスク名をセミコロン区切り（例: タスク1;タスク2）
- 依存がない場合は空欄

【例】
要件定義,2024-01-01,2024-01-15,Phase1,1.0,
基本設計,2024-01-10,2024-01-25,Phase1,0.8,要件定義
詳細設計,2024-01-20,2024-02-10,Phase2,0.5,基本設計
実装,2024-02-01,2024-03-15,Phase2,0.3,詳細設計
テスト,2024-03-10,2024-03-30,Phase3,0.0,実装

【テーマ】
（ここにテーマを記入）のプロジェクト計画をガントチャートで作成してください。""",
            
            DiagramType.FLOWCHART: """以下のMermaid記法でフローチャートを作成してください:

【基本記法】
flowchart TD
    A[開始] --> B{条件分岐}
    B -->|Yes| C[処理1]
    B -->|No| D[処理2]
    C --> E[終了]
    D --> E

【方向指定】
- TD: 上から下（縦方向）
- LR: 左から右（横方向）
- TB: 上から下（TDと同じ）
- RL: 右から左

【ノード形状】
- [テキスト]: 四角形
- (テキスト): 角丸四角
- {テキスト}: 菱形（条件分岐）
- ((テキスト)): 円形
- [(テキスト)]: 台形

【矢印ラベル】
- A -->|ラベル| B: ラベル付き矢印

【ルール】
- ノード名は簡潔に（15文字以内）
- 分岐は必ず{菱形}を使用
- 開始と終了を明確に

【テーマ】
（ここにテーマを記入）の処理フローをフローチャートで作成してください。"""
        }
    
    def get_diagram_type(self) -> str:
        """Get currently selected diagram type"""
        return self.type_combo.currentData()
    
    def set_diagram_type(self, diagram_type: str):
        """Set diagram type"""
        for i in range(self.type_combo.count()):
            if self.type_combo.itemData(i) == diagram_type:
                self.type_combo.setCurrentIndex(i)
                break
    
    def get_content(self) -> str:
        """Get current text content"""
        return self.text_edit.toPlainText()
    
    def set_content(self, content: str):
        """Set text content"""
        self.text_edit.setPlainText(content)
    
    def clear(self):
        """Clear text content"""
        self.text_edit.clear()
        logger.debug("Input panel cleared")
    
    def copy_content(self):
        """Copy content to clipboard"""
        content = self.get_content()
        if content.strip():
            if self.clipboard.copy_text(content):
                logger.debug("Content copied to clipboard")
            else:
                QMessageBox.warning(self, "エラー", "コピーに失敗しました。")
        else:
            QMessageBox.information(self, "情報", "コピーする内容がありません。")
    
    def paste_content(self):
        """Paste content from clipboard"""
        text = self.clipboard.paste_text()
        if text:
            self.text_edit.insertPlainText(text)
            logger.debug("Content pasted from clipboard")
        else:
            QMessageBox.information(self, "情報", "クリップボードにテキストがありません。")
    
    def load_diagram(self, diagram: Diagram):
        """Load diagram data"""
        self.set_diagram_type(diagram.diagram_type)
        self.set_content(diagram.mermaid_data)
        logger.debug(f"Loaded diagram: {diagram.title}")
    
    def is_modified(self) -> bool:
        """Check if content has been modified"""
        return bool(self.get_content().strip())