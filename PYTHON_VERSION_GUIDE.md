# 🐍 Python バージョン互換性ガイド

## 🎯 推奨 Python バージョン

### ✅ **最推奨: Python 3.11.x**
```bash
# pyenvを使用した場合
pyenv install 3.11.9
pyenv local 3.11.9

# 仮想環境作成
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 最適化された依存関係インストール
pip install -r requirements_python311.txt
```

**理由:**
- 🔒 **安定性抜群** - 長期テスト済み
- ⚡ **最適化済み** - PySide6との相性良好
- 🛡️ **問題回避** - 既知の問題を回避
- 🎯 **D3-Mind-Flow-Editor テスト済み**

---

## ⚠️ バージョン別互換性

### 🟢 **Python 3.11.x (推奨)**
- ✅ 完全サポート
- ✅ 全機能動作確認済み
- ✅ 最適なパフォーマンス

### 🟡 **Python 3.12.x (注意)**
- ⚠️ 一部新機能で非互換の可能性
- ✅ 基本機能は動作
- 🔧 互換性モードで自動調整

### 🟡 **Python 3.13.x (要注意)**
- ⚠️ 非常に新しく、未テストの問題あり
- ⚠️ PySide6との組み合わせで予期しない問題
- 🛡️ 安全起動スクリプトで自動対応

### 🔴 **Python 3.8-3.10 (古い)**
- ⚠️ サポート終了予定
- 🔧 基本機能は動作するが非推奨

---

## 🚀 バージョン確認と切り替え

### **現在のバージョン確認**
```bash
python --version
# または
python3 --version
```

### **pyenv使用（推奨）**
```bash
# 利用可能バージョン確認
pyenv install --list | grep 3.11

# Python 3.11.9 インストール
pyenv install 3.11.9

# プロジェクト用に設定
cd d3-mind-flow-editor
pyenv local 3.11.9

# 確認
python --version
```

### **conda使用**
```bash
# Python 3.11環境作成
conda create -n d3editor python=3.11

# 環境切り替え
conda activate d3editor

# 確認
python --version
```

---

## 🛠️ バージョン問題の対処

### **Python 3.13.x 使用時**
アプリケーションが自動的に警告を表示し、互換性モードで動作します：

```
⚠️  Warning: Python 3.13 detected
   Recommended: Python 3.11.x for maximum stability
   Continuing with compatibility mode...
```

### **問題が発生した場合**
1. **Python 3.11.9 にダウングレード**（最も確実）
2. **仮想環境を作り直し**
3. **キャッシュクリア:** `pip cache purge`
4. **再インストール:** `pip install -r requirements_python311.txt`

---

## 📋 バージョン別テスト状況

| Python Version | Status | 安定性 | 推奨度 |
|---------------|--------|--------|-------|
| **3.11.9** | ✅ 完全テスト済み | 🟢 最高 | ⭐⭐⭐ |
| **3.11.8** | ✅ 完全テスト済み | 🟢 最高 | ⭐⭐⭐ |
| **3.12.x** | ⚠️ 部分テスト | 🟡 良好 | ⭐⭐ |
| **3.13.x** | ⚠️ 基本テスト | 🟡 要注意 | ⭐ |
| **3.10.x** | ⚠️ 非推奨 | 🟡 古い | ⚠️ |

---

## 🎯 結論

**最も安全で確実:** Python 3.11.9 + requirements_python311.txt

現在 Python 3.13.x をお使いの場合でも、安全起動スクリプトが自動的に互換性を確保しますが、最適なエクスペリエンスのためには Python 3.11.x への切り替えを強く推奨します。