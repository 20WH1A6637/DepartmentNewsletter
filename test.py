from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import sqlite3
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# Initialize the PDF document
def create_pdf(semester_id, content):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Set the title for the semester
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title = Paragraph(f"<u>Semester ID: {semester_id}</u>", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2 * inch))
    
    # Loop through content and add titles, content, and images
    for row in content:
        title = row[4]
        content_text = row[5]
        content_text = content_text.replace("<br>", " ")  # Replace with space

        
        # Add title
        title_style = styles['Heading2']
        title_paragraph = Paragraph(title, title_style)
        elements.append(title_paragraph)
        
        # Add content
        content_style = styles['Normal']
        content_paragraph = Paragraph(content_text, content_style)
        elements.append(content_paragraph)

        # Add image if available
        image_filename = row[6]
        if image_filename:
            image_path = f"static/uploads/{image_filename}"  # Update with the correct path
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(Image(image_path, width=300, height=200))
        
        elements.append(Spacer(1, 0.2 * inch))

    # Build the PDF
    doc.build(elements)
    return buffer.getvalue()

# Define your database connection and query here
DATABASE = 'content.db'

# Create a function to fetch data for a specific semester
def fetch_semester_data(semester_id):
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM content WHERE semester_id = ? ORDER BY selected_page', (semester_id,))
    content = cursor.fetchall()
    db.close()
    return content

# Define the semesters
semesters = ["22-1-2", "22-2-1", "22-2-2", "23-3-1"]

# Generate PDFs for each semester
for semester_id in semesters:
    content = fetch_semester_data(semester_id)
    if content:
        pdf_data = create_pdf(semester_id, content)
        with open(f"{semester_id}_content.pdf", "wb") as pdf_file:
            pdf_file.write(pdf_data)

