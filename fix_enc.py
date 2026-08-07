import os
import glob

replacements = {
    'Ã©': 'é',
    'ÃƒÂ©': 'é',
    'Ã¨': 'è',
    'Ã\xa0': 'à',
    'Ã ': 'à',
    'â€™': "’",
    'Ãª': 'ê',
    'Ã§': 'ç',
    'Ã®': 'î',
    'Ã»': 'û',
    'Ã´': 'ô',
    'Ãœ': 'Ü',
    'Ã¢': 'â',
    'Ã¯': 'ï',
    'Ã‰': 'É',
    'ÃƒÂ': 'à',
    'ÃƒÂ¨': 'è',
    'ÃƒÂª': 'ê',
    'ÃƒÂ§': 'ç',
    'ÃƒÂ®': 'î',
    'ÃƒÂ´': 'ô',
    'ÃƒÂ¢': 'â',
    'ÃƒÂ‰': 'É',
    'AperÃ§u': 'Aperçu',
    'Âge': 'Âge', # Âge is actually Âge, but Âge mojibake is Ã¢ge
    'Ã¢ge': 'Âge',
    "ÃƒÆ’Ã†â€™Ãƒâ€\xa0Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¨re sportive en images ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â°ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¸ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â\xa0ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â\xa0": "ère sportive en images 📸",
    "ÃƒÆ’Ã†â€™Ãƒâ€\xa0Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©but d'une grande aventure ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â°ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¸ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¡ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬": "ébut d'une grande aventure 🚀",
}

files_to_fix = [
    'backend/app/infrastructure/sms_client.py',
    'backend/app/modules/athletes/router.py',
    'backend/app/modules/competitions/service.py',
    'backend/app/modules/payments/paydunya_client.py',
    'backend/app/modules/payments/service.py',
    'backend/app/modules/storage/router.py',
    'backend/app/modules/storage/service.py',
    'backend/app/modules/subscriptions/router.py',
    'backend/app/modules/subscriptions/service.py',
    'backend/app/workers/image_tasks.py',
    'backend/tests/conftest.py',
    'backend/tests/test_athletes_router.py',
    'backend/tests/test_competitions.py',
    'backend/worker_ai/app/main.py',
    'backend/worker_ai/app/worker.py',
    'frontend-client/src/pages/identity/EditIdentityPage.tsx',
]

for file_path in files_to_fix:
    full_path = os.path.join('e:/ZoPic Studio', file_path)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = content
        for bad, good in replacements.items():
            new_content = new_content.replace(bad, good)
            
        if new_content != content:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed encoding in {file_path}")
    else:
        print(f"File not found: {file_path}")

print("Done.")
