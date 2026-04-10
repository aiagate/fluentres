# flow-res

Rust 言語の `Result` 型に範を仰いだ、Python 向けの高機能かつ型安全なエラーハンドリングライブラリです。

従来の例外駆動型（Exception-driven）から、Result 駆動型（Result-driven）へのパラダイムシフトを強力に支援します。明示的なエラーハンドリングを導入することで、コードの堅牢性と可読性を飛躍的に向上させることが可能です。

## 主要な特徴

* **厳密な型安全性**: ジェネリクスを活用し、成功値とエラー値の双方に対して静的解析（mypy, pyright 等）を適用可能です。
* **鉄道指向プログラミング（ROP）**: `map` や `and_then` によるメソッドチェーンにより、宣言的なエラーハンドリングを実現します。
* **非同期処理のネイティブサポート**: `@async_result` デコレータを通じて、非同期処理を `AwaitableResult` として透過的にチェーン可能です。
* **メタプログラミングによる統合**: `@safe` デコレータを用いることで、既存の例外送出型関数を容易に Result 型へ変換できます。
* **高度な結果集約**: `combine`（早期失敗）および `combine_all`（全エラー集約）により、複数の処理結果を合理的に統合します。
* **軽量設計（ゼロ依存）**: 外部ライブラリへの依存はなく、プロジェクトへの導入障壁が極めて低く抑えられています。

## インストール

```bash
pip install flow_res
```

※ Python 3.13 以上が必要です。

## 実装ガイド

### 1. 基本的な定義とハンドリング

関数の戻り値に `Result` を指定することで、呼び出し側に対してエラー処理の検討を強制（明示）させます。Python 3.10 以降の構造的パターンマッチングを利用することで、エレガントに結果を処理できます。

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
from flow_res import Result

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

```python
import asyncio
from flow_res import Result, async_result

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

### 5. 複数結果の集約ロジック (combine / combine_all)

バリデーションなど、複数の検証結果を一括で扱うためのインターフェースを提供します。

* `combine`: 最初に遭遇した `Err` を返却する（短絡評価・早期失敗）
* `combine_all`: すべての `Err` を集約して複数の例外を保持する `Err` を返却する（全件チェック）

```python
from flow_res import Result, combine, combine_all, Ok, Err

results = (
    Ok(1),
    Err(ValueError("error1")),
    Err(RuntimeError("error2")),
)

# 最初のエラー (error1) のみを返す
print(combine(results)) 

# すべてのエラーを集約して返す
match combine_all(results):
    case Err(error):
        for e in error.exceptions:
            print(f"Error: {e}")
```

## 動作環境

* **Python バージョン**: 3.13 以上
* **型ヒント**: 完全対応（Static Type Checking を推奨）

## ライセンス

本プロジェクトは MIT License の下に公開されています。

## 協力・貢献

不具合報告や機能拡張の提案は、[GitHub Issues](https://github.com/aiagate/flow-res/issues) にて承っております。
