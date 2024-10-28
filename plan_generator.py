from datetime import datetime, timedelta

def generate_plan(analysis):
    """
    Generate implementation plan based on requirements analysis
    """
    plan_sections = []
    
    # Project Overview
    plan_sections.append({
        'title': 'Project Overview',
        'content': f"Complexity Level: {analysis['complexity'].title()}\n"
                  f"Estimated Duration: {analysis['estimated_duration']}\n"
                  f"Core Modules: {', '.join(analysis['modules'])}"
    })
    
    # Implementation Phases
    phases = generate_implementation_phases(analysis)
    plan_sections.append({
        'title': 'Implementation Phases',
        'content': '\n'.join(phases)
    })
    
    # Technical Requirements
    plan_sections.append({
        'title': 'Technical Requirements',
        'content': '\n'.join(analysis['technical_requirements']) if analysis['technical_requirements'] else 'No specific technical constraints identified.'
    })
    
    # Risk Analysis
    risks = generate_risk_analysis(analysis)
    plan_sections.append({
        'title': 'Risk Analysis',
        'content': risks
    })
    
    return '\n\n'.join([f"# {section['title']}\n{section['content']}" for section in plan_sections])

def generate_implementation_phases(analysis):
    """Generate implementation phases based on complexity and requirements"""
    phases = []
    
    # Initial Setup Phase
    phases.append("1. Initial Setup (1-2 weeks)")
    phases.append("   - Environment setup and configuration")
    phases.append("   - Module installation and basic configuration")
    
    # Development Phase
    if analysis['complexity'] == 'high':
        duration = "8-12 weeks"
    elif analysis['complexity'] == 'medium':
        duration = "4-8 weeks"
    else:
        duration = "2-4 weeks"
        
    phases.append(f"\n2. Development Phase ({duration})")
    for feature in analysis['key_features']:
        phases.append(f"   - {feature}")
        
    # Testing Phase
    phases.append("\n3. Testing Phase (2-3 weeks)")
    phases.append("   - Unit testing")
    phases.append("   - Integration testing")
    phases.append("   - User acceptance testing")
    
    # Deployment Phase
    phases.append("\n4. Deployment Phase (1-2 weeks)")
    phases.append("   - Data migration")
    phases.append("   - User training")
    phases.append("   - Go-live preparation")
    
    return phases

def generate_risk_analysis(analysis):
    """Generate risk analysis based on project complexity and requirements"""
    risks = []
    
    if analysis['complexity'] == 'high':
        risks.append("- High project complexity may require additional testing and validation")
        risks.append("- Multiple module integration points increase potential for conflicts")
        
    if len(analysis['technical_requirements']) > 3:
        risks.append("- Multiple technical constraints may impact development timeline")
        
    if not analysis['technical_requirements']:
        risks.append("- Lack of detailed technical requirements may lead to assumptions and rework")
        
    return '\n'.join(risks) if risks else "No significant risks identified."
