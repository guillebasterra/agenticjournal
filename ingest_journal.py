import re
import json

def parse_markdown_journal(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # This regex assumes your journal uses "## Tuesday 20 January 2026" style headings
    entries = re.split(r'\n### ', content)
    structured_entries = []
    
    for i, entry in enumerate(entries):
        if not entry.strip(): continue
        lines = entry.strip().split('\n')
        date = lines[0] # The heading text
        text = "\n".join(lines[1:]) # Everything under the heading
        
        structured_entries.append({
            "id": f"entry_{i:03}",
            "date": date,
            "text": text
        })
    return structured_entries

# Run it and save to your data folder
data = parse_markdown_journal('your_journal.md')
with open('data/entries.json', 'w') as f:
    json.dump(data, f, indent=4)
