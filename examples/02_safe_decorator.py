"""
@safe デコレータの使用例
例外を自動的に Result に変換
"""

from flow_res import safe


@safe
def parse_int(s: str) -> int:
    """文字列を整数に変換（例外を Result に変換）"""
    return int(s)


@safe
def get_dict_value(d: dict, key: str):
    """辞書のキーを取得（KeyError を Result に変換）"""
    return d[key]


@safe
def divide(a: float, b: float) -> float:
    """除算（ZeroDivisionError を Result に変換）"""
    return a / b


def main():
    # parse_int の使用
    print("--- Parse Integer ---")
    result = parse_int("42")
    print(f"parse_int('42'): {result}")

    result = parse_int("not_a_number")
    print(f"parse_int('not_a_number'): {result}")

    # get_dict_value の使用
    print("\n--- Get Dict Value ---")
    data = {"name": "Alice", "age": 30}
    result = get_dict_value(data, "name")
    print(f"get_dict_value(data, 'name'): {result}")

    result = get_dict_value(data, "email")
    print(f"get_dict_value(data, 'email'): {result}")

    # divide の使用
    print("\n--- Division ---")
    result = divide(10, 2)
    print(f"divide(10, 2): {result}")

    result = divide(10, 0)
    print(f"divide(10, 0): {result}")


if __name__ == "__main__":
    main()
