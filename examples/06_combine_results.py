"""
combine_results.py: 複数の Result を統合
combine と combine_all の使い方
"""

from flow_res import Err, Ok, Result, combine, combine_all


def example_combine():
    """
    combine: 最初のエラーで失敗
    すべてが成功した場合のみ Ok を返す
    """
    print("--- combine: All Success ---")
    results = (Ok(1), Ok(2), Ok(3))
    combined = combine(results)
    print(f"combine({results})")
    print(f"Result: {combined}\n")

    print("--- combine: First Error Stops ---")
    results = (
        Ok(1),
        Err(ValueError("error1")),
        Ok(3),
        Err(ValueError("error2")),
    )
    combined = combine(results)
    print(f"combine({results})")
    print(f"Result: {combined}")
    print("Note: Only first error is returned\n")


def example_combine_all():
    """
    combine_all: すべてのエラーを集約
    すべてのエラーを収集して返す
    """
    print("--- combine_all: All Success ---")
    results = (Ok(1), Ok(2), Ok(3))
    combined = combine_all(results)
    print(f"combine_all({results})")
    print(f"Result: {combined}\n")

    print("--- combine_all: Collect All Errors ---")
    results = (
        Ok(1),
        Err(ValueError("error1")),
        Ok(3),
        Err(ValueError("error2")),
        Err(ValueError("error3")),
    )
    combined = combine_all(results)
    print(f"combine_all({results})")
    match combined:
        case Ok(values):
            print(f"Result: Ok{values}")
        case Err(error):
            print(f"Result: Err with {len(error.exceptions)} errors")
            for error in error.exceptions:
                print(f"  - {error}")


def validate_credentials(username: str, password: str, email: str):
    """バリデーション例：すべてのエラーを一度に表示"""

    def validate_username(u: str) -> Result[str, ValueError]:
        if len(u) < 3:
            return Err(ValueError("Username too short"))
        return Ok(u)

    def validate_password(p: str) -> Result[str, ValueError]:
        if len(p) < 8:
            return Err(ValueError("Password too short"))
        return Ok(p)

    def validate_email(e: str) -> Result[str, ValueError]:
        if "@" not in e:
            return Err(ValueError("Invalid email"))
        return Ok(e)

    results = combine_all(
        (
            validate_username(username),
            validate_password(password),
            validate_email(email),
        )
    )

    match results:
        case Ok((u, p, e)):
            print(f"All credentials valid: {u}, {p}, {e}")
        case Err(errors):
            print("Validation failed:")
            for error in errors.exceptions:
                print(f"  - {error}")


def main():
    example_combine()
    example_combine_all()

    print("\n--- Use Case: Multiple Validations ---")
    print("Valid:")
    validate_credentials("alice", "password123", "alice@example.com")

    print("\nInvalid:")
    validate_credentials("ab", "pass", "invalid-email")


if __name__ == "__main__":
    main()
