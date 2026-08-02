import os
import re

def refactor_frontend():
    base_dir = r"E:\ZoPic Studio\frontend-web\src"
    
    # Files to rename
    renames = {
        r"pages\Events.tsx": r"pages\Competitions.tsx",
        r"pages\Events.module.css": r"pages\Competitions.module.css",
        r"pages\EventDetail.tsx": r"pages\CompetitionDetail.tsx",
        r"pages\EventDetail.module.css": r"pages\CompetitionDetail.module.css",
        r"services\eventsService.ts": r"services\competitionsService.ts"
    }

    # Perform renames
    for old, new in renames.items():
        old_path = os.path.join(base_dir, old)
        new_path = os.path.join(base_dir, new)
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            print(f"Renamed {old_path} -> {new_path}")

    replacements = [
        # Imports & Code tokens
        (r'\bEventDetail\b', 'CompetitionDetail'),
        (r'\beventsService\b', 'competitionsService'),
        (r'\bEvents\.module\.css\b', 'Competitions.module.css'),
        (r'\bEventDetail\.module\.css\b', 'CompetitionDetail.module.css'),
        
        # We must be careful with Event since it's a native DOM interface, but in our code it's mostly our types.
        # Let's replace 'Event' -> 'Competition' but NOT 'React.ChangeEvent' etc.
        # We will use lookbehinds and lookaheads, but let's just do it simple for now, and manual fix if needed.
        (r'(?<!React\.Change)(?<!React\.Form)(?<!React\.MouseEvent)(?<!React\.Keyboard)(?<!DOM)\bEvent\b(?!s)', 'Competition'),
        (r'\bevents\b', 'competitions'),
        (r'\bevent\b', 'competition'),
        (r'\bEventCreate\b', 'CompetitionCreate'),
        (r'\bEventResponse\b', 'CompetitionResponse'),
        
        # Albums
        (r'\bAlbum\b', 'Epreuve'),
        (r'\balbum\b', 'epreuve'),
        (r'\balbums\b', 'epreuves'),
        
        # French UI Text
        (r'Événements', 'Compétitions'),
        (r'Événement', 'Compétition'),
        (r'événement', 'compétition'),
        (r'Albums', 'Épreuves'),
        (r'Album', 'Épreuve'),
        
        # Specific paths
        (r"'/events'", "'/competitions'"),
        (r"'/events/'", "'/competitions/'"),
        (r"path=\"events\"", 'path="competitions"'),
        (r"path=\"events/:eventId\"", 'path="competitions/:competitionId"'),
    ]

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.tsx') or file.endswith('.ts') or file.endswith('.css'):
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                new_content = content
                for pattern, repl in replacements:
                    new_content = re.sub(pattern, repl, new_content)
                
                # Fix React Events just in case we broke them:
                new_content = new_content.replace('React.ChangeCompetition', 'React.ChangeEvent')
                new_content = new_content.replace('React.FormCompetition', 'React.FormEvent')
                new_content = new_content.replace('preventCompetitionDefault', 'preventDefault')
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Updated {filepath}")

if __name__ == "__main__":
    refactor_frontend()
