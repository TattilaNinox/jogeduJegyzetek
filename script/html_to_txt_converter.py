#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML to TXT Converter
Konvertálja a HTML tételeket vissza .txt fájlokká
"""

import os
import re
from pathlib import Path

def html_to_markdown(html_content):
    """Konvertálja a HTML tartalmat Markdown formátumra"""
    
    # Kivonjuk a body tartalmát
    body_match = re.search(r'<body>(.*?)</body>', html_content, re.DOTALL)
    if not body_match:
        return ""
    
    content = body_match.group(1)
    
    # Eltávolítjuk a felesleges whitespace-t
    content = re.sub(r'\s+', ' ', content)
    
    # H1 címek
    content = re.sub(r'<h1>(.*?)</h1>', r'# \1\n', content)
    
    # H2 címek
    content = re.sub(r'<h2>(.*?)</h2>', r'\n## \1\n', content)
    
    # H3 címek
    content = re.sub(r'<h3>(.*?)</h3>', r'\n### \1\n', content)
    
    # H4 címek
    content = re.sub(r'<h4>(.*?)</h4>', r'\n#### \1\n', content)
    
    # Felsorolások (ul)
    # Először kezeljük a teljes ul blokkokat
    def process_ul(match):
        ul_content = match.group(1)
        items = re.findall(r'<li>(.*?)</li>', ul_content, re.DOTALL)
        result = '\n'
        for item in items:
            item = re.sub(r'<strong>(.*?)</strong>', r'**\1**', item)
            item = re.sub(r'<.*?>', '', item)
            item = item.strip()
            if item:
                result += f'- {item}\n'
        return result + '\n'
    
    content = re.sub(r'<ul>(.*?)</ul>', process_ul, content, flags=re.DOTALL)
    
    # Számozott listák (ol)
    def process_ol(match):
        ol_content = match.group(1)
        items = re.findall(r'<li>(.*?)</li>', ol_content, re.DOTALL)
        result = '\n'
        for idx, item in enumerate(items, 1):
            item = re.sub(r'<strong>(.*?)</strong>', r'**\1**', item)
            item = re.sub(r'<.*?>', '', item)
            item = item.strip()
            if item:
                result += f'{idx}. {item}\n'
        return result + '\n'
    
    content = re.sub(r'<ol>(.*?)</ol>', process_ol, content, flags=re.DOTALL)
    
    # Paragraph-ok
    content = re.sub(r'<p>(.*?)</p>', r'\1\n\n', content, flags=re.DOTALL)
    
    # Bold (strong)
    content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', content)
    
    # Táblázatok - egyszerű szöveggé alakítjuk
    def process_table(match):
        table_content = match.group(1)
        # Kivonjuk a sorokat
        rows = re.findall(r'<tr>(.*?)</tr>', table_content, re.DOTALL)
        result = '\n'
        for row in rows:
            cells = re.findall(r'<t[dh]>(.*?)</t[dh]>', row, re.DOTALL)
            if cells:
                row_text = ' | '.join([re.sub(r'<.*?>', '', cell).strip() for cell in cells])
                result += f'{row_text}\n'
        return result + '\n'
    
    content = re.sub(r'<table>(.*?)</table>', process_table, content, flags=re.DOTALL)
    
    # Eltávolítjuk az összes maradék HTML címkét
    content = re.sub(r'<[^>]+>', '', content)
    
    # HTML entitások dekódolása
    content = content.replace('&nbsp;', ' ')
    content = content.replace('&amp;', '&')
    content = content.replace('&lt;', '<')
    content = content.replace('&gt;', '>')
    content = content.replace('&quot;', '"')
    content = content.replace('&#39;', "'")
    
    # Tisztítjuk a szöveget
    # Többszörös üres sorok egyesítése
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Szóközök tisztítása
    content = re.sub(r' +', ' ', content)
    
    # Sorok végének tisztítása
    lines = content.split('\n')
    cleaned_lines = [line.rstrip() for line in lines]
    content = '\n'.join(cleaned_lines)
    
    return content.strip()

def convert_html_files():
    """Konvertálja az összes HTML fájlt TXT fájlokká"""
    
    # Abszolút útvonalak használata
    base_dir = Path(__file__).parent.parent
    html_dir = base_dir / 'Tételek' / 'html_tetelek'
    output_dir = base_dir / 'Tételek'
    
    if not html_dir.exists():
        print(f"Hiba: A {html_dir} mappa nem található!")
        return
    
    html_files = list(html_dir.glob('*.html'))
    
    if not html_files:
        print("Nincs HTML fájl a mappában!")
        return
    
    converted_count = 0
    
    for html_file in html_files:
        try:
            # Beolvassuk a HTML fájlt
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Konvertáljuk Markdown-ra
            markdown_content = html_to_markdown(html_content)
            
            if not markdown_content:
                print(f"Figyelmeztetés: {html_file.name} üres tartalmat adott!")
                continue
            
            # Létrehozzuk a TXT fájl nevét
            txt_filename = html_file.stem + '.txt'
            txt_path = output_dir / txt_filename
            
            # Menti a TXT fájlt
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"✓ Konvertálva: {html_file.name} -> {txt_filename}")
            converted_count += 1
            
        except Exception as e:
            print(f"✗ Hiba a {html_file.name} feldolgozásakor: {e}")
    
    print(f"\nÖsszesen {converted_count} fájl konvertálva.")

if __name__ == '__main__':
    convert_html_files()

