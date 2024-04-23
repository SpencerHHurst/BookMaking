from docx import Document
from bs4 import BeautifulSoup
import requests
from docx.shared import Pt

# Initialize and configure the Word document
doc = Document()
styles = doc.styles
heading_style = styles['Heading 1']
heading_style.font.size = Pt(28)

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

# Scrape chapters

link = ["https://practicalguidetoevil.wordpress.com/2015/03/25/prologue/"]
for url in links:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Add chapter title
    title = soup.find('h1', class_='entry-title').get_text(strip=True)
    doc.add_heading(title, level=1)

    # Extract and format the content
    content_div = soup.find('div', class_='entry-content')
    paragraphs = content_div.find_all('p')

    for p in paragraphs:
        # Initialize a new paragraph in the document
        paragraph = doc.add_paragraph()
        # Process the children of the paragraph element
        for elem in p.children:
            if isinstance(elem, str):
                # Add normal text
                paragraph.add_run(elem)
            elif elem.name in ['i', 'em']:
                # Add italicized text for content within <i> tags
                paragraph.add_run(elem.get_text()).italic = True
            elif elem.name == 'span':
                # Process the content within <span> tags
                for child in elem.children:
                    if isinstance(child, str):
                        # Add normal text
                        paragraph.add_run(child)
                    elif child.name in ['i', 'em']:
                        # Add italicized text for content within <i> tags
                        paragraph.add_run(child.get_text()).italic = True

    # Add a page break after each chapter
    doc.add_page_break()

# Save the document
doc.save('Novel.docx')
