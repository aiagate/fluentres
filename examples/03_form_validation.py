"""
form_validation.py: フォームバリデーション例
複数のバリデーション結果を集約して表示
"""

from flow_res import Err, Ok, combine_all, safe


@safe
def validate_email(email: str) -> str:
    """メールアドレスをバリデーション"""
    if not email:
        raise ValueError("Email cannot be empty")
    if "@" not in email:
        raise ValueError("Invalid email format")
    if "." not in email.split("@")[1]:
        raise ValueError("Invalid domain")
    return email


@safe
def validate_age(age: int) -> int:
    """年齢をバリデーション"""
    if age < 0:
        raise ValueError("Age cannot be negative")
    if age < 18:
        raise ValueError("Must be 18 or older")
    if age > 150:
        raise ValueError("Age seems invalid")
    return age


@safe
def validate_username(username: str) -> str:
    """ユーザー名をバリデーション"""
    if not username:
        raise ValueError("Username cannot be empty")
    if len(username) < 3:
        raise ValueError("Username must be at least 3 characters")
    if len(username) > 20:
        raise ValueError("Username must be at most 20 characters")
    if not username.replace("_", "").isalnum():
        raise ValueError("Username can only contain letters, numbers, and underscores")
    return username


def validate_user_form(email: str, age: int, username: str):
    """複数のフォームフィールドをバリデーション"""
    validation_results = combine_all(
        (
            validate_email(email),
            validate_age(age),
            validate_username(username),
        )
    )

    match validation_results:
        case Ok((valid_email, valid_age, valid_username)):
            print("Success: All validations passed!")
            print(f"  Email: {valid_email}")
            print(f"  Age: {valid_age}")
            print(f"  Username: {valid_username}")
            return True
        case Err(errors):
            print("Validation failed:")
            for error in errors.exceptions:
                print(f"  - {error}")
            return False


def main():
    print("--- Test Case 1: Valid Input ---")
    validate_user_form("user@example.com", 25, "alice_123")

    print("\n--- Test Case 2: Invalid Email ---")
    validate_user_form("invalid-email", 25, "alice_123")

    print("\n--- Test Case 3: Too Young ---")
    validate_user_form("user@example.com", 15, "alice_123")

    print("\n--- Test Case 4: Short Username ---")
    validate_user_form("user@example.com", 25, "al")

    print("\n--- Test Case 5: Multiple Errors ---")
    validate_user_form("invalid", 10, "a")


if __name__ == "__main__":
    main()
