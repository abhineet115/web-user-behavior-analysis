import zipfile
import xml.etree.ElementTree as ET
import re
import os
import sys

def read_pptx(filename):
    print("==================================================")
    print(f"PPTX: {filename}")
    print("==================================================")
    if not os.path.exists(filename):
        print("File not found")
        return
    with zipfile.ZipFile(filename, 'r') as z:
        slides = [s for s in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml', s)]
        slides.sort(key=lambda s: int(re.search(r'\d+', s).group()))
        for s in slides:
            slide_num = re.search(r'\d+', s).group()
            tree = ET.fromstring(z.read(s))
            texts = [elem.text for elem in tree.iter() if elem.text]
            clean_text = ' '.join(' '.join(texts).split())
            print(f"\n--- SLIDE {slide_num} ---")
            print(clean_text)

def read_pdf(filename):
    print("\n==================================================")
    print(f"PDF: {filename}")
    print("==================================================")
    if not os.path.exists(filename):
        print("File not found")
        return
    
    # Try multiple pdf reading options
    read_success = False
    
    # Try pypdf / pypdf2 / pdfminer / fitz
    for mod in ['pypdf', 'PyPDF2', 'fitz', 'pdfplumber']:
        try:
            m = __import__(mod)
            print(f"Reading PDF with {mod}...")
            if mod in ['pypdf', 'PyPDF2']:
                reader = m.PdfReader(filename)
                print(f"Total Pages: {len(reader.pages)}")
                for i, page in enumerate(reader.pages):
                    print(f"\n--- PDF PAGE {i+1} ---")
                    print(page.extract_text())
                read_success = True
                break
            elif mod == 'fitz':
                doc = m.open(filename)
                print(f"Total Pages: {len(doc)}")
                for i, page in enumerate(doc):
                    print(f"\n--- PDF PAGE {i+1} ---")
                    print(page.get_text())
                read_success = True
                break
        except Exception as e:
            continue
            
    if not read_success:
        # Fallback: extract basic strings/streams if no library
        print("No standard PDF library found. Searching for text streams in PDF...")
        try:
            with open(filename, 'rb') as f:
                content = f.read().decode('latin1', errors='ignore')
                # Find title or outline
                matches = re.findall(r'\(([^\(\)]{4,100})\)\s*Tj', content)
                if matches:
                    print(f"Extracted {len(matches)} text snippets from PDF:")
                    print('\n'.join(matches[:100]))
                else:
                    print("Could not parse raw PDF stream without a PDF library.")
        except Exception as e:
            print("Error reading raw pdf:", e)

if __name__ == '__main__':
    with open('project_docs_summary.txt', 'w', encoding='utf-8') as out:
        sys.stdout = out
        read_pptx('Web_User_Behaviour_Analysis_Final_Presentation.pptx')
        read_pdf('final2.pdf')
