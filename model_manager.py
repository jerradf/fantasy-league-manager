#!/usr/bin/env python3
"""
Ollama Model Manager
Check current model, suggest optimal alternatives, and benchmark performance
"""

import requests
import json
import time
import sys
from pathlib import Path

OLLAMA_BASE = "http://localhost:11434"

def check_ollama_running():
    """Check if Ollama is running"""
    try:
        response = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_installed_models():
    """Get list of installed models"""
    try:
        response = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("models", [])
    except:
        pass
    return []

def get_current_config_model():
    """Read current model from config.py"""
    config_path = Path(__file__).parent / "config.py"
    try:
        with open(config_path, 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if 'OLLAMA_MODEL' in line and '=' in line:
                    model = line.split('=')[1].strip().strip('"').strip("'")
                    return model
    except:
        pass
    return "qwen2.5:7b"

def benchmark_model(model_name, test_prompt="Analyze this fantasy trade: Player A for Player B. Which side wins?"):
    """Quick benchmark of a model"""
    try:
        start = time.time()
        response = requests.post(
            f"{OLLAMA_BASE}/api/generate",
            json={
                "model": model_name,
                "prompt": test_prompt,
                "stream": False,
                "options": {"temperature": 0.3}
            },
            timeout=60
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            tokens = len(data.get("response", "").split())
            return {
                "success": True,
                "time": elapsed,
                "tokens": tokens,
                "tokens_per_sec": tokens / elapsed if elapsed > 0 else 0
            }
    except Exception as e:
        return {"success": False, "error": str(e)}
    
    return {"success": False}

# Recommended models for fantasy sports analysis
RECOMMENDED_MODELS = {
    "qwen2.5:7b": {
        "description": "Balanced model - good reasoning with fast inference",
        "size": "~4.7GB",
        "speed": "Fast",
        "quality": "High",
        "recommended_for": "Default choice - excellent balance"
    },
    "llama3.1:8b": {
        "description": "Meta's latest - strong reasoning and sports knowledge",
        "size": "~4.9GB",
        "speed": "Fast",
        "quality": "High",
        "recommended_for": "Best for trade analysis"
    },
    "mistral:7b": {
        "description": "Fast inference with good instruction following",
        "size": "~4.1GB",
        "speed": "Very Fast",
        "quality": "Good",
        "recommended_for": "Speed priority"
    },
    "gemma2:9b": {
        "description": "Google's model - excellent at structured output",
        "size": "~5.4GB",
        "speed": "Medium",
        "quality": "Very High",
        "recommended_for": "Complex multi-step analysis"
    },
    "phi3:medium": {
        "description": "Microsoft's efficient model - great for quick decisions",
        "size": "~7.9GB",
        "speed": "Fast",
        "quality": "Good",
        "recommended_for": "Quick lineup decisions"
    }
}

def main():
    print("🤖 Ollama Model Manager for Fantasy League")
    print("="*60)
    print()
    
    # Check Ollama status
    if not check_ollama_running():
        print("❌ Ollama is not running!")
        print("   Start it with: ollama serve")
        sys.exit(1)
    
    print("✅ Ollama is running")
    print()
    
    # Show current model
    current_model = get_current_config_model()
    print(f"📍 Current Model: {current_model}")
    
    if current_model in RECOMMENDED_MODELS:
        info = RECOMMENDED_MODELS[current_model]
        print(f"   Description: {info['description']}")
        print(f"   Size: {info['size']}")
        print(f"   Speed: {info['speed']} | Quality: {info['quality']}")
    
    print()
    print("="*60)
    print()
    
    # Get installed models
    installed = get_installed_models()
    
    if installed:
        print("📦 Installed Models:")
        for model in installed:
            name = model.get("name", "Unknown")
            size = model.get("size", 0) / (1024**3)  # Convert to GB
            modified = model.get("modified_at", "")
            
            indicator = "👉" if name == current_model else "  "
            print(f"{indicator} {name} ({size:.1f}GB)")
        print()
    
    # Show recommendations
    print("="*60)
    print("🎯 Recommended Models for Fantasy Sports:")
    print()
    
    for model_name, info in RECOMMENDED_MODELS.items():
        is_installed = any(m.get("name") == model_name for m in installed)
        is_current = model_name == current_model
        
        status = "✓ INSTALLED" if is_installed else "  Not installed"
        if is_current:
            status = "👉 CURRENT"
        
        print(f"{status} | {model_name}")
        print(f"         {info['description']}")
        print(f"         Size: {info['size']} | Speed: {info['speed']} | Quality: {info['quality']}")
        print(f"         Best for: {info['recommended_for']}")
        
        if not is_installed and not is_current:
            print(f"         Install: ollama pull {model_name}")
        
        print()
    
    print("="*60)
    print()
    
    # Offer to benchmark current model
    print("🔬 Benchmark Options:")
    print("1. Quick test current model")
    print("2. Exit")
    print()
    
    choice = input("Choose option (1-2): ").strip()
    
    if choice == "1":
        print()
        print(f"Testing {current_model}...")
        result = benchmark_model(current_model)
        
        if result["success"]:
            print(f"✅ Response time: {result['time']:.2f}s")
            print(f"   Tokens generated: {result['tokens']}")
            print(f"   Speed: {result['tokens_per_sec']:.1f} tokens/sec")
            
            if result['tokens_per_sec'] > 50:
                print("   ⚡ Excellent speed!")
            elif result['tokens_per_sec'] > 20:
                print("   ✓ Good speed")
            else:
                print("   ⚠️  Consider a faster model")
        else:
            print(f"❌ Benchmark failed: {result.get('error', 'Unknown error')}")
    
    print()
    print("="*60)
    print()
    print("💡 To switch models:")
    print("   1. Install new model: ollama pull <model_name>")
    print("   2. Edit config.py and change OLLAMA_MODEL value")
    print("   3. Restart league_manager.py")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting model manager")
        sys.exit(0)
