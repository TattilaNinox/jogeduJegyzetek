"""
PDF to Word konverter - lábjegyzetek és indexszámok eltávolításával
"""

import re
from pathlib import Path

# PyMuPDF a PDF olvasáshoz, python-docx a Word íráshoz
try:
    import fitz  # PyMuPDF
except ImportError:
    print("Telepítsd a PyMuPDF-et: pip install PyMuPDF")
    exit(1)

try:
    from docx import Document
    from docx.shared import Pt
except ImportError:
    print("Telepítsd a python-docx-et: pip install python-docx")
    exit(1)


def extract_text_without_footnotes(pdf_path: str) -> str:
    """
    Kinyeri a szöveget a PDF-ből, megőrizve az eredeti tagolást:
    - Lábjegyzetek eltávolítása (oldal alja)
    - Fejlécek eltávolítása (oldal teteje)
    - Oldalszámok eltávolítása
    - Felső indexszámok eltávolítása (lábjegyzet hivatkozások)
    - Eredeti bekezdések és tagolás megőrzése
    """
    doc = fitz.open(pdf_path)
    full_text = []
    
    for page_num, page in enumerate(doc):
        page_height = page.rect.height
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if "lines" not in block:
                continue
            
            block_bbox = block.get("bbox", [0, 0, 0, 0])
            block_y_top = block_bbox[1]
            
            # FEJLÉC kiszűrése (felső 10%)
            if block_y_top < page_height * 0.10:
                continue
            
            # LÁBLÉC/LÁBJEGYZETEK kiszűrése (alsó 15%)
            if block_y_top > page_height * 0.85:
                continue
            
            # Egy blokk sorait összegyűjtjük
            block_line_texts = []
            
            for line in block["lines"]:
                line_text = ""
                
                for span in line["spans"]:
                    text = span["text"]
                    font_size = span["size"]
                    flags = span["flags"]
                    
                    # Superscript számok kihagyása
                    is_superscript = (
                        font_size < 8 or 
                        (flags & 1) or
                        (text.strip().isdigit() and font_size < 10)
                    )
                    
                    if is_superscript and text.strip().isdigit():
                        continue
                    
                    line_text += text
                
                stripped = line_text.strip()
                
                # Oldalszámok kiszűrése
                if stripped.isdigit() and len(stripped) <= 3:
                    continue
                
                if stripped:
                    block_line_texts.append(stripped)
            
            if block_line_texts:
                # Blokk sorait SZÓKÖZZEL összekapcsoljuk (nem sortöréssel!)
                block_text = ' '.join(block_line_texts)
                full_text.append(block_text)
    
    doc.close()
    
    # Blokkok összekapcsolása bekezdésszünetekkel (dupla sortörés)
    result = "\n\n".join(full_text)
    
    return result


def clean_text(text: str) -> str:
    """
    További szövegtisztítás - maradék lábjegyzet számok és formázási problémák.
    """
    # Felső indexben lévő számok eltávolítása (Unicode superscript karakterek)
    superscript_digits = "⁰¹²³⁴⁵⁶⁷⁸⁹"
    for digit in superscript_digits:
        text = text.replace(digit, "")
    
    # "Lásd:" kezdetű teljes sor/mondat eltávolítása (általános minta)
    # Ez a minta a "Lásd:" után következő TELJES sort/mondatot eltávolítja
    text = re.sub(
        r'Lásd:[^\n.]*(?:\.[^\n]*)?(?=\n|$)',
        '',
        text,
        flags=re.IGNORECASE
    )
    
    # "Megállapította:", "Hatályos:", "Beiktatta:" stb. kezdetű módosítási megjegyzések
    text = re.sub(
        r'(?:Megállapította|Hatályos|Beiktatta|Módosította|Hatályon kívül helyezte):[^\n.]*(?:\.[^\n]*)?(?=\n|$)',
        '',
        text,
        flags=re.IGNORECASE
    )
    
    # Általánosabb minta: zárójelben lévő jogszabályi hivatkozások
    # Pl: "(2018. VI. 29-től.)" vagy hasonlók
    text = re.sub(
        r'\(\d{4}\.\s*[IVX]+\.\s*\d+-[a-zéáíóöőúüű]+\.\)',
        '',
        text,
        flags=re.IGNORECASE
    )
    
    # Szavak közepén lévő kis számok eltávolítása (pl. "szöveg1 további")
    # Ez a minta a szó végén lévő számokat távolítja el, ha nincs előtte szóköz
    text = re.sub(r'(?<=[a-záéíóöőúüű])(\d{1,3})(?=\s|[.,;:!?)]|$)', '', text, flags=re.IGNORECASE)
    
    # Önálló bekezdésszámok összekapcsolása a következő bekezdéssel
    # Pl: "(2)\n\nA szöveg..." -> "(2) A szöveg..."
    text = re.sub(r'\((\d+)\)\s*\n\n+', r'(\1) ', text)
    
    # Többszörös szóközök eltávolítása
    text = re.sub(r' +', ' ', text)
    
    # Többszörös sortörések csökkentése
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Üres bekezdések eltávolítása
    text = re.sub(r'\n\n\s*\n\n', '\n\n', text)
    
    return text.strip()


def create_word_document(text: str, output_path: str):
    """
    Word dokumentum létrehozása a tisztított szövegből, megőrizve az eredeti tagolást.
    """
    doc = Document()
    
    # Stílus beállítása
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)
    
    # Dupla sortörések mentén bekezdésekre bontás
    paragraphs = text.split('\n\n')
    
    for para in paragraphs:
        # A bekezdésen belüli sortöréseket szóközre cseréljük
        para_text = para.replace('\n', ' ')
        # Többszörös szóközök eltávolítása
        para_text = re.sub(r' +', ' ', para_text).strip()
        
        if para_text:
            doc.add_paragraph(para_text)
    
    doc.save(output_path)
    print(f"Word dokumentum elmentve: {output_path}")


def main():
    # Útvonalak
    script_dir = Path(__file__).parent
    pdf_path = script_dir / "PDF" / "Magyarország Alaptörvénye.pdf"
    output_path = script_dir / "word" / "Magyarország Alaptörvénye - tiszta.docx"
    
    if not pdf_path.exists():
        print(f"PDF nem található: {pdf_path}")
        return
    
    print(f"PDF feldolgozása: {pdf_path}")
    
    # Szöveg kinyerése lábjegyzetek nélkül
    print("Szöveg kinyerése...")
    raw_text = extract_text_without_footnotes(str(pdf_path))
    
    # Szöveg tisztítása
    print("Szöveg tisztítása...")
    clean = clean_text(raw_text)
    
    # Word dokumentum létrehozása
    print("Word dokumentum létrehozása...")
    create_word_document(clean, str(output_path))
    
    print("\nKész! A tisztított dokumentum itt található:")
    print(f"  {output_path}")


if __name__ == "__main__":
    main()
