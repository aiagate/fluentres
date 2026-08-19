# flow-res

Rust 言語の `Result` 型に範を仰いだ、Python 3.12+ 向けの小さく型付きのエラーハンドリングライブラリです。

予期できる失敗を `Result[T, E]` として戻り値に表し、成功・失敗の両方を呼び出し側のコードで明示的に扱えるようにします。Python の型チェッカーやランタイムがエラー処理を強制するものではありません。未処理の `Result` を無視することも、`unwrap()` で例外として伝播させることもできます。

`Err` は `Exception` のサブクラスだけを保持します。これは `unwrap()` が元の例外を再送出できるようにするための意図的な制約です。エラーコードや文字列などの値を失敗として扱いたい用途には向きません。

## 主要な特徴

* **型チェックを CI で検証**: ジェネリクスを活用し、成功値と例外型を pyright と mypy で検証します。
* **鉄道指向プログラミング（ROP）**: `map` や `and_then` によるメソッドチェーンにより、宣言的なエラーハンドリングを実現します。
* **非同期処理のネイティブサポート**: `@async_result` デコレータを通じて、非同期処理を `AwaitableResult` として透過的にチェーン可能です。
* **既存コードとの統合**: `@safe` デコレータを用いることで、既存の例外送出型関数を Result 型へ変換できます。
* **結果集約**: `combine`、`combine_lazy`、`combine_async`、`combine_all` により、複数の処理結果を集約します。
* **軽量設計**: Python 3.13 以上ではランタイム依存がなく、プロジェクトへの導入障壁が極めて低く抑えられています。Python 3.12 では型ガード互換性のため `typing-extensions` を使用します。

## インストール

```bash
pip install flow_res
```

※ Python 3.12 以上が必要です。Python 3.11 以下は対象外です。

## 実装ガイド

### 1. 基本的な定義とハンドリング

関数の戻り値に `Result` を指定することで、呼び出し側が成功・失敗の可能性をシグネチャから把握できます。Python 3.10 以降の構造的パターンマッチングで結果を処理できます。

```python
from flow_res import Result, Ok, Err

def divide(a: int, b: int) -> Result[float, ValueError]:
    """2つの数値の除算を行い、結果を Result 型で返却する"""
    if b == 0:
        return Err(ValueError("Division by zero"))
    return Ok(a / b)

result = divide(10, 2)
match result:
    case Ok(value):
        print(f"Success: {value}")
    case Err(error):
        print(f"Failure: {error}")
```

### 2. 関数型インターフェースによる連鎖処理 (Railroad-Oriented Programming)

`map` や `and_then` を用いることで、命令的な条件分岐を排除し、処理のパイプラインを構築できます。

```python
from flow_res import Err, Ok, Result

def validate_positive(x: int) -> Result[int, ValueError]:
    if x < 0:
        return Err(ValueError("Must be positive"))
    return Ok(x)

# 依存関係のある処理の連結
result = (
    Ok(5)
    .and_then(validate_positive)
    .map(lambda x: x * 2)
    .map(lambda x: x + 3)
)
print(result.unwrap())  # 13
```

### 3. @safe デコレータによる例外のラップ

既存の例外を発生させる可能性のある関数を、低コストで Result 駆動型へ移行させます。

引数なしの `@safe`（および `@safe()`）は、互換性のため、意図的にすべての
`Exception` を `Err` へ変換する catch-all です。そのため、予期しないプログラミング
エラーまで `Err` になり得ます。既存の bare `@safe` の動作は変更していません。
実運用では、捕捉したい対象を `@safe(ValueError, TypeError)` のように明示してください。
明示した型に一致しない例外はそのまま伝播します。

`asyncio.CancelledError` などの制御フロー用例外は `Exception` のサブクラスではないため、
bare `@safe` でも捕捉されず、キャンセルなどの制御フローを隠しません。

既存の catch-all を維持したい場合は移行不要です。捕捉範囲を狭める場合は、対象の例外を
監査したうえで `@safe` を `@safe(ValueError, ...)` に置き換えてください。

```python
from flow_res import safe

@safe
def parse_int(s: str) -> int:
    return int(s)

# 例外は送出されず、Err として返却される
result = parse_int("not_a_number")
print(result)  # Err(error=ValueError("invalid literal for int() with base 10: 'not_a_number'"))
```

