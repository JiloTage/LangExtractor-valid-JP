# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a modern Python project template with the following stack:
- **Python 3.12+** target version
- **uv** for fast package management
- **pytest** for testing
- **Ruff** for linting/formatting (100 char line length)
- **Pre-commit hooks** for code quality
- **Docker** and **Devcontainer** support

## Essential Commands

### Package Management (MUST use uv, NEVER pip)
```bash
uv sync                    # Install all dependencies
uv add package-name        # Add new package
uv add --dev package-name  # Add dev dependency
```

### Code Quality & Testing
```bash
uv run ruff format .       # Format code
uv run ruff check . --fix  # Lint with auto-fix
uv run pytest             # Run all tests
uv run pytest tests/test_hello.py::test_hello  # Run specific test
```

### Development Workflow
```bash
uv run pre-commit install  # Setup git hooks (one-time)
./docker/build.sh         # Build Docker image
./docker/run.sh           # Run in Docker
```

## Project Structure

```
src/my_package/    # Main package code
tests/            # Test files
docker/           # Docker configs
pyproject.toml    # Project config & dependencies
```

## Critical Development Rules

From `.cursor/rules/coding_style.mdc`:
1. **Package Management**: ONLY use `uv add`, NEVER `pip install` or `@latest`
2. **Type Hints**: Required for ALL functions
3. **Docstrings**: Use Google style
4. **Git Commits**: Follow Conventional Commits (feat:, fix:, docs:)
5. **Testing**: New features need tests, bug fixes need regression tests

## SuperClaude Framework

This project includes the SuperClaude framework for enhanced AI assistance:

@.superclaude/COMMANDS.md
@.superclaude/FLAGS.md
@.superclaude/PRINCIPLES.md
@.superclaude/RULES.md
@.superclaude/MCP.md
@.superclaude/PERSONAS.md
@.superclaude/ORCHESTRATOR.md
@.superclaude/MODES.md

### Quick SuperClaude Usage

**MCP Setup** (Serena for intelligent code navigation):
```bash
claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context ide-assistant --project $(pwd)
```

**Common Workflows**:
- `/analyze` - Analyze codebase with auto-persona activation
- `/implement feature` - Build features with appropriate tools
- `/improve --wave-mode` - Systematic improvements
- `--uc` flag for compressed output
- `--think` for complex analysis
- `--persona-[type]` for specialized behavior

The framework auto-activates personas and tools based on context, handles complex operations through wave orchestration, and provides intelligent routing for optimal results.
