# 🚀 D3-Mind-Flow-Editor Quick Start Guide (macOS)

## ✅ PySide6 6.10+ 完全対応済み

この手順で確実に起動できます。

## 📋 必要な手順

### 1. 依存関係の確認
```bash
cd /Users/syuta/Downloads/webapp
source venv/bin/activate
pip list | grep PySide6  # バージョン確認
```

### 2. Playwright ブラウザーエンジンのインストール
```bash
# エクスポート機能に必要（初回のみ）
python -m playwright install chromium
```

### 3. アプリケーション起動
```bash
cd src
python main.py
```

## 🔧 トラブルシューティング

### 問題1: 依存関係エラー
```bash
pip install --upgrade -r requirements.txt
```

### 問題2: Playwright未インストール
```bash
python -m playwright install --force chromium
```

### 問題3: 権限エラー (macOS)
```bash
# 必要に応じて
pip install --user playwright
python -m playwright install --force
```

## ✅ 動作確認方法

起動後、以下が表示されれば成功：
- メインウィンドウが開く
- 左側に入力パネル
- 右側にプレビューエリア
- タブ: プレビュー、デバッグ、ヘルプ、設定

## 🎯 機能テスト

1. **マインドマップ**: 入力エリアにCSVデータ入力
2. **フローチャート**: Mermaid記法でフローチャート作成
3. **エクスポート**: HTML/PNG/SVG/PDF出力テスト

## 📞 サポート

起動できない場合は、以下の情報を確認：
- Python バージョン: `python --version`
- PySide6 バージョン: `pip show PySide6`
- エラーメッセージの詳細