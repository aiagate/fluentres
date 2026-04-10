"""
async_example.py: 非同期操作のサンプル
AwaitableResult を使用したメソッドチェーニング
"""

import asyncio

from flow_res import Err, Ok, Result, async_result


@async_result
async def fetch_user(user_id: int) -> Result[dict, Exception]:
    """ユーザー情報を取得（シミュレーション）"""
    await asyncio.sleep(0.1)
    if user_id < 0:
        return Err(ValueError("Invalid user ID"))
    return Ok(
        {"id": user_id, "name": f"User{user_id}", "email": f"user{user_id}@example.com"}
    )


@async_result
async def fetch_posts(user_id: int) -> Result[list[dict], Exception]:
    """ユーザーの投稿を取得（シミュレーション）"""
    await asyncio.sleep(0.1)
    if user_id == 0:
        return Err(ValueError("User not found"))
    return Ok(
        [
            {"id": 1, "title": "Post 1", "user_id": user_id},
            {"id": 2, "title": "Post 2", "user_id": user_id},
        ]
    )


async def main():
    print("--- Async Example 1: Get User Name ---")
    result = await fetch_user(1).map(lambda u: u["name"]).map(str.upper)
    print(f"Result: {result}")

    print("\n--- Async Example 2: Combine User and Posts ---")
    user_result = await (
        fetch_user(2)
        .and_then(lambda u: fetch_posts(u["id"]).map(lambda posts: (u, posts)))
        .map(lambda data: f"{data[0]['name']} has {len(data[1])} posts")
    )
    print(f"Result: {user_result}")

    print("\n--- Async Example 3: Error Handling ---")
    result = await (
        fetch_user(-1)
        .and_then(lambda u: fetch_posts(u["id"]))
        .map(lambda posts: f"Got {len(posts)} posts")
    )
    print(f"Result: {result}")

    print("\n--- Async Example 4: Transform User Data ---")
    result = await fetch_user(3).map(
        lambda u: {"id": u["id"], "display_name": f"{u['name']} ({u['email']})"}
    )
    match result:
        case Ok(user):
            print(f"Transformed user: {user}")
        case Err(error):
            print(f"Error: {error}")


if __name__ == "__main__":
    asyncio.run(main())
