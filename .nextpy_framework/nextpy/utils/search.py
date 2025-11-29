"""
NextPy Search Utilities
Simple full-text search functionality
"""

from typing import List, Dict, Any
import re


def simple_search(query: str, items: List[Dict[str, Any]], fields: List[str]) -> List[Dict[str, Any]]:
    """Simple full-text search across multiple fields"""
    query_lower = query.lower()
    results = []
    
    for item in items:
        for field in fields:
            if field in item:
                value = str(item.get(field, "")).lower()
                if query_lower in value:
                    results.append(item)
                    break
    
    return results


def fuzzy_search(query: str, items: List[Dict[str, Any]], field: str) -> List[Dict[str, Any]]:
    """Fuzzy search with scoring"""
    def fuzzy_match(pattern: str, text: str) -> int:
        """Calculate fuzzy match score"""
        pattern = pattern.lower()
        text = text.lower()
        score = 0
        j = 0
        
        for i, char in enumerate(pattern):
            pos = text.find(char, j)
            if pos == -1:
                return 0
            score += 1 / (pos - j + 1)
            j = pos + 1
        
        return score
    
    results = []
    for item in items:
        text = str(item.get(field, ""))
        score = fuzzy_match(query, text)
        if score > 0:
            results.append((item, score))
    
    # Sort by score descending
    results.sort(key=lambda x: x[1], reverse=True)
    return [item for item, score in results]


def search_highlight(query: str, text: str) -> str:
    """Highlight search terms in text"""
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(f'<mark>{query}</mark>', text)
