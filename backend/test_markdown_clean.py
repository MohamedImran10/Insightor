"""
Quick test to verify markdown cleaning logic
"""

def clean_markdown_symbols(text: str) -> str:
    """Test version of markdown cleaning"""
    if not text:
        return text
    
    text = text.strip()
    
    # Remove all ** (bold markdown)
    while '**' in text:
        text = text.replace('**', '')
    
    # Remove all __ (alternate bold)
    while '__' in text:
        text = text.replace('__', '')
    
    # Remove all ~~ (strikethrough)
    while '~~' in text:
        text = text.replace('~~', '')
    
    # Remove leading/trailing asterisks
    text = text.strip('*')
    
    # Remove multiple spaces
    text = ' '.join(text.split())
    
    return text.strip()


# Test cases
test_cases = [
    '**Advanced Reasoning in AI** - AI reasoning is driving increased compute demand',
    'Some **bold text** with asterisks',
    '**Key Finding**: This is important',
    'Normal text without **anything**',
    '** Extra spaces ** at start and end',
    '***triple asterisks***',
]

print('✅ Markdown Cleaning Test Results:\n')
for text in test_cases:
    cleaned = clean_markdown_symbols(text)
    print(f'Original: {text}')
    print(f'Cleaned:  {cleaned}')
    print(f'Has **:   {"YES ❌" if "**" in cleaned else "NO ✓"}')
    print()
