import os
import openai
from typing import Dict, Any

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

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
1. Project Overview with timeline estimates
2. Detailed phase breakdown (Initial Setup, Development, Testing, Deployment)
3. Specific tasks and milestones for each phase
4. Risk assessment and mitigation strategies
5. Technical considerations and best practices
6. Resource allocation recommendations

Please format the response with Markdown headings and bullet points."""

    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert ERP implementation consultant specializing in Odoo ERP systems. Generate detailed, practical implementation plans."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Extract and return the generated plan
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        # Fallback to basic plan generation if API call fails
        print(f"Error generating plan with GPT: {str(e)}")
        from plan_generator import generate_plan
        return generate_plan(analysis)
