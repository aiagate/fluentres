# flow-res への貢献

不具合報告や機能提案は [GitHub Issues](https://github.com/aiagate/flow-res/issues) へお寄せください。コードやドキュメントを変更する場合は、以下の手順でローカル検証を行ってからプルリクエストを作成してください。

## 開発環境

Python 3.12 以上と [uv](https://docs.astral.sh/uv/) が必要です（Python 3.11 以下は対象外です）。リポジトリを clone したディレクトリで、ロックファイルに従って開発用依存関係をインストールします。

```bash
uv sync --frozen
```

依存関係を意図的に更新する場合だけ `uv sync` を実行し、変更された `uv.lock` を同じプルリクエストに含めてください。

## 品質チェック

CI と同じ主要チェックは次のコマンドで実行できます。

```bash
uv run --frozen ruff format --check .
uv run --frozen ruff check .
uv run --frozen pyright
uv run --frozen pytest --cov --cov-report=term-missing
uv build
```

pytest はカバレッジ 95% を最低基準としています。README 内の Python コード例もテストで個別に実行されるため、例を追加・変更するときは自己完結した実行可能なコードにしてください。

配布物を変更した場合は、build 後に wheel を空の仮想環境へインストールし、import できることも確認します。

```bash
python -m venv .wheel-venv
.wheel-venv/bin/python -m pip install dist/*.whl
.wheel-venv/bin/python -c "import flow_res"
```

## `AwaitableResult` を変更するときの注意

`AwaitableResult` は、内部のコルーチンを一つだけ保持する単一消費型です。

- 同じインスタンスを複数回 await しないでください。
- 同じインスタンスから複数のチェーンへ分岐させないでください。
- 生成したインスタンスは、一つのチェーンの終端で必ず await してください。

await されないインスタンスを破棄すると、Python が未消費コルーチンの `RuntimeWarning` を報告する場合があります。この制約を変える実装は API の動作変更に当たるため、互換性への影響とテストをプルリクエストに明記してください。

## 互換性と破壊的変更

公開 API は `flow_res` パッケージから import できる名前、その型シグネチャ、および文書化された動作です。変更時は次の方針に従います。

- バグ修正と後方互換な機能追加では、既存の公開 API と型チェック結果を維持します。
- 公開名の削除・改名、引数や戻り値の非互換変更、例外や評価タイミングなど文書化された動作の変更は、破壊的変更として扱います。
- 破壊的変更には、変更理由、移行方法、影響を受ける API をプルリクエストとリリースノートへ記載します。可能な場合は、削除前に非推奨期間を設けます。
- Python の最低対応バージョン引き上げも破壊的変更として扱います。

リリース番号は PEP 440 に準拠します。安定版では、破壊的変更をメジャーバージョンで示します。`1.0.0` 未満ではマイナーバージョンで破壊的変更が入る可能性があるため、リリースノートを確認してください。

## リリース運用

パッケージのバージョンは Git tag から `hatch-vcs` が決定します。公開対象の tag は `v` で始まる PEP 440 バージョンで、ローカルバージョン識別子（例: `+local`）は使用できません。

| tag の例 | 種別 | 公開先 |
| --- | --- | --- |
| `v1.2.3rc1`, `v1.2.3b1`, `v1.2.3.dev1` | プレリリース | TestPyPI |
| `v1.2.3`, `v1.2.3.post1` | 安定版 | PyPI |

`v*` tag の push により TestPyPI 用と PyPI 用の workflow が起動し、tag の分類に一致する側だけがテスト、build、公開を実行します。公開前に ruff、pyright、pytest、配布物のバージョン一致、および wheel のインストールが検証されます。

手動実行する場合は、GitHub Actions の `publish-test` または `publish-prod` workflow に既存の tag 名を指定します。TestPyPI にはプレリリース、PyPI には安定版だけを指定してください。公開済みバージョンは再利用せず、新しい PEP 440 バージョンを作成します。

リリース担当者は tag 作成前に、対象 commit が `main` に取り込まれ、CI が成功し、リリースノートに互換性上の注意事項が記載されていることを確認してください。
