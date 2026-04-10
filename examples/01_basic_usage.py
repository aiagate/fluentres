"""
基本的な使い方のサンプル
OK と Err の作成、map、and_then のチェーニング
"""

from flow_res import Err, Ok, Result


def divide(a: int, b: int) -> Result[float, ValueError]:
    """2つの数値を除算し、結果を返す"""
    if b == 0:
        return Err(ValueError("Division by zero"))
    return Ok(a / b)


def main():
    # 成功ケース
    result = divide(10, 2)
    match result:
        case Ok(value):
            print(f"Success: 10 / 2 = {value}")
        case Err(error):
            print(f"Error: {error}")

    # エラーケース
    result = divide(10, 0)
    match result:
        case Ok(value):
            print(f"Success: {value}")
        case Err(error):
            print(f"Error: {error}")

    # map でチェーニング
    print("\n--- Chaining with map ---")
    result = Ok(5).map(lambda x: x * 2).map(lambda x: x + 3)
    print(f"(5 * 2) + 3 = {result.unwrap()}")

    # and_then でチェーニング
    print("\n--- Chaining with and_then ---")

    def validate_positive(x: int) -> Result[int, ValueError]:
        if x < 0:
            return Err(ValueError("Must be positive"))
        return Ok(x)

    result = Ok(-5).and_then(validate_positive).map(lambda x: x * 2)
    match result:
        case Ok(value):
            print(f"Value: {value}")
        case Err(error):
            print(f"Validation error: {error}")


if __name__ == "__main__":
    main()
