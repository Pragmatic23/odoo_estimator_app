import os
import openai
from typing import Dict, Any
from openai import OpenAI

# Initialize OpenAI client with error handling
def get_openai_client():
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key is not set in environment variables")
    return OpenAI(api_key=api_key)

def generate_improved_plan(analysis: Dict[str, Any]) -> str:
    """Generate an improved implementation plan using OpenAI GPT"""
    
    # Create a prompt for GPT based on the analysis
    modules_list = ', '.join(analysis['modules'])
    technical_reqs = '\n'.join(analysis['technical_requirements']) if analysis['technical_requirements'] else 'No specific technical requirements'
    
    prompt = f"""Generate a detailed ERP implementation plan for the following requirements:

Core Modules to be implemented: {modules_list}
Project Complexity: {analysis['complexity']}
Technical Requirements:
{technical_reqs}

The plan should include:
1. Project Overview with exact timeline details
   - Total duration in weeks and months
   - Clear start and end dates
   - Phase-specific durations
2. Detailed phase breakdown:
   - Initial Setup
   - Development
   - Testing
   - Deployment
3. Specific tasks and milestones for each phase
4. Risk assessment and mitigation strategies
5. Technical considerations and best practices
6. Resource allocation recommendations

Please format the response with clear section headers and use markdown formatting."""

    try:
        # Get OpenAI client
        client = get_openai_client()
        
        # Call OpenAI API with improved error handling
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": """You are an expert ERP implementation consultant specializing in Odoo ERP systems. 
                    Generate detailed, practical implementation plans with clear timeline breakdowns and specific technical tasks."""
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Extract and return the generated plan
        return response.choices[0].message.content.strip()
        
    except openai.APIError as e:
        print(f"OpenAI API Error: {str(e)}")
        from plan_generator import generate_basic_plan
        return generate_basic_plan(analysis)
    except Exception as e:
        print(f"Error generating plan with GPT: {str(e)}")
        from plan_generator import generate_basic_plan
        return generate_basic_plan(analysis)
