#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML generáló szkript a Tételek mappában lévő kidolgozott tételek HTML formátumba konvertálásához
Használat: python tetelek_html_generator.py [mappa_utvonal]
Példa: python tetelek_html_generator.py "Tételek"
"""

import re
import os
import sys

def get_html_template():
    """HTML template CSS stílusokkal"""
    return """<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-size: 13px;
            line-height: 1.6;
            text-align: justify;
            hyphens: auto;
            padding: 2em;
            word-wrap: break-word;
        }}
        h1 {{
            font-size: 1.4em;
            text-align: left;
        }}
        h2 {{
            font-size: 1.3em;
            border-bottom: 1px solid #ccc;
            padding-bottom: 5px;
            margin-top: 1.5em;
        }}
        h3 {{
            font-size: 1.1em;
            margin-top: 1.2em;
        }}
        h4 {{
            font-size: 1.0em;
            color: #333;
            margin-top: 1.0em;
        }}
        p {{
            margin-bottom: 1em;
        }}
        ul, ol {{
            padding-left: 20px;
            margin-bottom: 1em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1em;
        }}
        th, td {{
            padding: 10px;
            border: 1px solid #ddd;
            text-align: left;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #e6f3ff;
        }}
        @media screen and (max-width: 768px) {{
            body {{
                padding: 1em;
            }}
            table {{
                overflow-x: auto;
                display: block;
            }}
        }}
        .szin-piros {{
            color: #D32F2F;
            font-weight: bold;
        }}
        .szin-zold {{
            color: #388E3C;
        }}
        .szin-kek {{
            color: #1976D2;
        }}
        .hatter-sarga {{
            background-color: #FFF59D;
            padding: 0.1em 0.3em;
            border-radius: 3px;
        }}
        strong {{
            font-weight: bold;
        }}
    </style>
