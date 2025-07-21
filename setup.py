#!/usr/bin/env python3
"""
Setup Script for Aegis Agent
Automates the initial setup process.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def create_env_file():
    """Create .env file from example if it doesn't exist."""
    env_path = Path(".env")
    example_path = Path("env.example")
    
    if not env_path.exists() and example_path.exists():
        print("📝 Creating .env file from env.example...")
        try:
            with open(example_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ .env file created successfully!")
            print("⚠️  Please edit .env file and add your DeepSeek API key")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    elif env_path.exists():
        print("✅ .env file already exists")
        return True
    else:
        print("❌ env.example file not found")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
        return True


def install_dependencies():
    """Install required dependencies."""
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing dependencies"
    )


def create_virtual_environment():
    """Create virtual environment if it doesn't exist."""
    venv_path = Path(".venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    return run_command(
        f"{sys.executable} -m venv .venv",
        "Creating virtual environment"
    )


def test_installation():
    """Test the installation by running a simple import."""
    print("🧪 Testing installation...")
    try:
        # Add current directory to Python path
        sys.path.insert(0, str(Path.cwd()))
        
        # Test imports
        from python.utils.env_manager import env_manager
        from python.agent.core import Agent, AgentConfig
        
        print("✅ Core modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 Aegis Agent Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create virtual environment
    if not create_virtual_environment():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create environment file
    if not create_env_file():
        return False
    
    # Test installation
    if not test_installation():
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your DeepSeek API key")
    print("2. Run: python run.py")
    print("3. Test DeepSeek integration: python examples/deepseek_integration.py")
    print("\n📖 For more information, see README.md")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 