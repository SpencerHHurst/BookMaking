from bs4 import BeautifulSoup
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register the Garamond font
pdfmetrics.registerFont(TTFont('Garamond', 'EB_Garamond/static/EBGaramond-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Garamond-Italic', 'EB_Garamond/static/EBGaramond-Italic.ttf'))

# Fetch table of contents
url = 'https://practicalguidetoevil.wordpress.com/table-of-contents/'
response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.text, 'html.parser')

# Find and process book links
book_1_header = soup.find('h2', text="Book 1")
if book_1_header:
    book_1_links = book_1_header.find_next('ul').find_all('a')
    links = [link['href'] for link in book_1_links if link.get('href')]
    for link in links:
        print(link)
else:
    print("Book 1 section not found.")

# Create a new PDF document
doc = SimpleDocTemplate("Novel.pdf", pagesize=letter)

# Define custom styles
styles = getSampleStyleSheet()
styles['Heading1'].fontName = 'Garamond'
styles['Heading1'].fontSize = 24
styles['Heading1'].leading = 26
styles['Heading1'].spaceAfter = 12

styles.add(ParagraphStyle(name='FirstParagraph', fontName='Garamond', fontSize=14, leading=18, spaceAfter=12))

styles['Normal'].fontName = 'Garamond'
styles['Normal'].fontSize = 12
styles['Normal'].leading = 14
styles['Normal'].spaceAfter = 8

styles['Italic'].fontName = 'Garamond-Italic'
styles['Italic'].fontSize = 12
styles['Italic'].leading = 14
styles['Italic'].spaceAfter = 8

# Custom function to add page numbers
def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('Garamond', 10)
    page_number_text = "%d" % doc.page
    canvas.drawCentredString(4.25 * inch, 0.5 * inch, page_number_text)
    canvas.restoreState()

# Scrape chapters and add content to the PDF
story = []
for url in links:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Add chapter title
    title = soup.find('h1', class_='entry-title').get_text(strip=True)
    story.append(Paragraph(title, styles['Heading1']))

    # Extract and format the content
    content_div = soup.find('div', class_='entry-content')
    paragraphs = content_div.find_all('p')
    for i, p in enumerate(paragraphs):
        # Process the children of the paragraph element
        paragraph_text = ""
        for elem in p.children:
            if isinstance(elem, str):
                # Add normal text
                paragraph_text += elem.replace('&', '&')
            elif elem.name in ['i', 'em']:
                # Add italicized text for content within <i> tags
                paragraph_text += f"<i>{elem.get_text().replace('&', '&')}</i>"
            elif elem.name == 'span':
                # Process the content within <span> tags
                for child in elem.children:
                    if isinstance(child, str):
                        # Add normal text
                        paragraph_text += child.replace('&', '&')
                    elif child.name in ['i', 'em']:
                        # Add italicized text for content within <i> tags
                        paragraph_text += f"<i>{child.get_text().replace('&', '&')}</i>"

        # Apply the appropriate style to the paragraph
        if url != "https://practicalguidetoevil.wordpress.com/2015/03/25/prologue/":
            if i == 0:
                story.append(Paragraph(paragraph_text, styles['FirstParagraph']))
            else:
                story.append(Paragraph(paragraph_text, styles['Normal']))
        else:
            story.append(Paragraph(paragraph_text, styles['Normal']))

        story.append(Spacer(1, 12))

    story.append(PageBreak())  # Add a new page after each chapter

# Build the PDF document
doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
print("PDF generated successfully.")