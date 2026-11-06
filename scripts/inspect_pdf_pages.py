import re

with open('scripts/build_full_38page_pdf.py', 'r', encoding='utf-8') as f:
    text = f.read()

pages = text.split('PageBreak()')
print(f'Total pages delimited by PageBreak: {len(pages)}')
for idx, page in enumerate(pages):
    figs = re.findall(r'img_fit\((?:filename=)?["\']([^"\']+)["\']', page)
    titles = re.findall(r'Paragraph\(["\']([^"\']+)["\'], styles\[["\'](?:SectionHeading|TitleStyle|SubSectionHeading)["\']\]', page)
    t = titles[0] if titles else 'Page content'
    print(f'Page {idx+1:02d}: {t[:45]} | Figs: {figs}')
