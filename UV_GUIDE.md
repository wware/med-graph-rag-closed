# Using uv for Python Environment Management

## Why uv?

- **10-100x faster** than pip
- Better dependency resolution
- Unified interface for venv + pip
- Written in Rust
- Drop-in replacement for pip

## Installation

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip (if you already have Python)
pip install uv
```

## Quick Start

```bash
# Create venv and install dependencies in one go
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -r requirements.txt
```

## Common Commands

### Environment Management

```bash
# Create virtual environment
uv venv

# Create with specific Python version
uv venv --python 3.12

# Activate (same as regular venv)
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### Installing Packages

```bash
# Install from requirements.txt
uv pip install -r requirements.txt

# Install single package
uv pip install boto3

# Install with extras
uv pip install "fastapi[all]"

# Install in editable mode (for development)
uv pip install -e .

# Install multiple packages
uv pip install boto3 opensearch-py pandas
```

### Managing Dependencies

```bash
# Freeze current environment
uv pip freeze > requirements.txt

# Compile requirements (like pip-compile)
uv pip compile requirements.in -o requirements.txt

# Sync environment to match requirements.txt exactly
uv pip sync requirements.txt
```

### Upgrading Packages

```bash
# Upgrade a specific package
uv pip install --upgrade boto3

# Upgrade all packages (be careful!)
uv pip install --upgrade -r requirements.txt
```

### Uninstalling

```bash
# Uninstall a package
uv pip uninstall boto3

# Uninstall all packages
uv pip freeze | uv pip uninstall -r -
```

## Project Workflow

### Initial Setup

```bash
# Clone repo
git clone https://github.com/your-username/medical-knowledge-graph.git
cd medical-knowledge-graph

# Set up environment
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Adding New Dependencies

```bash
# Install the package
uv pip install scispace

# Update requirements.txt
uv pip freeze > requirements.txt

# Or manually add to requirements.txt and sync
echo "scispace>=1.0.0" >> requirements.txt
uv pip sync requirements.txt
```

### Development Workflow

```bash
# Activate environment
source .venv/bin/activate

# Install dev dependencies
uv pip install -r requirements-dev.txt

# Run code
python -m src.ingestion.pipeline

# When done, deactivate
deactivate
```

## Using uv with Docker

The Dockerfiles don't need to change - they can still use pip or uv:

### Option 1: Keep using pip in Docker (simpler)
```dockerfile
# No changes needed to existing Dockerfiles
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

### Option 2: Use uv in Docker (faster builds)
```dockerfile
# Install uv in Docker
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Install dependencies with uv
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt
```

## Tips & Tricks

### Speed Comparison

```bash
# Traditional pip
time pip install -r requirements.txt
# ~45 seconds

# uv
time uv pip install -r requirements.txt
# ~3 seconds (cached) or ~8 seconds (fresh)
```

### Caching

uv caches packages globally, so reinstalling is super fast:

```bash
# First install
uv pip install boto3  # Downloads and caches

# Delete venv and recreate
rm -rf .venv
uv venv
uv pip install boto3  # Instant (from cache)
```

### Requirements Files

You can use the same requirements.txt format:

```txt
# requirements.txt
boto3>=1.34.0
opensearch-py>=2.4.0
fastapi>=0.109.0

# With extras
uvicorn[standard]>=0.27.0

# From git
git+https://github.com/user/repo.git@branch

# Local editable install
-e .
```

### Working with Multiple Environments

```bash
# Different venvs for different purposes
uv venv .venv-dev --python 3.12
uv venv .venv-test --python 3.11

# Activate the one you need
source .venv-dev/bin/activate
```

## Migration from pip

If you're already using pip:

```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Use uv exactly like pip
# Just replace 'pip' with 'uv pip' in your commands

# Old:
pip install -r requirements.txt

# New:
uv pip install -r requirements.txt

# That's it! Your requirements.txt stays the same.
```

## Common Issues

### "uv: command not found"

```bash
# Add to PATH (Linux/Mac)
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Or for zsh
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Permission Errors

```bash
# On Linux, you might need to make uv executable
chmod +x ~/.cargo/bin/uv
```

### Package Installation Fails

```bash
# Fall back to pip for problematic packages
uv pip install most-packages
pip install problematic-package
```

## Comparison with Other Tools

| Feature | uv | pip | pip-tools | poetry |
|---------|----|----|-----------|--------|
| Speed | ⚡⚡⚡ | 🐌 | 🐌 | 🏃 |
| Drop-in for pip | ✅ | N/A | ❌ | ❌ |
| Lock files | ✅ | ❌ | ✅ | ✅ |
| Project management | ❌ | ❌ | ❌ | ✅ |
| Learning curve | Easy | Easy | Medium | Steep |

## For This Project

**Recommended approach:**

1. Use `uv` for local development (fast!)
2. Keep `requirements.txt` format (compatible with pip)
3. Dockerfiles can use either pip or uv
4. CDK stack uses pip (simpler for deployment)

This gives you speed locally while keeping compatibility everywhere else.

## Resources

- [uv Documentation](https://github.com/astral-sh/uv)
- [uv vs pip Benchmark](https://github.com/astral-sh/uv#benchmarks)
- [Migration Guide](https://github.com/astral-sh/uv/blob/main/MIGRATION.md)
