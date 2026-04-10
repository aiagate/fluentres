"""
railroad_oriented.py: Railroad-Oriented Programming パターン
複数のステップをパイプラインとしてチェーン
"""

from flow_res import Err, Ok, Result, safe


@safe
def parse_int(s: str) -> int:
    """文字列を整数に解析"""
    return int(s)


def validate_range(x: int) -> Result[int, ValueError]:
    """値が10～100の範囲内か確認"""
    if x < 10 or x > 100:
        return Err(ValueError(f"Value must be between 10 and 100, got {x}"))
    return Ok(x)


def apply_tax(price: int) -> Result[float, ValueError]:
    """税金を適用（10%）"""
    if price < 0:
        return Err(ValueError("Price cannot be negative"))
    return Ok(price * 1.1)


def apply_discount(price: float) -> Result[float, ValueError]:
    """割引を適用（15%）"""
    if price < 0:
        return Err(ValueError("Price cannot be negative"))
    return Ok(price * 0.85)


def process_price(price_str: str) -> Result[str, Exception]:
    """
    Railroad-Oriented Programming のパターン：
    正常系と異常系が"線路"のように分かれる
    """
    return (
        parse_int(price_str)  # 文字列を解析
        .and_then(validate_range)  # 範囲チェック
        .and_then(apply_tax)  # 税金適用
        .and_then(apply_discount)  # 割引適用
        .map(lambda x: f"${x:.2f}")  # フォーマット
        .map_err(lambda e: Exception(f"Processing error: {e}"))  # エラーメッセージ変換
    )


def main():
    test_cases = ["50", "5", "150", "100", "invalid"]

    print("--- Price Processing Pipeline ---\n")
    for price_input in test_cases:
        result = process_price(price_input)
        match result:
            case Ok(price):
                print(f"Success: '{price_input}' → {price}")
            case Err(error):
                print(f"Error: '{price_input}' → {error}")


if __name__ == "__main__":
    main()
