# flow_res Examples

このフォルダには、`flow_res` ライブラリの各機能を示すサンプルコードが含まれています。

## サンプル一覧

### 1. `01_basic_usage.py` - 基本的な使い方
`Ok`、`Err`、`map`、`and_then` の基本的な使用方法を学びます。

**学習ポイント:**
- `Ok` と `Err` の作成
- `map` でチェーニング
- `and_then` で Result を返す操作をチェーン

実行:
```bash
python examples/01_basic_usage.py
```

### 2. `02_safe_decorator.py` - @safe デコレータ
例外を自動的に `Result` に変換する `@safe` デコレータの使い方。

**学習ポイント:**
- 既存の例外を発生させる関数を `Result` に変換
- 例外型が自動的にキャプチャされる

実行:
```bash
python examples/02_safe_decorator.py
```

### 3. `03_form_validation.py` - フォームバリデーション
複数のバリデーションを集約し、すべてのエラーを一度に表示する実践的な例。

**学習ポイント:**
- `combine_all` で複数結果を統合
- バリデーション場面での使用方法
- ユーザーフレンドリーなエラー表示

実行:
```bash
python examples/03_form_validation.py
```

### 4. `04_async_example.py` - 非同期操作
`AwaitableResult` を使用して async/await と統合する方法。

**学習ポイント:**
- `AwaitableResult` で非同期チェーニング
- await の前にメソッドチェーンが可能
- 非同期処理のエラーハンドリング

実行:
```bash
python examples/04_async_example.py
```

### 5. `05_railroad_oriented.py` - Railroad-Oriented Programming
複数のステップを"線路"のようにチェーンしていくパターン。

**学習ポイント:**
- 正常系と異常系の分岐
- `map_err` でエラーを変換
- パイプラインパターン

実行:
```bash
python examples/05_railroad_oriented.py
```

### 6. `06_combine_results.py` - 複数結果の統合
`combine` と `combine_all` の違いと使い分け。

**学習ポイント:**
- `combine`: 最初のエラーで停止
- `combine_all`: すべてのエラーを集約
- 複数バリデーションの実装方法

実行:
```bash
python examples/06_combine_results.py
```

## すべてのサンプルを実行

```bash
for file in examples/0*.py; do
    echo "=== Running $file ==="
    python "$file"
    echo
done
```

## 推奨される学習順序

1. **01_basic_usage.py** - 基本を理解
2. **02_safe_decorator.py** - デコレータを学ぶ
3. **05_railroad_oriented.py** - パターンを理解
4. **03_form_validation.py** - 実践的な例
5. **06_combine_results.py** - 高度な統合
6. **04_async_example.py** - 非同期処理

## さらに詳しく

詳細は [README.md](../README.md) を参照してください。
