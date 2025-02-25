from gpt_planner import generate_improved_plan
from typing import Dict, Any
from datetime import datetime, timedelta
import re

def generate_plan(analysis: Dict[str, Any]) -> str:
    """
    Generate implementation plan based on requirements analysis using GPT
    Falls back to basic plan generation if GPT generation fails
    """
    try:
        # Always try GPT-4 first for enhanced plan generation
        return generate_improved_plan(analysis)
    except Exception as e:
        print(f"Falling back to basic plan generation: {str(e)}")
        return generate_basic_plan(analysis)

def generate_basic_plan(analysis: Dict[str, Any]) -> str:
    """Basic plan generation logic as fallback"""
    # Calculate timeline details
    total_weeks = 12  # Default timeline
    
    # Calculate phase durations (in weeks)
    phase_durations = {
        'Initial Setup': max(2, int(total_weeks * 0.2)),
        'Development': max(4, int(total_weeks * 0.4)),
        'Testing': max(2, int(total_weeks * 0.25)),
        'Deployment': max(1, int(total_weeks * 0.15))
    }
    
    # Generate timeline dates
    start_date = datetime.now()
    current_date = start_date
    phase_dates = {}
    
    for phase, duration in phase_durations.items():
        phase_end = current_date + timedelta(weeks=duration)
        phase_dates[phase] = {
            'start': current_date.strftime('%Y-%m-%d'),
            'end': phase_end.strftime('%Y-%m-%d'),
            'duration': duration
        }
        current_date = phase_end

    # Calculate months and remaining weeks
    months = total_weeks // 4
    remaining_weeks = total_weeks % 4
    duration_text = f"{total_weeks} weeks ({months} months, {remaining_weeks} weeks)"

    plan_sections = []
    
    # Project Duration at the very top
    duration_section = [
        "Total Project Duration:",
        f"- {duration_text}",
        f"- Start Date: {start_date.strftime('%Y-%m-%d')}",
        f"- End Date: {current_date.strftime('%Y-%m-%d')}",
        "\n"
    ]
    plan_sections.append('\n'.join(duration_section))
    
    # Project Overview
    overview = [
        "# Project Overview",
        "",
        "Core Modules:",
        *[f"- {module}" for module in analysis['modules']],
        "",
        "Phase Breakdown:"
    ]
    
    for i, (phase, details) in enumerate(phase_dates.items(), 1):
        overview.extend([
            f"{i}. {phase} ({details['duration']} weeks)",
            f"   - Start: {details['start']}",
            f"   - End: {details['end']}",
            ""
        ])
        
    plan_sections.append('\n'.join(overview))
    
    # Implementation Phases with detailed steps
    phases = ["# Implementation Phases"]
    for i, (phase, details) in enumerate(phase_dates.items(), 1):
        phase_content = []
        if phase == 'Initial Setup':
            phase_content = [
                "- Environment setup and configuration",
                "- Module installation and basic configuration",
                "- Initial database setup",
                "- User access configuration"
            ]
        elif phase == 'Development':
            phase_content = [
                "- Configure core modules",
                "- Implement customizations",
                "- Develop integrations",
                "- Setup workflows"
            ]
        elif phase == 'Testing':
            phase_content = [
                "- Unit testing",
                "- Integration testing",
                "- User acceptance testing",
                "- Performance testing"
            ]
        else:  # Deployment
            phase_content = [
                "- Data migration",
                "- User training",
                "- Go-live preparation",
                "- Post-deployment support"
            ]
        
        phases.extend([
            f"{i}. {phase}",
            f"   Duration: {details['duration']} weeks",
            f"   Timeline: {details['start']} to {details['end']}",
            "",
            *[f"   {step}" for step in phase_content],
            ""
        ])
    
    plan_sections.append('\n'.join(phases))
    
    # Technical Requirements
    tech_requirements = [
        "# Technical Requirements",
        "- Use only out-of-the-box Odoo features wherever possible",
        "- Standard Odoo workflow configurations",
        *[f"- {req}" for req in analysis['technical_requirements']]
    ]
    
    plan_sections.append('\n'.join(tech_requirements))
    
    # Risk Analysis
    risks = generate_risk_analysis(analysis)
    plan_sections.append(f"# Risk Analysis\n{risks}")
    
    return '\n\n'.join(plan_sections)

def generate_risk_analysis(analysis: Dict[str, Any]) -> str:
    """Generate risk analysis based on project complexity and requirements"""
    risks = [
        "- Ensure all customizations stay within Odoo's standard feature set",
        "- User adoption of standard Odoo workflows may require additional training"
    ]
    
    if analysis['complexity'] == 'high':
        risks.extend([
            "- Complex requirements may need to be simplified to fit standard features",
            "- Timeline may need adjustment based on complexity"
        ])
    
    if analysis['technical_requirements']:
        risks.append("- Technical constraints may impact implementation approach")
    
    return '\n'.join(risks)
