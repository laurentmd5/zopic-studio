import os
import re

def refactor_backend_tests():
    tests_dir = r"E:\ZoPic Studio\backend\tests"
    
    # 1. Rename files
    for root, dirs, files in os.walk(tests_dir):
        for file in files:
            if 'event' in file:
                old_path = os.path.join(root, file)
                new_file = file.replace('event', 'competition')
                new_path = os.path.join(root, new_file)
                os.rename(old_path, new_path)
                print(f"Renamed {file} -> {new_file}")

    # 2. Search and replace
    replacements = [
        (r'\bEvent\b', 'Competition'),
        (r'\bevent\b', 'competition'),
        (r'\bevents\b', 'competitions'),
        (r'\bAlbum\b', 'Epreuve'),
        (r'\balbum\b', 'epreuve'),
        (r'\balbums\b', 'epreuves'),
    ]

    for root, dirs, files in os.walk(tests_dir):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = content
                for pattern, repl in replacements:
                    new_content = re.sub(pattern, repl, new_content)
                
                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Updated {file}")

if __name__ == "__main__":
    refactor_backend_tests()
