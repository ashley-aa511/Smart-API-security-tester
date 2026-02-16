"""
Coordinator Agent - Plans and orchestrates security scans
Uses Azure OpenAI to intelligently decide which tests to run
"""
import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()


class CoordinatorAgent:
    """
    Intelligent agent that analyzes APIs and creates optimal security scan plans.
    
    This agent uses Azure OpenAI to:
    1. Analyze API endpoints and their purposes
    2. Identify potential risk areas
    3. Prioritize security tests based on risk
    4. Create an execution plan for the scanner agent
    """
    
    def __init__(self):
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
    async def analyze_api(self, target_url: str, headers: Optional[Dict] = None) -> Dict:
        """
        Analyzes the target API to understand its structure and purpose.
        
        Args:
            target_url: The API endpoint to analyze
            headers: Optional authentication headers
            
        Returns:
            Analysis containing API type, authentication method, risk profile
        """
        prompt = f"""
        Analyze this API endpoint and provide security recommendations:
        
        URL: {target_url}
        Headers: {json.dumps(headers or {}, indent=2)}
        
        Determine:
        1. API type (REST, GraphQL, etc.)
        2. Authentication method (Bearer, API Key, OAuth, None)
        3. Data sensitivity level (Low, Medium, High, Critical)
        4. Likely purpose/business domain
        5. Key risk areas to focus on
        
        Respond in JSON format:
        {{
            "api_type": "REST",
            "auth_method": "Bearer Token",
            "data_sensitivity": "High",
            "domain": "Financial Services",
            "risk_areas": ["authentication", "authorization", "data_exposure"],
            "reasoning": "Brief explanation"
        }}
        """
        
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {
                    "role": "system",
                    "content": "You are a security expert specializing in API security assessment."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temperature for more consistent analysis
            response_format={"type": "json_object"}
        )
        
        analysis = json.loads(response.choices[0].message.content)
        return analysis
    
    async def create_scan_plan(self, api_analysis: Dict) -> Dict:
        """
        Creates an intelligent scan plan based on API analysis.
        
        Args:
            api_analysis: Results from analyze_api()
            
        Returns:
            Prioritized test plan with specific parameters
        """
        prompt = f"""
        Based on this API analysis, create an optimal security testing plan:
        
        {json.dumps(api_analysis, indent=2)}
        
        Available test categories (OWASP API Security Top 10):
        1. API1:2023 - Broken Object Level Authorization (BOLA)
        2. API2:2023 - Broken Authentication
        3. API3:2023 - Broken Object Property Level Authorization
        4. API4:2023 - Unrestricted Resource Consumption
        5. API5:2023 - Broken Function Level Authorization
        6. API7:2023 - Server Side Request Forgery (SSRF)
        7. API8:2023 - Security Misconfiguration
        8. API9:2023 - Improper Inventory Management
        9. API10:2023 - Injection Vulnerabilities
        
        Create a prioritized test plan in JSON format:
        {{
            "priority_tests": [
                {{
                    "test_id": "API2",
                    "test_name": "Broken Authentication",
                    "priority": "CRITICAL",
                    "reason": "API uses Bearer tokens, high value target",
                    "parameters": {{
                        "focus_areas": ["token_validation", "session_management"],
                        "intensity": "high"
                    }}
                }}
            ],
            "recommended_order": ["API2", "API5", "API1", "API10", "API8"],
            "estimated_duration_minutes": 15,
            "special_considerations": ["Rate limiting may trigger after 10 requests"]
        }}
        
        Prioritize based on:
        - Data sensitivity level
        - Authentication complexity
        - Risk areas identified
        - Likely attack vectors for this domain
        """
        
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert penetration tester planning API security assessments."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
            response_format={"type": "json_object"}
        )
        
        scan_plan = json.loads(response.choices[0].message.content)
        return scan_plan
    
    async def plan_scan(self, target_url: str, headers: Optional[Dict] = None) -> Dict:
        """
        Main entry point: Analyzes API and creates complete scan plan.
        
        Args:
            target_url: API endpoint to scan
            headers: Optional authentication headers
            
        Returns:
            Complete scan plan ready for execution
        """
        print("🤖 Coordinator Agent: Analyzing target API...")
        
        # Step 1: Analyze the API
        api_analysis = await self.analyze_api(target_url, headers)
        print(f"✓ Analysis complete: {api_analysis['domain']} API")
        print(f"  Data Sensitivity: {api_analysis['data_sensitivity']}")
        print(f"  Auth Method: {api_analysis['auth_method']}")
        
        # Step 2: Create scan plan
        print("\n🤖 Coordinator Agent: Creating scan plan...")
        scan_plan = await self.create_scan_plan(api_analysis)
        print(f"✓ Plan created: {len(scan_plan['priority_tests'])} tests prioritized")
        print(f"  Estimated duration: {scan_plan['estimated_duration_minutes']} minutes")
        
        # Combine analysis and plan
        return {
            "api_analysis": api_analysis,
            "scan_plan": scan_plan,
            "target_url": target_url,
            "headers": headers or {}
        }


# Test the agent (when run directly)
if __name__ == "__main__":
    import asyncio
    
    async def test_coordinator():
        coordinator = CoordinatorAgent()
        
        # Test with a sample API
        result = await coordinator.plan_scan(
            target_url="https://api.example.com/v1/users",
            headers={"Authorization": "Bearer test-token-123"}
        )
        
        print("\n" + "="*60)
        print("SCAN PLAN RESULTS")
        print("="*60)
        print(json.dumps(result, indent=2))
    
    asyncio.run(test_coordinator())