# D3-Mind-Flow-Editor

D3.jsを使用したマインドマップ・フローチャート・ガントチャート作成デスクトップアプリケーション

## 概要

D3-Mind-Flow-Editorは、PySide6とD3.jsを使用して構築された高機能なダイアグラム作成ツールです。マインドマップ、フローチャート、ガントチャートの作成・編集・エクスポートに対応しています。

## 主な機能

- **マインドマップ作成**: CSV形式での階層構造入力
- **フローチャート作成**: Mermaid記法に対応
- **ガントチャート作成**: CSV形式でのプロジェクト計画
- **インタラクティブな操作**: ドラッグ、ズーム、折りたたみ機能
- **多様なエクスポート形式**: HTML、PNG、SVG、PDF
- **AIプロンプト支援**: 図表作成のためのテンプレート提供
- **高DPI対応**: Retina/4Kディスプレイ完全対応

## システム要件

- Python 3.10以上
- macOS または Windows 10/11
- 4GB以上のRAM推奨

## インストール

```bash
# リポジトリのクローン
git clone https://github.com/seyaytua/d3-mind-flow-editor.git
cd d3-mind-flow-editor

# 仮想環境の作成
python -m venv .venv

# 仮想環境の有効化（macOS/Linux）
source .venv/bin/activate

# 仮想環境の有効化（Windows）
.venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# Playwrightブラウザのインストール
python -m playwright install chromium
```

## 使用方法

```bash
# アプリケーションの起動
python src/main.py
```

## 開発環境

```bash
# 開発用依存関係のインストール
pip install pytest pytest-qt black flake8

# テストの実行
pytest tests/

# コードフォーマット
black src/ tests/
```

## ライセンス

MIT License

## 作成者

seyaytua

## 貢献

プルリクエストやイシューの報告を歓迎します。