#!/usr/bin/env python3
"""
Integration test: Coordinator Agent + Test API Server
This demonstrates the AI agent analyzing the vulnerable test server
"""
import asyncio
import sys
from src.agents.coordinator_agent import CoordinatorAgent

async def test_integration():
    """Test the coordinator agent against the local test server"""

    print("=" * 70)
    print("INTEGRATION TEST: AI Coordinator + Vulnerable Test Server")
    print("=" * 70)
    print("\nPREREQUISITES:")
    print("1. Test server must be running: python test_api_server.py")
    print("2. Azure OpenAI credentials must be configured in .env")
    print("\nStarting test...\n")

    try:
        # Initialize coordinator agent
        coordinator = CoordinatorAgent()

        # Test scenarios
        test_scenarios = [
            {
                "name": "Anonymous User Access",
                "url": "http://localhost:5000/api/user/1",
                "headers": None
            },
            {
                "name": "Admin Panel Access",
                "url": "http://localhost:5000/api/admin",
                "headers": None
            },
            {
                "name": "Authenticated Request",
                "url": "http://localhost:5000/api/users",
                "headers": {"Authorization": "Bearer fake-token-123"}
            }
        ]

        for idx, scenario in enumerate(test_scenarios, 1):
            print(f"\n{'=' * 70}")
            print(f"SCENARIO {idx}: {scenario['name']}")
            print(f"{'=' * 70}")
            print(f"Target: {scenario['url']}")
            print(f"Headers: {scenario['headers']}")
            print()

            # Get AI-powered scan plan
            result = await coordinator.plan_scan(
                target_url=scenario['url'],
                headers=scenario['headers']
            )

            # Display results
            print("\n" + "-" * 70)
            print("AI ANALYSIS RESULTS:")
            print("-" * 70)

            api_analysis = result['api_analysis']
            print(f"\nAPI Type: {api_analysis.get('api_type', 'Unknown')}")
            print(f"Auth Method: {api_analysis.get('auth_method', 'Unknown')}")
            print(f"Data Sensitivity: {api_analysis.get('data_sensitivity', 'Unknown')}")
            print(f"Domain: {api_analysis.get('domain', 'Unknown')}")
            print(f"\nKey Risk Areas:")
            for area in api_analysis.get('risk_areas', []):
                print(f"  • {area}")
            print(f"\nReasoning: {api_analysis.get('reasoning', 'N/A')}")

            scan_plan = result['scan_plan']
            print(f"\n{'-' * 70}")
            print("RECOMMENDED SCAN PLAN:")
            print("-" * 70)
            print(f"\nPriority Tests ({len(scan_plan.get('priority_tests', []))}):")
            for test in scan_plan.get('priority_tests', [])[:5]:  # Show top 5
                print(f"\n  [{test.get('priority', 'N/A')}] {test.get('test_name', 'Unknown')}")
                print(f"  Reason: {test.get('reason', 'N/A')}")

            print(f"\nRecommended Order: {', '.join(scan_plan.get('recommended_order', []))}")
            print(f"Estimated Duration: {scan_plan.get('estimated_duration_minutes', 'N/A')} minutes")

            if scan_plan.get('special_considerations'):
                print(f"\nSpecial Considerations:")
                for consideration in scan_plan['special_considerations']:
                    print(f"  ⚠ {consideration}")

        print("\n" + "=" * 70)
        print("✓ INTEGRATION TEST COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nNOTE: This demonstrates AI-powered scan planning.")
        print("Actual vulnerability testing is not yet implemented.")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure test_api_server.py is running")
        print("2. Check .env has valid Azure OpenAI credentials")
        print("3. Verify network connectivity")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_integration())
