# FDE Handover Runbook Generator（運用引き継ぎ手順書のMarkdown整形）

[![tests](https://github.com/takashi-101/fde-handover-runbook-gen/actions/workflows/tests.yml/badge.svg)](https://github.com/takashi-101/fde-handover-runbook-gen/actions/workflows/tests.yml)

システム名、主管ロール、日次確認コマンド、エスカレーション先（異常時の連絡先）、切り戻し手順（変更を元に戻す手順）の5項目を受け取り、決まった見出し構成の運用引き継ぎ手順書を、Markdown（見出しや箇条書きを記号で書く文書の形式）の文字列で返すPythonの関数です。標準ライブラリだけで動きます。

## 30秒で読む要点
- **入力は5項目、出力は固定の書式**：`HandoverSpec` に5項目を入れて `generate_runbook_markdown` に渡すと、表題、主管ロールとエスカレーション先の箇条書き、「1. 日次確認コマンド」「2. 異常発生時の切り戻し手順」の2つの節からなるMarkdownを返します。見出しの文言と順序は固定です。
- **文字列を並べるだけです**：コマンドの実行や存在の確認、手順の妥当性の確認はしません。ファイルへの保存もせず、文字列を返すだけです。
- **入力の検査はしません**：空の文字列や空のリストもそのまま出力します。Markdownの記号（`` ` ``、`*`、`#` など）のエスケープ（記号を文字として表示させる処理）もしません。

## 実行
```
python examples/run_example.py
```
`examples/sample_spec.json`（架空のシステムの5項目）から `HandoverSpec` を作り、`generate_runbook_markdown` の戻り値を表示します。出力：
```
# 運用引き継ぎ手順書：架空の窓口予約システム

- **主管ロール**：架空課 運用担当
- **異常時エスカレーション先**：架空の情報システム担当窓口（内線0000）

## 1. 日次確認コマンド
- `python scripts/check_queue.py --date today`
- `python scripts/export_daily_report.py`

## 2. 異常発生時の切り戻し手順
1. 予約受付画面に一時停止のお知らせを表示する
2. 前日のバックアップから予約データを戻す
3. 電話受付に切り替えたことを利用者に案内する
```
見本のコマンド（`scripts/check_queue.py` など）は架空のもので、このリポジトリにはありません。

テスト：
```
python -m unittest discover -s tests -v
```

## 出力の書式
| 入力の項目 | 出力での位置 |
|---|---|
| `system_name` | 表題 `# 運用引き継ぎ手順書：<system_name>` |
| `owner_role` | `- **主管ロール**：<owner_role>` |
| `escalation_contact` | `- **異常時エスカレーション先**：<escalation_contact>` |
| `daily_commands`（文字列のリスト） | 「## 1. 日次確認コマンド」の下に、1件ずつ `` - `<コマンド>` `` |
| `rollback_steps`（文字列のリスト） | 「## 2. 異常発生時の切り戻し手順」の下に、1から番号を振って `1. <手順>` |

- リストの順序はそのまま保ちます。リストが空の場合、その節は見出しだけになります。
- 項目の中の改行もそのまま入るため、手順に改行を入れると番号付きの箇条書きが崩れます。
- コマンドに `` ` `` を含めると、インラインコード（文中のコード表記）が崩れます。

## 公開している関数
| 名前 | 内容 |
|---|---|
| `runbook_gen.HandoverSpec(system_name, owner_role, daily_commands, escalation_contact, rollback_steps)` | 入力のデータクラス（値をまとめて持つクラス。`frozen` 指定で変更できません）。5項目すべて必須で、足りない場合や、それ以外の項目を渡した場合は `TypeError` です。 |
| `runbook_gen.generate_runbook_markdown(spec)` | Markdownの文字列を返します。`daily_commands` や `rollback_steps` が `None` の場合は `TypeError`、`HandoverSpec` の代わりに辞書を渡した場合は `AttributeError` です。 |

パッケージは `src/` にあり、インストール用の設定（`pyproject.toml`）はありません。テストと `examples/run_example.py` は、先頭で `src` をimportパスに加えています。

## テスト（17件）
- 正常系：出力全体の一致、コマンドの順序、手順の番号、末尾の改行
- 境界値：空のリスト、空の文字列、Markdownの記号をエスケープしないこと、手順の中の改行、タプルの入力、入力が変更できないこと
- 異常系：項目の不足と未定義の項目、`None` のリスト、`HandoverSpec` 以外の入力
- READMEの「実行」に載せた出力が、`examples/run_example.py` の実際の出力と一致すること

CI（GitHub Actionsによる自動テスト）は、push と pull request のたびに、Python 3.11 と 3.12 でテストとサンプルの実行を行う設定です（`.github/workflows/tests.yml`）。

## 制約
- 見出しの文言と節の構成は固定で、変える設定はありません。
- 型の検査はしません。`daily_commands` と `rollback_steps` には文字列のリスト（またはタプル）を渡す前提です。

## ファイル構成
```
src/runbook_gen/
  generator.py               HandoverSpec と Markdown の組み立て
  __init__.py                HandoverSpec と generate_runbook_markdown を公開
examples/
  sample_spec.json           見本データ（架空）
  run_example.py             見本データから手順書を表示
tests/                       ユニットテスト
.github/workflows/tests.yml  CI
```

## ライセンス
MIT（[LICENSE](LICENSE)）
