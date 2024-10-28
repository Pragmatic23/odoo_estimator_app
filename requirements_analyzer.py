def analyze_requirements(requirement):
    """
    Analyze the requirements using basic text processing to extract key information
    """
    analysis = {
        'modules': [],
        'complexity': 'medium',
        'estimated_duration': '',
        'key_features': [],
        'technical_requirements': []
    }
    
    # Process modules involved
    modules = [module.strip() for module in requirement.modules_involved.split(',')]
    analysis['modules'] = modules
    
    # Estimate complexity based on requirements length and keywords
    complex_keywords = ['integration', 'custom', 'automation', 'workflow', 'third-party']
    text = f"{requirement.project_scope} {requirement.functional_requirements}".lower()
    
    complexity_score = len([word for word in complex_keywords if word in text])
    if complexity_score > 2:
        analysis['complexity'] = 'high'
    elif complexity_score < 1:
        analysis['complexity'] = 'low'
        
    # Extract timeline
    if requirement.preferred_timeline:
        analysis['estimated_duration'] = requirement.preferred_timeline
        
    # Extract key features from functional requirements
    sentences = requirement.functional_requirements.split('.')
    for sent in sentences:
        sent = sent.strip()
        if any(keyword in sent.lower() for keyword in ['need', 'should', 'must', 'require']):
            if sent:
                analysis['key_features'].append(sent)
            
    # Extract technical requirements
    if requirement.technical_constraints:
        tech_sentences = requirement.technical_constraints.split('.')
        for sent in tech_sentences:
            sent = sent.strip()
            if sent:
                analysis['technical_requirements'].append(sent)
            
    return analysis
