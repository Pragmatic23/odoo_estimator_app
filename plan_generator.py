def generate_plan(analysis):
    """
    Generate implementation plan based on requirements analysis with updated specifications
    """
    from datetime import datetime, timedelta
    
    # Calculate timeline details
    total_weeks = 0
    if analysis['estimated_duration']:
        # Try to extract months from the duration
        import re
        match = re.search(r'(\d+)\s*(?:month|months|mo)', analysis['estimated_duration'].lower())
        if match:
            months = int(match.group(1))
            total_weeks = months * 4  # Approximate weeks per month
        else:
            # Default timeline if not specified
            total_weeks = 12
    else:
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
            'end': phase_end.strftime('%Y-%m-%d')
        }
        current_date = phase_end

    plan_sections = []
    
    # Project Overview with detailed timeline
    overview = [
        f"Complexity Level: {analysis['complexity'].title()}",
        f"Estimated Duration: {total_weeks} weeks",
        f"Project Start Date: {start_date.strftime('%Y-%m-%d')}",
        f"Project End Date: {current_date.strftime('%Y-%m-%d')}",
        "",
        "Core Modules:",
        *[f"- {module}" for module in analysis['modules']],
        "",
        "Timeline Breakdown:"
    ]
    
    for phase, dates in phase_dates.items():
        overview.append(f"- {phase}")
        overview.append(f"  Start: {dates['start']}")
        overview.append(f"  End: {dates['end']}")
        overview.append("")
        
    plan_sections.append({
        'title': 'Project Overview',
        'content': '\n'.join(overview)
    })
    
    # Implementation Phases with detailed steps
    phases = []
    for phase, dates in phase_dates.items():
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
            f"{phase} ({dates['start']} to {dates['end']})",
            *phase_content,
            ""
        ])
    
    plan_sections.append({
        'title': 'Implementation Phases',
        'content': '\n'.join(phases)
    })
    
    # Technical Requirements
    tech_requirements = [
        "- Use only out-of-the-box Odoo features wherever possible",
        "- Standard Odoo workflow configurations",
        *[f"- {req}" for req in analysis['technical_requirements']]
    ]
    
    plan_sections.append({
        'title': 'Technical Requirements',
        'content': '\n'.join(tech_requirements)
    })
    
    # Risk Analysis
    risks = generate_risk_analysis(analysis)
    plan_sections.append({
        'title': 'Risk Analysis',
        'content': risks
    })
    
    return '\n\n'.join([f"# {section['title']}\n{section['content']}" for section in plan_sections])

def generate_risk_analysis(analysis):
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
