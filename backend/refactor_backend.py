import os
import re

def refactor_backend():
    dirs_to_process = [
        r"E:\ZoPic Studio\backend\app\modules\competitions",
        r"E:\ZoPic Studio\backend\tests"
    ]
    
    replacements = [
        (r'\bEventBase\b', 'CompetitionBase'),
        (r'\bEventCreate\b', 'CompetitionCreate'),
        (r'\bEventResponse\b', 'CompetitionResponse'),
        (r'\bAlbumBase\b', 'EpreuveBase'),
        (r'\bAlbumCreate\b', 'EpreuveCreate'),
        (r'\bAlbumResponse\b', 'EpreuveResponse'),
        
        (r'\bcreate_event\b', 'create_competition'),
        (r'\bget_events\b', 'get_competitions'),
        (r'\bget_event\b', 'get_competition'),
        (r'\bcreate_album\b', 'create_epreuve'),
        
        (r'\bevent_data\b', 'competition_data'),
        (r'\balbum_data\b', 'epreuve_data'),
        (r'\bdb_event\b', 'db_competition'),
        (r'\bdb_album\b', 'db_epreuve'),
        (r'\bevents_result\b', 'competitions_result'),
        (r'\balbums_result\b', 'epreuves_result'),
        (r'\bevent_ids\b', 'competition_ids'),
        (r'\balbum_ids\b', 'epreuve_ids'),
    ]

    for d in dirs_to_process:
        for root, dirs, files in os.walk(d):
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
                        print(f"Updated {path}")

if __name__ == "__main__":
    refactor_backend()
