from collections import Counter
from typing import Dict, List, Any

def analyze_modules(requirements: List[Any]) -> Dict:
    """Analyze module usage patterns"""
    all_modules = []
    for req in requirements:
        modules = [m.strip() for m in req.modules_involved.split(',')]
        all_modules.extend(modules)
    
    counter = Counter(all_modules)
    top_modules = dict(counter.most_common(5))
    
    # Ensure we always return lists for JSON serialization
    return {
        'labels': list(top_modules.keys()) if top_modules else ['No data'],
        'values': list(top_modules.values()) if top_modules else [0]
    }

def analyze_complexity(requirements: List[Any]) -> Dict:
    """Analyze complexity distribution"""
    complexity_counts = Counter(req.complexity for req in requirements)
    values = [
        complexity_counts.get('low', 0),
        complexity_counts.get('medium', 0),
        complexity_counts.get('high', 0)
    ]
    
    return {
        'labels': ['Low', 'Medium', 'High'],
        'values': values if sum(values) > 0 else [0, 1, 0]  # Default to medium if no data
    }

def analyze_timeline(requirements: List[Any]) -> Dict:
    """Analyze project timeline patterns"""
    def extract_months(timeline: str) -> int:
        if not timeline:
            return 0
        import re
        match = re.search(r'(\d+)\s*(?:month|months|mo)', timeline.lower())
        return int(match.group(1)) if match else 0
    
    timeline_ranges = ['1-3 months', '4-6 months', '7-12 months', '12+ months']
    counts = [0] * len(timeline_ranges)
    
    for req in requirements:
        months = extract_months(req.preferred_timeline)
        if months > 0:
            if months <= 3:
                counts[0] += 1
            elif months <= 6:
                counts[1] += 1
            elif months <= 12:
                counts[2] += 1
            else:
                counts[3] += 1
    
    return {
        'labels': timeline_ranges,
        'values': counts if sum(counts) > 0 else [0, 0, 0, 0]
    }

def get_requirements_stats(requirements: List[Any]) -> Dict:
    """Get overall requirements statistics"""
    if not requirements:
        return {
            'total_requirements': 0,
            'avg_complexity': 'N/A',
            'common_type': 'N/A'
        }
    
    # Calculate average complexity
    complexity_scores = {'low': 1, 'medium': 2, 'high': 3}
    total_score = sum(complexity_scores.get(req.complexity, 2) for req in requirements)  # Default to medium
    avg_score = total_score / len(requirements)
    
    if avg_score < 1.67:
        avg_complexity = 'Low'
    elif avg_score < 2.34:
        avg_complexity = 'Medium'
    else:
        avg_complexity = 'High'
    
    # Get most common type
    type_counter = Counter(req.customization_type for req in requirements)
    common_type = type_counter.most_common(1)[0][0] if type_counter else 'N/A'
    
    return {
        'total_requirements': len(requirements),
        'avg_complexity': avg_complexity,
        'common_type': common_type.replace('_', ' ').title()
    }
