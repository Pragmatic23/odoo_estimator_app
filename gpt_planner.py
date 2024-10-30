import os
import openai
from typing import Dict, Any
from datetime import datetime, timedelta

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def generate_improved_plan(analysis: Dict[str, Any]) -> str:
    """Generate an improved implementation plan using OpenAI GPT-4"""
    
    # Create a detailed prompt for GPT based on the analysis
    modules_list = ', '.join(analysis['modules'])
    technical_reqs = '\n'.join([f"- {req}" for req in analysis['technical_requirements']]) if analysis['technical_requirements'] else 'No specific technical requirements'
    
    # Calculate estimated timeline based on complexity
    base_weeks = {'low': 8, 'medium': 12, 'high': 16}
    estimated_weeks = base_weeks.get(analysis['complexity'].lower(), 12)
    
    prompt = f"""As an Odoo ERP implementation expert, create a detailed implementation plan for:

Project Scope:
- Modules to implement: {modules_list}
- Project Complexity: {analysis['complexity']}
- Estimated Duration: {estimated_weeks} weeks

Technical Requirements:
{technical_reqs}

Please provide a comprehensive implementation plan including:

1. Project Overview:
   - Total duration with exact timeline
   - Core modules and their implementation order
   - Resource requirements

2. Implementation Phases:
   - Initial Setup Phase (environment, basic configurations)
   - Development Phase (module customizations, integrations)
   - Testing Phase (unit tests, UAT)
   - Deployment Phase (data migration, training)

3. For each phase include:
   - Specific tasks and milestones
   - Duration estimates in weeks
   - Dependencies and prerequisites
   - Quality checkpoints

4. Technical Considerations:
   - Best practices for Odoo implementation
   - Data migration strategy
   - Integration approaches
   - Security considerations

5. Risk Analysis:
   - Potential challenges
   - Mitigation strategies
   - Critical success factors

Format the response using Markdown with clear headings, bullet points, and proper sectioning."""

    try:
        # Call OpenAI API with enhanced parameters
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert Odoo ERP implementation consultant with extensive experience in planning and executing complex ERP projects. Focus on providing practical, actionable implementation plans with precise timelines and clear deliverables."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500,
            temperature=0.7,
            presence_penalty=0.3,
            frequency_penalty=0.3
        )
        
        # Extract and return the generated plan
        plan = response.choices[0].message.content.strip()
        
        # Add timestamp and version info
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
        plan = f"Plan Generated: {timestamp}\nVersion: GPT-4 Enhanced\n\n{plan}"
        
        return plan
        
    except Exception as e:
        print(f"Error generating plan with GPT-4: {str(e)}")
        # Fallback to basic plan generation
        from plan_generator import generate_basic_plan
        return generate_basic_plan(analysis)
