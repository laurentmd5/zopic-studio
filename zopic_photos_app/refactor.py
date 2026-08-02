import os
import re

def refactor_flutter():
    base_dir = r"E:\ZoPic Studio\zopic_photos_app\lib"
    
    # 1. First, rename files
    for root, dirs, files in os.walk(base_dir, topdown=False):
        for file in files:
            if 'event' in file.lower() or 'album' in file.lower():
                old_path = os.path.join(root, file)
                new_file = file.replace('event', 'competition').replace('album', 'epreuve')
                new_path = os.path.join(root, new_file)
                os.rename(old_path, new_path)
                print(f"Renamed file {old_path} -> {new_path}")
                
        # 2. Rename directories
        for d in dirs:
            if 'event' in d.lower() or 'album' in d.lower():
                old_path = os.path.join(root, d)
                new_dir = d.replace('event', 'competition').replace('album', 'epreuve')
                new_path = os.path.join(root, new_dir)
                os.rename(old_path, new_path)
                print(f"Renamed dir {old_path} -> {new_path}")

    # 3. Content replacement
    replacements = [
        # UI Texts
        (r'Événements', 'Compétitions'),
        (r'Événement', 'Compétition'),
        (r'événement', 'compétition'),
        (r'Albums', 'Épreuves'),
        (r'Album', 'Épreuve'),
        (r'Participants', 'Athlètes'),
        (r'Participant', 'Athlète'),
        (r'participant', 'athlète'),
        
        # Dart Code identifiers
        (r'\bEvent\b', 'Competition'),
        (r'\bevent\b', 'competition'),
        (r'\bevents\b', 'competitions'),
        (r'\bEventPage\b', 'CompetitionPage'),
        (r'\bEventRepository\b', 'CompetitionRepository'),
        (r'\bMockEventRepository\b', 'MockCompetitionRepository'),
        
        (r'\bAlbum\b', 'Epreuve'),
        (r'\balbum\b', 'epreuve'),
        (r'\balbums\b', 'epreuves'),
        
        (r'event_id', 'competition_id'),
        (r'album_id', 'epreuve_id'),
    ]

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.dart'):
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                new_content = content
                for pattern, repl in replacements:
                    new_content = re.sub(pattern, repl, new_content)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Updated {filepath}")

if __name__ == "__main__":
    refactor_flutter()
