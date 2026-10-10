from pypdf import PdfReader

p = r'C:/Users/ASHISH S YADAV.LAPTOP-LEK06VOJ/Downloads/task.pdf'
reader = PdfReader(p)
text = '\n'.join(page.extract_text() or '' for page in reader.pages)
out = r'C:/Users/ASHISH S YADAV.LAPTOP-LEK06VOJ/OneDrive/Desktop/kanishka/task_extracted.txt'
with open(out, 'w', encoding='utf-8') as f:
    f.write(text)
print('WROTE', out)
