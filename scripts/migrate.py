#!/usr/bin/env python3
"""Migration script to help transition from old to new project structure."""

import os
import shutil
from pathlib import Path

def create_migration_guide():
    """Create a migration guide for users."""
    guide = """
# Migration Guide

## Old vs New Structure

### Old Structure:
- `app.py` (main FastAPI app)
- `core/` (business logic)
- `agents/` (AI agents)
- `config/setting.py` (configuration)
- `prompts/` (prompt templates)
- `param/` (parameter models)

### New Structure:
- `src/api/main.py` (main FastAPI app)
- `src/core/` (business logic with better organization)
- `src/agents/` (AI agents with proper packaging)
- `src/core/config.py` (Pydantic settings)
- `src/prompts/` (prompt templates)
- `src/param/` (parameter models)
- `src/utils/` (utilities like logging)
- `src/cli.py` (command-line interface)

## Running the Application

### Before:
```bash
python app.py
# or
uvicorn app:app
```

### After:
```bash
# Recommended
uvicorn src.api.main:app --reload

# Or
python -m src.api.main

# CLI interface
python -m src.cli
```

## Configuration Changes

### Before:
```python
from config.setting import LLM_MODEL, TEMPERATURE
```

### After:
```python
from src.core.config import settings
# Use settings.LLM_MODEL, settings.TEMPERATURE
```

## Import Changes

### Before:
```python
from core.graph import TravelAssistantGraph
from agents.retrieval.retrieval_agent import RetrievalAgent
```

### After:
```python
from src.core.graph import TravelAssistantGraph
from src.agents.retrieval import RetrievalAgent
```

## Environment Variables

The application now uses Pydantic Settings. Create a `.env` file:

```
OPENAI_API_KEY=your_key_here
SERPAPI_API_KEY=your_key_here
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

## Backward Compatibility

The old `app.py` still works but shows a deprecation warning.
Consider updating your deployment scripts to use the new entry point.
"""
    
    with open("MIGRATION.md", "w", encoding="utf-8") as f:
        f.write(guide)
    
    print("✅ Migration guide created: MIGRATION.md")

def backup_old_files():
    """Backup old files before migration."""
    backup_dir = Path("backup_old_structure")
    backup_dir.mkdir(exist_ok=True)
    
    old_files = [
        "app.py.old",
        "core/",
        "agents/",
        "config/",
        "prompts/",
        "param/",
        "logger.py"
    ]
    
    for file_path in old_files:
        if Path(file_path).exists():
            if Path(file_path).is_file():
                shutil.copy2(file_path, backup_dir / Path(file_path).name)
            else:
                shutil.copytree(file_path, backup_dir / Path(file_path).name, dirs_exist_ok=True)
    
    print(f"✅ Old files backed up to: {backup_dir}")

def main():
    """Main migration function."""
    print("🔄 Starting migration to new project structure...")
    
    # Create migration guide
    create_migration_guide()
    
    # Check if new structure exists
    if Path("src").exists():
        print("✅ New structure already exists in src/")
    else:
        print("❌ New structure not found. Please ensure src/ directory is created.")
    
    print("\n📋 Migration completed!")
    print("📖 Check MIGRATION.md for detailed migration instructions")
    print("🚀 Start the new application with: uvicorn src.api.main:app --reload")

if __name__ == "__main__":
    main() 