### 4. 非同期処理の統合 (@async_result)

`@async_result` デコレータを使用することで、非同期関数の実行結果に対しても await 前にメソッドチェーンを適用できます。
`AwaitableResult` は内部のコルーチンを一つだけ保持する単一消費型です。同じインスタンスを複数回 await したり、複数のチェーンへ分岐させたりせず、一つのチェーンで消費してください。複数の独立したチェーンが必要なときは、デコレート済みの関数をチェーンごとに呼び出して別インスタンスを作成します。
2回目のawait、または分岐したチェーンのうち後から消費するチェーンでは、`RuntimeError("AwaitableResult can only be consumed once")` が送出されます。
また、生成した `AwaitableResult` を await せずに破棄すると、Python が未消費コルーチンの `RuntimeWarning` を報告する場合があります。呼び出した非同期処理は、必ず一つのチェーンの終端で await してください。

```python
import asyncio
from flow_res import Err, Ok, Result, async_result

@async_result
async def fetch_user(user_id: int) -> Result[dict, ValueError]:
    await asyncio.sleep(0.1)
    if user_id < 0:
        return Err(ValueError("Invalid user ID"))
    return Ok({"id": user_id, "name": f"User{user_id}"})

async def main():
    # 処理を連結した後に一括で await
    result = await (
        fetch_user(1)
        .map(lambda u: u["name"])
        .map(str.upper)
    )
    print(result.unwrap())  # USER1

asyncio.run(main())
```

### 5. 複数結果の集約ロジック (combine / combine_lazy / combine_async / combine_all)

バリデーションなど、複数の検証結果を一括で扱うためのインターフェースを提供します。

* `combine`: 既に計算済みの `Result` のシーケンスを集約し、走査中に最初に遭遇した `Err` を返却する。tuple/list の入力式は `combine` 呼び出し前に評価済みなので、`Err` 以降の入力評価は止められない
* `combine_lazy`: `Result` を返す遅延 factory を順番に呼び、最初の `Err` で後続 factory を呼ばずに停止する
* `combine_async`: `Result` または `Awaitable[Result]` を返す遅延 factory を順番に呼び、必要なものだけ await して最初の `Err` で停止する（タスクを並列実行しない）
* `combine_all`: すべての `Err` を集約して複数の例外を保持する `Err` を返却する（全件チェック）

`combine` と `combine_all` は、1〜10 要素の異種 tuple では各要素の型を保持します。11 要素以上の tuple と一般の `Sequence` も受け付けますが、その場合の成功値は `tuple[Any, ...]` にフォールバックします。

```python
from flow_res import Result, combine, combine_all, combine_async, combine_lazy, Ok, Err

results = (
    Ok(1),
    Err(ValueError("error1")),
    Err(RuntimeError("error2")),
)

# 最初のエラー (error1) のみを返す
print(combine(results)) 

# 計算そのものを遅延させると、Err の後の factory は呼ばれない
print(combine_lazy((lambda: Ok(1), lambda: Err(ValueError("error1")), lambda: Ok(3))))

# すべてのエラーを集約して返す
match combine_all(results):
    case Err(error):
        for e in error.exceptions:
            print(f"Error: {e}")
```

`combine_async` は、同期 factory と非同期 factory を同じ iterable に混在させられます。各 factory は直列に実行され、非同期の戻り値だけが await されます。

```python
import asyncio

from flow_res import Ok, combine_async

async def fetch_value() -> Ok[int]:
    return Ok(2)

async def main() -> None:
    result = await combine_async((lambda: Ok(1), fetch_value))
    print(result)  # Ok((1, 2))

asyncio.run(main())
```

## 動作環境

* **Python バージョン**: 3.12 以上（3.11 以下は対象外）
* **型ヒント**: 完全対応（Static Type Checking を推奨）

## ライセンス

本プロジェクトは MIT License の下に公開されています。

## 協力・貢献

不具合報告や機能拡張の提案は、[GitHub Issues](https://github.com/shimae-net/flow-res/issues) にて承っております。
開発環境の構築、品質チェック、互換性方針、リリース手順については [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。
