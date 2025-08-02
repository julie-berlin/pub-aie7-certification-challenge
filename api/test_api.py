#!/usr/bin/env python3
"""
Simple test script for FastAPI backend
"""
import asyncio
import httpx
from app.models.chat_models import ChatRequest, UserContext, UserRole


async def test_api_endpoints():
    """Test the FastAPI backend endpoints"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🧪 Testing FastAPI Backend")
        print("=" * 40)
        
        # Test ping endpoint
        try:
            response = await client.get(f"{base_url}/api/ping")
            print(f"✅ Ping: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"❌ Ping failed: {e}")
        
        # Test health endpoint
        try:
            response = await client.get(f"{base_url}/api/health")
            print(f"✅ Health: {response.status_code}")
            if response.status_code == 200:
                health_data = response.json()
                print(f"   Status: {health_data.get('status')}")
                print(f"   Version: {health_data.get('version')}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
        
        # Test chat endpoint with simple question
        try:
            print("\n🤖 Testing Chat Endpoint...")
            
            test_request = {
                "question": "Can I accept a gift worth $25 from a contractor?",
                "user_context": {
                    "role": "federal_employee",
                    "agency": "GSA",
                    "seniority": "GS-12"
                },
                "include_reflection": True,
                "include_confidence": True
            }
            
            print(f"Question: {test_request['question']}")
            
            response = await client.post(
                f"{base_url}/api/chat",
                json=test_request,
                timeout=120.0  # Allow time for processing
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Chat response received ({response.status_code})")
                print(f"   Processing time: {result.get('processing_time_seconds', 0):.2f}s")
                print(f"   Confidence: {result.get('confidence_score', 0)}/100")
                print(f"   Federal sources: {result.get('federal_law_sources', 0)}")
                print(f"   Web sources: {result.get('web_sources', 0)}")
                print(f"   Response preview: {result.get('response', '')[:100]}...")
            else:
                print(f"❌ Chat request failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Chat endpoint test failed: {e}")


def test_pydantic_models():
    """Test Pydantic model validation"""
    print("\n📋 Testing Pydantic Models")
    print("=" * 30)
    
    try:
        # Test UserContext
        user_context = UserContext(
            role=UserRole.FEDERAL_EMPLOYEE,
            agency="Department of Defense",
            seniority="GS-14",
            grade_level="GS-14"
        )
        print(f"✅ UserContext: {user_context.role}, {user_context.agency}")
        
        # Test ChatRequest
        chat_request = ChatRequest(
            question="Is this an ethics violation?",
            user_context=user_context,
            include_reflection=True
        )
        print(f"✅ ChatRequest: {len(chat_request.question)} chars")
        
    except Exception as e:
        print(f"❌ Pydantic model test failed: {e}")


if __name__ == "__main__":
    print("🚀 FastAPI Backend Test Suite")
    print("=" * 50)
    
    # Test models first
    test_pydantic_models()
    
    # Test API endpoints (server must be running)
    print("\n⚠️ Make sure FastAPI server is running on localhost:8000")
    print("   Run: python3 api/run_server.py")
    input("Press Enter to continue with API tests...")
    
    asyncio.run(test_api_endpoints())
    
    print("\n✅ Test suite completed!")