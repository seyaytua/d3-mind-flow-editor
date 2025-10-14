#!/usr/bin/env python3
"""
Help tab for D3-Mind-Flow-Editor
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QTabWidget, QScrollArea, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ..database.models import DiagramType
from ..utils.clipboard import ClipboardManager
from ..utils.logger import logger


class HelpTab(QWidget):
    """Help tab for displaying user guide and AI prompts"""
    
    def __init__(self):
        super().__init__()
        
        self.clipboard = ClipboardManager()
        
        self._setup_ui()
        self._setup_connections()
        
        logger.debug("Help tab initialized")
    
    def _setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("ヘルプ・ガイド")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Tab widget for different help sections
        self.help_tabs = QTabWidget()
        
        # Usage guide tab
        self._create_usage_tab()
        
        # AI prompts tab
        self._create_ai_prompts_tab()
        
        # Examples tab
        self._create_examples_tab()
        
        # FAQ tab
        self._create_faq_tab()
        
        layout.addWidget(self.help_tabs)
    
    def _setup_connections(self):
        """Setup signal connections"""
        pass
    
    def _create_usage_tab(self):
        """Create usage guide tab"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Usage guide content
        usage_text = QTextEdit()
        usage_text.setReadOnly(True)
        usage_text.setHtml(self._get_usage_guide_html())
        
        layout.addWidget(usage_text)
        
        scroll_area.setWidget(content_widget)
        self.help_tabs.addTab(scroll_area, "使い方")
    
    def _create_ai_prompts_tab(self):
        """Create AI prompts tab"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Introduction
        intro_label = QLabel("以下のプロンプトをAIにコピー&ペーストして図表を作成できます")
        intro_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(intro_label)
        
        # Mindmap prompts
        layout.addWidget(self._create_prompt_section(
            "マインドマップ用プロンプト",
            self._get_mindmap_prompt(),
            "#4CAF50"
        ))
        
        # Gantt chart prompts
        layout.addWidget(self._create_prompt_section(
            "ガントチャート用プロンプト", 
            self._get_gantt_prompt(),
            "#2196F3"
        ))
        
        # Flowchart prompts
        layout.addWidget(self._create_prompt_section(
            "フローチャート用プロンプト",
            self._get_flowchart_prompt(),
            "#FF9800"
        ))
        
        layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        self.help_tabs.addTab(scroll_area, "AIプロンプト")
    
    def _create_examples_tab(self):
        """Create examples tab"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Examples content
        examples_text = QTextEdit()
        examples_text.setReadOnly(True)
        examples_text.setHtml(self._get_examples_html())
        
        layout.addWidget(examples_text)
        
        scroll_area.setWidget(content_widget)
        self.help_tabs.addTab(scroll_area, "サンプル")
    
    def _create_faq_tab(self):
        """Create FAQ tab"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # FAQ content
        faq_text = QTextEdit()
        faq_text.setReadOnly(True)
        faq_text.setHtml(self._get_faq_html())
        
        layout.addWidget(faq_text)
        
        scroll_area.setWidget(content_widget)
        self.help_tabs.addTab(scroll_area, "よくある質問")
    
    def _create_prompt_section(self, title: str, prompt_text: str, color: str) -> QFrame:
        """Create a prompt section with copy button"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet(f"QFrame {{ border: 2px solid {color}; border-radius: 5px; padding: 5px; }}")
        
        layout = QVBoxLayout(frame)
        
        # Header with title and copy button
        header_layout = QHBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-weight: bold; color: {color}; font-size: 13px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        copy_button = QPushButton("📋 コピー")
        copy_button.setToolTip("このプロンプトをクリップボードにコピー")
        copy_button.clicked.connect(lambda: self._copy_prompt(prompt_text, title))
        header_layout.addWidget(copy_button)
        
        layout.addLayout(header_layout)
        
        # Prompt text
        text_edit = QTextEdit()
        text_edit.setPlainText(prompt_text)
        text_edit.setReadOnly(True)
        text_edit.setMaximumHeight(200)
        
        # Set monospace font
        font = QFont("Consolas", 9)
        font.setFamily("Monaco")  # macOS
        font.setFamily("DejaVu Sans Mono")  # Linux
        text_edit.setFont(font)
        
        layout.addWidget(text_edit)
        
        return frame
    
    def _copy_prompt(self, prompt_text: str, title: str):
        """Copy prompt to clipboard"""
        if self.clipboard.copy_text(prompt_text):
            QMessageBox.information(self, "成功", f"{title}をクリップボードにコピーしました。")
            logger.debug(f"Prompt copied: {title}")
        else:
            QMessageBox.warning(self, "エラー", "プロンプトのコピーに失敗しました。")
    
    def _get_usage_guide_html(self) -> str:
        """Get usage guide HTML content"""
        return """
        <html>
        <head>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; }
                h2 { color: #2196F3; border-bottom: 2px solid #2196F3; padding-bottom: 5px; }
                h3 { color: #4CAF50; }
                .step { background-color: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
                .tip { background-color: #fff3e0; padding: 10px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #ff9800; }
                code { background-color: #f5f5f5; padding: 2px 4px; border-radius: 3px; font-family: 'Courier New', monospace; }
            </style>
        </head>
        <body>
            <h2>📚 基本的な使い方</h2>
            
            <h3>🚀 クイックスタート</h3>
            <div class="step">
                <strong>1. 図の種類を選択</strong><br>
                左上のドロップダウンから「マインドマップ」「ガントチャート」「フローチャート」を選択
            </div>
            
            <div class="step">
                <strong>2. データを入力</strong><br>
                入力エリアにMermaid記法またはCSV形式でデータを入力
            </div>
            
            <div class="step">
                <strong>3. プレビュー確認</strong><br>
                右側のプレビューエリアでリアルタイムに図表を確認
            </div>
            
            <div class="step">
                <strong>4. 保存・エクスポート</strong><br>
                ツールバーの「保存」ボタンでデータベースに保存、「エクスポート」でファイル出力
            </div>
            
            <h3>💡 AI活用のコツ</h3>
            <div class="tip">
                <strong>AIプロンプトボタンを活用</strong><br>
                入力エリアの「📋 AIプロンプト」ボタンで、図の種類に応じたプロンプトテンプレートをコピーできます。
                これをChatGPTやClaude等のAIにペーストして図表データを生成してもらいましょう。
            </div>
            
            <h3>🎯 各図表の特徴</h3>
            
            <h4>マインドマップ</h4>
            <ul>
                <li>CSV形式で階層構造を表現</li>
                <li>ブレインストーミングやアイデア整理に最適</li>
                <li>空白セルで階層レベルを制御</li>
            </ul>
            
            <h4>ガントチャート</h4>
            <ul>
                <li>CSV形式でタスク、期間、依存関係を定義</li>
                <li>プロジェクト管理に最適</li>
                <li>進捗率と依存関係の視覚化</li>
            </ul>
            
            <h4>フローチャート</h4>
            <ul>
                <li>Mermaid記法でプロセスフローを定義</li>
                <li>業務プロセスやアルゴリズムの図解に最適</li>
                <li>条件分岐と処理フローの明確化</li>
            </ul>
            
            <h3>⌨️ ショートカットキー</h3>
            <ul>
                <li><code>Ctrl+N</code> - 新規作成</li>
                <li><code>Ctrl+S</code> - 保存</li>
                <li><code>Ctrl+O</code> - 開く</li>
                <li><code>Ctrl+C</code> - コピー</li>
                <li><code>Ctrl+V</code> - 貼り付け</li>
                <li><code>F5</code> - プレビュー更新</li>
            </ul>
            
            <h3>🔧 設定のカスタマイズ</h3>
            <p>「設定」タブでDPIスケーリング、エクスポート設定、表示設定をカスタマイズできます。</p>
            <ul>
                <li>高解像度ディスプレイ対応</li>
                <li>PNG/PDF出力品質設定</li>
                <li>自動保存間隔設定</li>
            </ul>
            
        </body>
        </html>
        """
    
    def _get_examples_html(self) -> str:
        """Get examples HTML content"""
        return """
        <html>
        <head>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; }
                h2 { color: #2196F3; border-bottom: 2px solid #2196F3; padding-bottom: 5px; }
                h3 { color: #4CAF50; }
                .example { background-color: #f5f5f5; padding: 15px; margin: 15px 0; border-radius: 5px; }
                pre { background-color: #fff; padding: 10px; border: 1px solid #ddd; border-radius: 3px; overflow-x: auto; }
                .description { margin-bottom: 10px; color: #666; }
            </style>
        </head>
        <body>
            <h2>📝 入力サンプル</h2>
            
            <h3>🧠 マインドマップ（CSV形式）</h3>
            
            <div class="example">
                <div class="description">プロジェクト企画のマインドマップ例</div>
                <pre>プロジェクト企画,,,
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
,,スケジュールリスク,</pre>
            </div>
            
            <h3>📊 ガントチャート（CSV形式）</h3>
            
            <div class="example">
                <div class="description">Webアプリ開発スケジュール例</div>
                <pre>task,start,end,category,progress,dependencies
企画・要件定義,2024-01-01,2024-01-15,Phase1,1.0,
UI/UX設計,2024-01-10,2024-01-25,Phase1,0.9,企画・要件定義
システム設計,2024-01-20,2024-02-05,Phase2,0.7,企画・要件定義
フロントエンド開発,2024-02-01,2024-02-28,Phase2,0.4,UI/UX設計
バックエンド開発,2024-02-01,2024-02-28,Phase2,0.4,システム設計
統合テスト,2024-02-25,2024-03-10,Phase3,0.1,フロントエンド開発;バックエンド開発
リリース準備,2024-03-05,2024-03-15,Phase3,0.0,統合テスト</pre>
            </div>
            
            <h3>🔄 フローチャート（Mermaid記法）</h3>
            
            <div class="example">
                <div class="description">ユーザー登録プロセス例</div>
                <pre>flowchart TD
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
    I --> L[トップページへ]</pre>
            </div>
            
            <div class="example">
                <div class="description">業務プロセス例（横方向レイアウト）</div>
                <pre>flowchart LR
    A[申請書受付] --> B{内容確認}
    B -->|OK| C[承認者へ転送]
    B -->|NG| D[差し戻し]
    C --> E{承認判定}
    E -->|承認| F[処理実行]
    E -->|却下| G[申請者へ通知]
    F --> H[完了報告]
    D --> A
    G --> I[プロセス終了]
    H --> I</pre>
            </div>
            
            <h3>💡 応用テクニック</h3>
            
            <h4>マインドマップの階層制御</h4>
            <p>空白セルの数で階層レベルを制御できます：</p>
            <ul>
                <li>A列: ルートレベル</li>
                <li>B列: 第1階層</li>
                <li>C列: 第2階層</li>
                <li>D列以降: さらに深い階層</li>
            </ul>
            
            <h4>ガントチャートの依存関係</h4>
            <p>dependenciesカラムでタスク間の依存関係を定義：</p>
            <ul>
                <li>単一依存: <code>前のタスク名</code></li>
                <li>複数依存: <code>タスク1;タスク2</code></li>
                <li>依存なし: 空欄</li>
            </ul>
            
        </body>
        </html>
        """
    
    def _get_faq_html(self) -> str:
        """Get FAQ HTML content"""
        return """
        <html>
        <head>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; }
                h2 { color: #2196F3; border-bottom: 2px solid #2196F3; padding-bottom: 5px; }
                h3 { color: #4CAF50; }
                .faq { background-color: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #4CAF50; }
                .question { font-weight: bold; color: #2196F3; margin-bottom: 10px; }
                .answer { margin-left: 10px; }
                .troubleshoot { background-color: #ffebee; padding: 10px; border-radius: 5px; border-left: 4px solid #f44336; }
            </style>
        </head>
        <body>
            <h2>❓ よくある質問</h2>
            
            <div class="faq">
                <div class="question">Q: プレビューが表示されません</div>
                <div class="answer">
                    A: 以下を確認してください：<br>
                    • 入力データが正しい形式になっているか<br>
                    • プレビューエリアで「🔄 更新」ボタンを押してみる<br>
                    • デバッグタブでエラーメッセージを確認<br>
                    • ブラウザのJavaScript機能が有効になっているか
                </div>
            </div>
            
            <div class="faq">
                <div class="question">Q: 保存したデータが見つかりません</div>
                <div class="answer">
                    A: 保存データは左下のリストパネルに表示されます。<br>
                    • 検索ボックスでタイトルや説明を検索可能<br>
                    • 「種類」ドロップダウンで図の種類でフィルタ可能<br>
                    • リストを「🔄」ボタンで更新してみる
                </div>
            </div>
            
            <div class="faq">
                <div class="question">Q: エクスポートした画像が荒い</div>
                <div class="answer">
                    A: 設定タブでエクスポート品質を調整できます：<br>
                    • PNG DPIを300以上に設定<br>
                    • 画像サイズを大きく設定<br>
                    • PDF形式ならベクター出力で高品質
                </div>
            </div>
            
            <div class="faq">
                <div class="question">Q: 文字が小さくて見えません</div>
                <div class="answer">
                    A: 高DPIディスプレイでの表示問題の可能性があります：<br>
                    • 設定タブでDPIスケーリングを調整<br>
                    • プレビューエリアのズームボタン（🔍+）を使用<br>
                    • システムの表示設定を確認
                </div>
            </div>
            
            <div class="faq">
                <div class="question">Q: CSVデータの階層がうまく表示されない</div>
                <div class="answer">
                    A: CSV形式の階層表現を確認してください：<br>
                    • 空白セルで階層レベルを制御<br>
                    • カンマ区切りが正しいか確認<br>
                    • 日本語の場合は適切にエンコードされているか<br>
                    • サンプルタブの例を参考にしてください
                </div>
            </div>
            
            <div class="faq">
                <div class="question">Q: Mermaid記法のエラーが出ます</div>
                <div class="answer">
                    A: Mermaid記法の構文を確認してください：<br>
                    • ノード名に特殊文字が含まれていないか<br>
                    • 矢印記法（-->）が正しいか<br>
                    • ノード形状の記法（[]、{}、()等）が正しいか<br>
                    • サンプルタブの例を参考にしてください
                </div>
            </div>
            
            <h3>🛠️ トラブルシューティング</h3>
            
            <div class="troubleshoot">
                <strong>アプリケーションが起動しない場合：</strong><br>
                1. Python 3.10以上がインストールされているか確認<br>
                2. 必要なパッケージがインストールされているか確認<br>
                3. 仮想環境が正しく有効化されているか確認<br>
                4. デバッグタブでエラーログを確認
            </div>
            
            <div class="troubleshoot">
                <strong>パフォーマンスが悪い場合：</strong><br>
                1. 設定タブでレンダリング品質を「低（動作優先）」に変更<br>
                2. アンチエイリアスを無効にする<br>
                3. 大量のデータを扱う場合は段階的に作成する<br>
                4. システムのメモリとCPU使用量を確認
            </div>
            
            <h3>📞 サポート情報</h3>
            <p>
                • プロジェクトページ: <a href="https://github.com/seyaytua/d3-mind-flow-editor">GitHub Repository</a><br>
                • バグレポート: Issuesページをご利用ください<br>
                • バージョン: 1.0.0<br>
                • 作者: seyaytua
            </p>
            
        </body>
        </html>
        """
    
    def _get_mindmap_prompt(self) -> str:
        """Get mindmap AI prompt"""
        return """以下のCSV形式でマインドマップを作成してください:

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
（ここにテーマを記入）についてのマインドマップを作成してください。"""
    
    def _get_gantt_prompt(self) -> str:
        """Get gantt chart AI prompt"""
        return """以下のCSV形式でガントチャートを作成してください:

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
（ここにテーマを記入）のプロジェクト計画をガントチャートで作成してください。
期間は（期間を記入）を想定してください。"""
    
    def _get_flowchart_prompt(self) -> str:
        """Get flowchart AI prompt"""
        return """以下のMermaid記法でフローチャートを作成してください:

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