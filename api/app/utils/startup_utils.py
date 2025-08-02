import os
from typing import List


def validate_environment_variables() -> List[str]:
    """Validate that required environment variables are set"""
    required_vars = [
        "OPENAI_API_KEY",
        "TAVILY_API_KEY", 
        "LANGCHAIN_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return missing_vars


def print_startup_info():
    """Print startup information and warnings"""
    print("🏛️ Federal Ethics Compliance Chatbot API")
    print("=" * 50)
    
    # Check environment variables
    missing_vars = validate_environment_variables()
    
    if missing_vars:
        print("⚠️ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("   Please check your .env.local file")
    else:
        print("✅ All required environment variables configured")
    
    print("\n🧠 Agentic Workflow Features:")
    print("   - Planning Agent (GPT-4o-mini)")
    print("   - Parallel Web Search (3x faster)")
    print("   - Reflection Agent (quality assurance)")
    print("   - Federal Ethics Law RAG")
    
    print("\n📚 Available Endpoints:")
    print("   - POST /api/chat - Ethics consultation")
    print("   - GET /api/health - Health check")
    print("   - GET /docs - API documentation")
    
    print("")