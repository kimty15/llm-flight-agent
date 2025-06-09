#!/usr/bin/env python3
"""Setup script for the Nha Trang Tourism Assistant."""

import os
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 12):
        print("❌ Python 3.12+ is required")
        return False
    print("✅ Python version is compatible")
    return True

def check_environment_file():
    """Check if .env file exists and has required variables."""
    env_file = Path(".env")
    required_vars = ["OPENAI_API_KEY"]
    optional_vars = ["SERPAPI_API_KEY", "DEBUG", "HOST", "PORT"]
    
    if not env_file.exists():
        print("⚠️  .env file not found. Creating template...")
        template = """# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
SERPAPI_API_KEY=your_serpapi_key_here
DEBUG=false
HOST=0.0.0.0
PORT=8000
"""
        with open(".env", "w") as f:
            f.write(template)
        print("✅ .env template created. Please fill in your API keys.")
        return False
    
    # Read existing .env
    with open(".env", "r") as f:
        content = f.read()
    
    missing_vars = []
    for var in required_vars:
        if f"{var}=" not in content or f"{var}=your_" in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing or incomplete environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment variables configured")
    return True

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        "fastapi",
        "uvicorn",
        "langchain",
        "langgraph",
        "openai",
        "faiss-cpu",
        "pydantic",
        "python-dotenv"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_faiss_index():
    """Check if FAISS index exists."""
    index_path = Path("faiss_index_openai_embeddings")
    if not index_path.exists():
        print("⚠️  FAISS index not found. You'll need to generate it from your PDF documents.")
        return False
    
    print("✅ FAISS index found")
    return True

def check_data_files():
    """Check if data files exist."""
    data_dir = Path("data")
    if not data_dir.exists():
        print("⚠️  Data directory not found")
        return False
    
    pdf_files = list(data_dir.glob("*.pdf"))
    if not pdf_files:
        print("⚠️  No PDF files found in data directory")
        return False
    
    print(f"✅ Found {len(pdf_files)} PDF files in data directory")
    return True

def main():
    """Main setup function."""
    print("🔧 Setting up Nha Trang Tourism Assistant...")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", check_environment_file),
        ("Data Files", check_data_files),
        ("FAISS Index", check_faiss_index),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 50)
    print("📊 Setup Summary:")
    
    all_passed = True
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 Setup complete! You can now run the application:")
        print("   uvicorn src.api.main:app --reload")
        print("   python -m src.cli")
    else:
        print("\n⚠️  Some issues need to be resolved before running the application.")
        print("Please address the issues above and run setup again.")

if __name__ == "__main__":
    main() 