</head>
<body>
{content}
</body>
</html>"""

def fajlnev_to_title(fajlnev):
    """Fájlnévből HTML title generálása"""
    # Kiterjesztés eltávolítása
    title = os.path.splitext(fajlnev)[0]
    # Aláhúzások szóközökké
    title = title.replace('_', ' ')
    # Első betűk nagybetűvé
    title = title.title()
    return title

def markdown_to_html(szoveg):
    """Markdown formázást HTML-re konvertál"""
    # Először az ÖSSZES * karaktert eltávolítjuk (biztonsági tisztítás)
    # De előbb a **bold** formázást kezeljük
    szoveg = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', szoveg)
    
    # Most már eltávolíthatjuk az összes maradék * karaktert
    szoveg = szoveg.replace('*', '')
    
    sorok = szoveg.split('\n')
    html_sorok = []
    aktualis_paragrafus = []
    aktualis_lista = []
    
    i = 0
    while i < len(sorok):
        sor = sorok[i].rstrip()
        
        # Üres sor kezelése
        if not sor.strip():
            # Ha van folyamatban lévő lista, zárjuk le
            if aktualis_lista:
                html_sorok.append('<ul>')
                html_sorok.extend(aktualis_lista)
                html_sorok.append('</ul>')
                aktualis_lista = []
            
            # Ha van folyamatban lévő paragrafus, zárjuk le
            if aktualis_paragrafus:
                paragrafus_szoveg = ' '.join(aktualis_paragrafus)
                if paragrafus_szoveg.strip():
                    html_sorok.append(f'<p>{paragrafus_szoveg}</p>')
                aktualis_paragrafus = []
            
            html_sorok.append('')
            i += 1
            continue
        
        # Címsorok kezelése (először a több #-os formátumokat)
        if re.match(r'^####\s+', sor):
            if aktualis_paragrafus or aktualis_lista:
                if aktualis_lista:
                    html_sorok.append('<ul>')
                    html_sorok.extend(aktualis_lista)
                    html_sorok.append('</ul>')
                    aktualis_lista = []
                if aktualis_paragrafus:
                    html_sorok.append(f'<p>{" ".join(aktualis_paragrafus)}</p>')
                    aktualis_paragrafus = []
            cim = re.sub(r'^####\s+', '', sor)
            html_sorok.append(f'<h4>{cim}</h4>')
            i += 1
            continue
        elif re.match(r'^###\s+', sor):
            if aktualis_paragrafus or aktualis_lista:
                if aktualis_lista:
                    html_sorok.append('<ul>')
                    html_sorok.extend(aktualis_lista)
                    html_sorok.append('</ul>')
                    aktualis_lista = []
                if aktualis_paragrafus:
                    html_sorok.append(f'<p>{" ".join(aktualis_paragrafus)}</p>')
                    aktualis_paragrafus = []
            cim = re.sub(r'^###\s+', '', sor)
            html_sorok.append(f'<h3>{cim}</h3>')
            i += 1
            continue
        elif re.match(r'^##\s+', sor):
            if aktualis_paragrafus or aktualis_lista:
                if aktualis_lista:
                    html_sorok.append('<ul>')
                    html_sorok.extend(aktualis_lista)
                    html_sorok.append('</ul>')
                    aktualis_lista = []
                if aktualis_paragrafus:
                    html_sorok.append(f'<p>{" ".join(aktualis_paragrafus)}</p>')
                    aktualis_paragrafus = []
            cim = re.sub(r'^##\s+', '', sor)
            html_sorok.append(f'<h2>{cim}</h2>')
            i += 1
            continue
        elif re.match(r'^#\s+', sor):
            if aktualis_paragrafus or aktualis_lista:
                if aktualis_lista:
                    html_sorok.append('<ul>')
                    html_sorok.extend(aktualis_lista)
                    html_sorok.append('</ul>')
                    aktualis_lista = []
                if aktualis_paragrafus:
                    html_sorok.append(f'<p>{" ".join(aktualis_paragrafus)}</p>')
                    aktualis_paragrafus = []
            cim = re.sub(r'^#\s+', '', sor)
            html_sorok.append(f'<h1>{cim}</h1>')
            i += 1
            continue
        
        # Római számos fejezetek (I., II., III., stb.) → <h2>
        if re.match(r'^(I{1,3}|IV|V|VI{0,3}|IX|X{0,3})\.\s+', sor):
            if aktualis_paragrafus or aktualis_lista:
                if aktualis_lista:
                    html_sorok.append('<ul>')
                    html_sorok.extend(aktualis_lista)
                    html_sorok.append('</ul>')
                    aktualis_lista = []
                if aktualis_paragrafus:
                    html_sorok.append(f'<p>{" ".join(aktualis_paragrafus)}</p>')
                    aktualis_paragrafus = []
            cim = re.sub(r'^(I{1,3}|IV|V|VI{0,3}|IX|X{0,3})\.\s+', '', sor)
            html_sorok.append(f'<h2>{cim}</h2>')
            i += 1
            continue
        
        # Betűvel jelölt alcímek (A., B., C., stb.) → <h3>
        # De csak ha a következő sor nem üres és nem lista
        if re.match(r'^([A-Z])\.\s+', sor):
            # Ellenőrizzük, hogy nem lista elem-e (pl. "A. pont" vs "a) pont")
            if i + 1 < len(sorok) and sorok[i + 1].strip():
                kovetkezo = sorok[i + 1].strip()
                # Ha a következő sor lista vagy paragrafus, akkor ez alcím
                if not re.match(r'^[-•]|^[a-z]\)|^\d+\)', kovetkezo):
                    if aktualis_paragrafus or aktualis_lista:
                        if aktualis_lista:
                            html_sorok.append('<ul>')
                            html_sorok.extend(aktualis_lista)
                            html_sorok.append('</ul>')
                            aktualis_lista = []
                        if aktualis_paragrafus:
                            html_sorok.append(f'<p>{" ".join(aktualis_paragrafus)}</p>')
                            aktualis_paragrafus = []
                    cim = re.sub(r'^([A-Z])\.\s+', '', sor)
                    html_sorok.append(f'<h3>{cim}</h3>')
                    i += 1
                    continue
        
        # Számozott alcímek (1., 2., 3., stb.) → <h4>
        # De csak ha az előző sor üres vagy cím, és nem lista elem
        if re.match(r'^(\d+)\.\s+', sor):
            # Ellenőrizzük, hogy nem lista elem-e (pl. "- 1. pont")
            # Csak akkor alcím, ha az előző sor üres vagy cím volt
            elozo_ures_vagy_cim = (i == 0 or not sorok[i-1].strip() or 
                                   re.match(r'^(I{1,3}|IV|V|VI{0,3}|IX|X{0,3})\.\s+|^([A-Z])\.\s+|^#+\s+', sorok[i-1]))
            if elozo_ures_vagy_cim:
                if aktualis_paragrafus or aktualis_lista:
                    if aktualis_lista:
                        html_sorok.append('<ul>')
                        html_sorok.extend(aktualis_lista)
                        html_sorok.append('</ul>')
                        aktualis_lista = []
                    if aktualis_paragrafus:
                        html_sorok.append(f'<p>{" ".join(aktualis_paragrafus)}</p>')
                        aktualis_paragrafus = []
                cim = re.sub(r'^(\d+)\.\s+', '', sor)
                html_sorok.append(f'<h4>{cim}</h4>')
                i += 1
                continue
        
        # Felsorolások kezelése
        # Listajeles felsorolások: - vagy •
        if re.match(r'^[-•]\s+', sor):
            # Ha új lista kezdődik, zárjuk le az előző paragrafust
            if aktualis_paragrafus:
                html_sorok.append(f'<p>{" ".join(aktualis_paragrafus)}</p>')
                aktualis_paragrafus = []
            
            lista_elem = re.sub(r'^[-•]\s+', '', sor)
            aktualis_lista.append(f'<li>{lista_elem}</li>')
            i += 1
            continue
        
        # Számozott listák: a) b) c) vagy 1) 2) 3)
        if re.match(r'^([a-z])\)\s+', sor):
            if aktualis_paragrafus:
                html_sorok.append(f'<p>{" ".join(aktualis_paragrafus)}</p>')
                aktualis_paragrafus = []
            
            lista_elem = re.sub(r'^([a-z])\)\s+', '', sor)
            aktualis_lista.append(f'<li>{lista_elem}</li>')
            i += 1
            continue
        
        if re.match(r'^(\d+)\)\s+', sor):
            if aktualis_paragrafus:
                html_sorok.append(f'<p>{" ".join(aktualis_paragrafus)}</p>')
                aktualis_paragrafus = []
            
            lista_elem = re.sub(r'^(\d+)\)\s+', '', sor)
            aktualis_lista.append(f'<li>{lista_elem}</li>')
            i += 1
            continue
        
        # Normál szöveg sor
        # Ha van folyamatban lévő lista, zárjuk le
        if aktualis_lista:
            html_sorok.append('<ul>')
            html_sorok.extend(aktualis_lista)
            html_sorok.append('</ul>')
            aktualis_lista = []
        
        aktualis_paragrafus.append(sor)
        i += 1
    
    # Utolsó lista és paragrafus kezelése
    if aktualis_lista:
        html_sorok.append('<ul>')
        html_sorok.extend(aktualis_lista)
        html_sorok.append('</ul>')
    
    if aktualis_paragrafus:
        paragrafus_szoveg = ' '.join(aktualis_paragrafus)
        if paragrafus_szoveg.strip():
            html_sorok.append(f'<p>{paragrafus_szoveg}</p>')
    
    html = '\n'.join(html_sorok)
    
    # Többszörös üres sorok eltávolítása
    html = re.sub(r'\n{3,}', '\n\n', html)
    
    # Üres <p></p> tag-ek eltávolítása
    html = re.sub(r'<p>\s*</p>', '', html)
    
    return html.strip()

def feldolgoz_fajl(fajl_utvonal):
    """Egy fájl feldolgozása és HTML-re konvertálása"""
    print(f"Feldolgozás: {fajl_utvonal}")
    
    # Fájl beolvasása
    with open(fajl_utvonal, 'r', encoding='utf-8') as f:
        tartalom = f.read()
    
    # Főcím kinyerése (első sor, ha nagybetűs)
    sorok = tartalom.strip().split('\n')
    if sorok and sorok[0].strip().isupper() and len(sorok[0].strip()) > 10:
        # Főcím az első sor
        fo_cim = sorok[0].strip()
        # A többi sor a tartalom
        tartalom = '\n'.join(sorok[1:]).strip()
    else:
        # Nincs külön főcím, a fájlnévből generáljuk
        fo_cim = None
    
    # Markdown → HTML konverzió
    html_tartalom = markdown_to_html(tartalom)
    
    # Főcím hozzáadása ha van
    if fo_cim:
        html_tartalom = f'<h1>{fo_cim}</h1>\n\n{html_tartalom}'
    
    return html_tartalom

def main():
    """Fő függvény"""
    # Parancssori argumentumok kezelése
    if len(sys.argv) > 1:
        bemenet = sys.argv[1]
    else:
        # Alapértelmezett: Tételek mappa (a script mappájához képest)
        script_mappa = os.path.dirname(os.path.abspath(__file__))
        bemenet = os.path.join(os.path.dirname(script_mappa), 'Tételek')
    
    # Normalizáljuk az útvonalat
    bemenet = os.path.abspath(bemenet)
    
    # Ellenőrizzük, hogy fájl vagy mappa
    fajlok = []
    if os.path.isfile(bemenet):
        # Egy fájl
        if bemenet.endswith('.txt'):
            fajlok.append(bemenet)
        else:
            print(f"Figyelem: A megadott fájl nem .txt kiterjesztésű: {bemenet}")
            return
    elif os.path.isdir(bemenet):
        # Mappa: minden .txt fájlt feldolgozunk
        for fajl in os.listdir(bemenet):
            if fajl.endswith('.txt'):
                fajlok.append(os.path.join(bemenet, fajl))
    else:
        print(f"Hiba: A megadott útvonal nem létezik: {bemenet}")
        return
    
    if not fajlok:
        print(f"Figyelem: Nem található .txt fájl a megadott útvonalon: {bemenet}")
        return
    
    print(f"HTML generálás indítása...")
    print(f"Talált fájlok száma: {len(fajlok)}")
    
    # Kimeneti mappa létrehozása
    if os.path.isfile(bemenet):
        # Ha fájl volt a bemenet, a fájl mappájába megy a kimenet
        kimenet_mappa = os.path.join(os.path.dirname(bemenet), 'html_tetelek')
    else:
        # Ha mappa volt a bemenet, abba a mappába megy a kimenet
        kimenet_mappa = os.path.join(bemenet, 'html_tetelek')
    
    os.makedirs(kimenet_mappa, exist_ok=True)
    
    # HTML template
    html_template = get_html_template()
    
    # Minden fájl feldolgozása
    sikeres = 0
    for fajl_utvonal in fajlok:
        try:
            html_tartalom = feldolgoz_fajl(fajl_utvonal)
            
            # Fájlnév és title generálása
            fajl_nev = os.path.basename(fajl_utvonal)
            html_fajl_nev = os.path.splitext(fajl_nev)[0] + '.html'
            title = fajlnev_to_title(fajl_nev)
            
            # HTML generálása
            html = html_template.format(title=title, content=html_tartalom)
            
            # Fájl írása
            kimenet_fajl_utvonal = os.path.join(kimenet_mappa, html_fajl_nev)
            with open(kimenet_fajl_utvonal, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"  ✓ {fajl_nev} -> {html_fajl_nev}")
            sikeres += 1
        except Exception as e:
            print(f"  ✗ {os.path.basename(fajl_utvonal)}: {str(e)}")
    
    print(f"\nHTML generálás kész! {sikeres} fájl konvertálva.")
    print(f"Kimeneti mappa: {kimenet_mappa}")

if __name__ == '__main__':
    main()


