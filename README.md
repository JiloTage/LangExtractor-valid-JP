# Python-Project-Template

[![CI](https://github.com/mjun0812/python-project-template/actions/workflows/ci.yml/badge.svg)](https://github.com/mjun0812/python-project-template/actions/workflows/ci.yml)

A simple modern Python project template.

This repository is created by [mjun0812/python-copier-template](https://github.com/mjun0812/python-copier-template) using [copier](https://copier.readthedocs.io/).

[Article](https://mjunya.com/en/posts/2025-06-15-python-template/) [日本語記事](https://zenn.dev/mjun0812/articles/0ae2325d40ed20)

## Features

- 🚀 **Modern Python**: Support for Python 3.10-3.13
- 📦 **uv Package Manager**: Fast and reliable package management with [uv](https://github.com/astral-sh/uv)
- 🐳 **Docker Support**: Complete Docker development environment
- 📦 **Devcontainer Support**: VS Code devcontainer for consistent development
- ✨ **AI Editor Support**: [Cursor rules](https://docs.cursor.com/context/rules) and
  [CLAUDE.md](https://docs.anthropic.com/en/docs/claude-code/overview) included for AI-powered development
- 📝 **Type Hints**: Full type annotation support with modern Python features
- 🔍 **Code Quality**: Pre-configured Ruff for linting and formatting
- 🧪 **Testing**: pytest setup with example tests
- 🔧 **Pre-commit Hooks**: Automated code quality checks
- 🏗️ **CI Ready**: GitHub Actions workflows included

## Quick Start

### Pre-Requirements

- [uv](https://docs.astral.sh/uv/): Fast Python package installer


### SuperClaudeとSerenaの使い方

#### Serena MCPサーバーのセットアップ

Serenaは、Claude Codeでインテリジェントなコード編集と検索を可能にするMCPサーバーです。

```bash
# Serena MCPサーバーを追加
claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context ide-assistant --project $(pwd)
```

#### SuperClaudeフレームワークについて

SuperClaudeは、Claude Codeの能力を拡張する包括的なフレームワークです。このプロジェクトには、`.superclaude/`ディレクトリに以下のコンポーネントが含まれています：

- **COMMANDS.md**: `/analyze`, `/build`, `/implement`などのスラッシュコマンド
- **FLAGS.md**: `--think`, `--uc`, `--persona-architect`などの動作調整フラグ
- **PERSONAS.md**: 特定タスクに特化した11種類のAIペルソナ
- **MCP.md**: Serenaを含むMCPサーバー統合
- **ORCHESTRATOR.md**: インテリジェントなタスク振り分けシステム
- **MODES.md**: タスク管理、内省、トークン効率化の動作モード

#### 基本的な使い方

**1. コード分析**
```bash
# アーキテクチャ分析（アーキテクトペルソナが自動起動）
/analyze --think

# セキュリティ監査（セキュリティペルソナ使用）
/analyze --focus security --ultrathink
```

**2. 機能実装**
```bash
# UIコンポーネントの実装（フロントエンドペルソナとMagic MCPが自動起動）
/implement "ユーザー認証フォーム" --type component

# APIエンドポイントの実装
/implement "REST API for user management" --type api
```

**3. コード改善**
```bash
# 体系的なコード改善（Wave orchestrationが自動起動）
/improve --wave-mode

# パフォーマンス最適化
/improve --focus performance --persona-performance
```

**4. 効率的な出力**
```bash
# 圧縮出力モード（トークン使用量を30-50%削減）
/analyze --uc

# 詳細な思考プロセスを表示
/analyze --introspect
```

#### 高度な機能

**Wave Orchestration**: 複雑度が0.7以上の大規模タスクで自動的に起動し、複数段階での実行を管理します。

**自動ペルソナ選択**: タスクの内容に基づいて最適なペルソナが自動的に選択されます：
- フロントエンド作業 → frontend ペルソナ
- API開発 → backend ペルソナ
- デバッグ → analyzer ペルソナ
- リファクタリング → refactorer ペルソナ

**MCP統合**: 
- Serena: コードナビゲーションと編集
- Sequential: 複雑な分析とマルチステップ推論
- Context7: 公式ドキュメントとベストプラクティス
- Magic: UIコンポーネント生成


### Development Setup

```bash
# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest

# Run formatting and linting (automatically runs on commit)
uv run ruff format .
uv run ruff check .
# Auto Fix
uv run ruff check . --fix
```

### Docker Development Setup

The template includes a complete Docker setup:

```bash
# create uv.lock file
uv sync

# use the provided scripts
./docker/build.sh
./docker/run.sh # or./docker/run.sh (Command)

# Build and run with Docker Compose
docker compose build
docker compose up
```

### VS Code Devcontainer

Open the project in VS Code and use the "Reopen in Container" command for a fully configured development environment.

### Update Template

Thit template is created by [mjun0812/python-copier-template](https://github.com/mjun0812/python-copier-template).
You can apply update from it.

```bash
cd your-project-name
uvx copier update -A
```

## Project Structure

```text
your-project/
├── src/
│   └── your_project/          # Main package
├── tests/                     # Test files
├── docker/                    # Docker configuration
├── compose.yml               # Docker Compose setup
├── pyproject.toml            # Project configuration
└── README.md                 # Project documentation
```

## Q&A

### Why don't you use a type checker?

I'm waiting for stable release of [`ty`](https://github.com/astral-sh/ty).
You can install and use your preferred type checker.

## Support

- 📖 [Copier Documentation](https://copier.readthedocs.io/)
- 🐍 [uv Documentation](https://docs.astral.sh/uv/)
- 🔍 [Ruff Documentation](https://docs.astral.sh/ruff/)
