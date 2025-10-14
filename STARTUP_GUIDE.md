# 🚀 D3-Mind-Flow-Editor 起動ガイド

## 🎯 問題解決済み

**以前のエラー:** `cannot access local variable 'QTimer' where it is not associated with a value`  
**状態:** ✅ **完全解決済み**

---

## 🔧 推奨起動方法

### 1. 安全起動スクリプト（推奨）
```bash
python3 safe_launch.py
```

**特徴:**
- 📋 包括的な事前チェック
- 🛡️ セーフモード自動フォールバック  
- 🔍 依存関係検証
- ⚡ 最適なモード自動選択

### 2. 直接起動
```bash
python3 src/main.py
```

### 3. 基本テスト
```bash
python3 test_basic_startup.py
```

---

## 🛠️ 解決された問題

### ✅ QTimerエラー修正
- **原因:** `QTimer.singleShot()`の変数スコープ問題
- **解決:** 適切なタイマーオブジェクトインスタンス化
- **場所:** `src/main.py` lines 334-335

### ✅ PySide6 6.10+ 互換性
- **WebEngine互換性:** 非推奨属性修正済み
- **インポートエラーハンドリング:** 包括的フォールバック
- **QApplication シングルトン:** 競合解決済み

### ✅ 環境対応
- **ヘッドレス環境:** オフスクリーンプラットフォーム対応
- **依存関係:** オプションモジュール graceful degradation
- **エラーハンドリング:** 全UIコンポーネント安全初期化

---

## 📋 起動モード

### 🚀 フルモード
- 全機能利用可能
- WebEngine プレビュー
- 完全なエクスポート機能
- リアルタイム統計

### 🛡️ セーフモード  
- 基本機能のみ
- 依存関係問題時の自動フォールバック
- 最低限の安定動作

---

## 🎯 システム要件

### ✅ 必須
- **Python:** 3.8+ 
- **PySide6:** 6.6+ (6.10+ 完全対応)

### ⚡ オプション（機能拡張）
- **WebEngine:** プレビュー機能
- **Playwright:** エクスポート機能
- **Pillow:** 画像処理

---

## 🔍 トラブルシューティング

### 起動エラーが発生した場合

1. **安全起動を試行:**
   ```bash
   python3 safe_launch.py
   ```

2. **基本テストを実行:**
   ```bash
   python3 test_basic_startup.py
   ```

3. **依存関係確認:**
   ```bash
   pip install -r requirements_stable.txt
   ```

### よくある問題

#### `QTimer` エラー
- **状態:** ✅ 解決済み
- **対策:** 最新コードを使用

#### プラットフォームプラグインエラー
- **対策:** 自動でオフスクリーンモード設定済み
- **環境変数:** `QT_QPA_PLATFORM=offscreen`

#### WebEngine不利用可能
- **影響:** プレビュー機能制限
- **対策:** セーフモードで継続動作

---

## 🎉 成功した機能

### ✅ 確認済み動作
- アプリケーション起動
- 基本UI表示
- エクスポート機能
- リアルタイム統計
- サンプルデータ読み込み
- 設定管理
- データベース操作

### 🚀 即座に利用可能
- **マインドマップ作成**
- **フローチャート作成**  
- **ガントチャート作成**
- **HTML/PNG/SVG/PDF エクスポート**
- **プレビュー表示**
- **統計情報表示**

---

## 📞 サポート

問題が発生した場合は、以下の情報と共にお知らせください:

```bash
# システム情報収集
python3 safe_launch.py > startup_log.txt 2>&1
```

**GitHub Issues:** https://github.com/seyaytua/d3-mind-flow-editor/issues  
**Pull Request:** https://github.com/seyaytua/d3-mind-flow-editor/pull/1

---

**🎯 すべての未実装問題が解決され、安定した動作が確保されています！**