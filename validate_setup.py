#!/usr/bin/env python3
"""
Lightweight Trading Bot - Setup Validation Script
Tests the system without requiring full installation
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    if sys.version_info >= (3, 8):
        print(f"✅ Python {sys.version.split()[0]} - Compatible")
        return True
    else:
        print(f"❌ Python {sys.version.split()[0]} - Requires 3.8+")
        return False

def check_file_structure():
    """Check that all required files exist"""
    print("\n📁 Checking file structure...")
    required_files = [
        'main.py',
        'trader.py', 
        'technical_analysis.py',
        'scraper.py',
        'bot.py',
        'config.py',
        'database.py',
        'requirements.txt',
        'setup_ubuntu.sh',
        'README.md'
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - Missing")
            all_exist = False
    
    return all_exist

def check_requirements():
    """Check requirements.txt for lightweight dependencies"""
    print("\n📋 Checking requirements.txt...")
    
    if not Path('requirements.txt').exists():
        print("❌ requirements.txt missing")
        return False
    
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    # Check for removed heavy dependencies
    heavy_deps = ['talib', 'quantlib', 'zipline', 'matplotlib', 'plotly', 'xgboost', 'lightgbm', 'catboost']
    removed_deps = []
    
    for dep in heavy_deps:
        if dep.lower() in content.lower():
            print(f"⚠️  Found heavy dependency: {dep}")
        else:
            removed_deps.append(dep)
    
    # Check for essential lightweight dependencies
    essential_deps = ['oandapyV20', 'python-telegram-bot', 'numpy', 'pandas', 'aiosqlite', 'textblob']
    found_essential = []
    
    for dep in essential_deps:
        if dep in content:
            found_essential.append(dep)
            print(f"✅ {dep} - Found")
        else:
            print(f"❌ {dep} - Missing")
    
    print(f"\n📊 Heavy dependencies removed: {len(removed_deps)}/{len(heavy_deps)}")
    print(f"📊 Essential dependencies found: {len(found_essential)}/{len(essential_deps)}")
    
    return len(found_essential) == len(essential_deps)

def check_technical_analysis():
    """Check technical analysis implementation"""
    print("\n📊 Checking technical analysis module...")
    
    if not Path('technical_analysis.py').exists():
        print("❌ technical_analysis.py missing")
        return False
    
    with open('technical_analysis.py', 'r') as f:
        content = f.read()
    
    # Check for key technical indicators
    indicators = [
        'calculate_rsi',
        'calculate_macd', 
        'calculate_bollinger_bands',
        'calculate_stochastic',
        'calculate_atr',
        'calculate_adx',
        'calculate_williams_r',
        'calculate_cci',
        'calculate_obv',
        'calculate_mfi',
        'calculate_vwap'
    ]
    
    found_indicators = []
    for indicator in indicators:
        if indicator in content:
            found_indicators.append(indicator)
            print(f"✅ {indicator}")
        else:
            print(f"❌ {indicator} - Missing")
    
    print(f"\n📈 Technical indicators implemented: {len(found_indicators)}/{len(indicators)}")
    return len(found_indicators) >= len(indicators) * 0.8  # 80% threshold

def check_import_syntax():
    """Check Python syntax and imports in key files"""
    print("\n🔍 Checking Python syntax...")
    
    key_files = ['main.py', 'technical_analysis.py', 'config.py', 'database.py']
    syntax_ok = True
    
    for file in key_files:
        if Path(file).exists():
            try:
                with open(file, 'r') as f:
                    compile(f.read(), file, 'exec')
                print(f"✅ {file} - Syntax OK")
            except SyntaxError as e:
                print(f"❌ {file} - Syntax Error: {e}")
                syntax_ok = False
            except Exception as e:
                print(f"⚠️  {file} - Warning: {e}")
        else:
            print(f"❌ {file} - File missing")
            syntax_ok = False
    
    return syntax_ok

def check_setup_script():
    """Check setup script"""
    print("\n🚀 Checking setup script...")
    
    if Path('setup_ubuntu.sh').exists():
        # Check if executable
        if os.access('setup_ubuntu.sh', os.X_OK):
            print("✅ setup_ubuntu.sh - Executable")
        else:
            print("⚠️  setup_ubuntu.sh - Not executable (run: chmod +x setup_ubuntu.sh)")
        
        # Check content
        with open('setup_ubuntu.sh', 'r') as f:
            content = f.read()
        
        if 'ubuntu' in content.lower() and 'requirements.txt' in content:
            print("✅ setup_ubuntu.sh - Content looks good")
            return True
        else:
            print("⚠️  setup_ubuntu.sh - Content may be incomplete")
            return False
    else:
        print("❌ setup_ubuntu.sh - Missing")
        return False

def estimate_installation_size():
    """Estimate installation size"""
    print("\n💾 Estimating installation footprint...")
    
    if not Path('requirements.txt').exists():
        print("❌ Cannot estimate - requirements.txt missing")
        return False
    
    with open('requirements.txt', 'r') as f:
        lines = f.readlines()
    
    # Count non-comment, non-empty lines
    deps = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
    
    print(f"📦 Dependencies: {len(deps)} packages")
    
    # Rough estimation based on lightweight packages
    estimated_size = len(deps) * 2  # ~2MB per lightweight package average
    
    if estimated_size < 100:
        print(f"✅ Estimated size: ~{estimated_size}MB (Lightweight)")
        return True
    else:
        print(f"⚠️  Estimated size: ~{estimated_size}MB (May be heavy)")
        return False

def generate_report():
    """Generate comprehensive validation report"""
    print("\n" + "="*60)
    print("🎯 LIGHTWEIGHT TRADING BOT - VALIDATION REPORT")
    print("="*60)
    
    checks = [
        ("Python Version", check_python_version()),
        ("File Structure", check_file_structure()),
        ("Requirements", check_requirements()),
        ("Technical Analysis", check_technical_analysis()),
        ("Python Syntax", check_import_syntax()),
        ("Setup Script", check_setup_script()),
        ("Installation Size", estimate_installation_size())
    ]
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    print(f"\n📊 VALIDATION SUMMARY:")
    print(f"✅ Passed: {passed}/{total} checks")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED!")
        print("✅ Your trading bot is ready for lightweight deployment!")
        print("\n🚀 Next steps:")
        print("1. Run: chmod +x setup_ubuntu.sh")
        print("2. Run: ./setup_ubuntu.sh")
        print("3. Export your environment variables")
        print("4. Start trading!")
    elif passed >= total * 0.8:
        print("\n⚠️  MOSTLY READY - Minor issues detected")
        print("🔧 Fix the failed checks and try again")
    else:
        print("\n❌ SIGNIFICANT ISSUES DETECTED")
        print("🛠️  Please review and fix the failed checks")
    
    print("\n" + "="*60)
    
    return passed == total

if __name__ == "__main__":
    print("🚀 Lightweight Trading Bot - Setup Validation")
    print("=" * 50)
    
    try:
        success = generate_report()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Validation failed with error: {e}")
        sys.exit(1)