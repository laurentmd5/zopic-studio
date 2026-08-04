import os
html = open('htmlcov/z_4ad5ec94a08151f4_router_py.html', encoding='utf-8').read()
for line in html.split('\n'):
    if 'class="mis show_mis"' in line:
        print(line)
