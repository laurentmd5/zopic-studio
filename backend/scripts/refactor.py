import os
import re

def refactor_backend():
    base_dir = r"E:\ZoPic Studio\backend\app"
    
    # We will rename directories and files if necessary.
    # We already renamed 'events' to 'competitions'
    
    replacements = [
        (r'app\.modules\.events', r'app.modules.competitions'),
        (r'\bEvent\b', 'Competition'),
        (r'\bevent\b', 'competition'),
        (r'\bevents\b', 'competitions'),
        (r'\bAlbum\b', 'Epreuve'),
        (r'\balbum\b', 'epreuve'),
        (r'\balbums\b', 'epreuves'),
        (r'\bevent_id\b', 'competition_id'),
        (r'\balbum_id\b', 'epreuve_id'),
    ]

    for root, dirs, files in os.walk(base_dir):
        # Do not process pycache or .venv
        if '__pycache__' in root or '.venv' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                new_content = content
                for pattern, repl in replacements:
                    # We use re.sub for word boundaries if specified, else simple string replace
                    new_content = re.sub(pattern, repl, new_content)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Updated {filepath}")

if __name__ == "__main__":
    refactor_backend()
