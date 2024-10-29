def generate_plan(analysis):
    """
    Generate implementation plan based on requirements analysis with updated specifications
    """
    plan_sections = []
    
    # Project Overview
    plan_sections.append({
        'title': 'Project Overview',
        'content': f"Complexity Level: {analysis['complexity'].title()}\n"
                  f"Core Modules: Accounting, Sales, CRM\n"
                  f"Technical Approach: Out-of-the-box Odoo features only"
    })
    
    # Implementation Phases
    phases = [
        "1. Initial Setup (1-2 weeks)",
        "   - Environment setup and configuration",
        "   - Module installation and basic configuration",
        "   - Initial database setup",
        "",
        "2. Development Phase (4-8 weeks)",
        "   - Configure Accounting module with Odoo-supported bank integrations",
        "   - Setup Sales module with standard workflows",
        "   - Implement CRM module with basic automation",
        "   - Integration between core modules",
        "",
        "3. Testing Phase (2-3 weeks)",
        "   - Unit testing",
        "   - Integration testing",
        "   - User acceptance testing",
        "",
        "4. Deployment Phase (1-2 weeks)",
        "   - Data migration",
        "   - User training",
        "   - Go-live preparation"
    ]
    
    plan_sections.append({
        'title': 'Implementation Phases',
        'content': '\n'.join(phases)
    })
    
    # Technical Requirements
    tech_requirements = [
        "- Use only out-of-the-box Odoo features wherever possible to maintain compatibility with future Odoo updates",
        "- No external payment gateways; only Odoo-supported bank integrations",
        "- Standard Odoo workflow configurations"
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
        "- Bank integration complexity may affect timeline",
        "- User adoption of standard Odoo workflows may require additional training"
    ]
    
    if analysis['complexity'] == 'high':
        risks.append("- Complex requirements may need to be simplified to fit standard features")
    
    return '\n'.join(risks)
