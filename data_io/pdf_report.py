from fpdf import FPDF
from typing import List
from core.models import Group
import os

class SimplePDFReport:
    def __init__(self, title: str = "تقرير المجموعات"):
        # Initialize the PDF report with a custom title (default is Arabic text "Group Report")

        self.title = title
    
    def groups_to_pdf(self, groups: List[Group], path: str):
        # Create a new PDF document with A4 format
        pdf = FPDF(format="A4")
        pdf.add_page()

        # Use simple Arial font to avoid issues
        pdf.set_font("Arial", size=12)
        
        # Add the report title at the center of the page
        pdf.cell(0, 10, "Carpet Groups Report", ln=True, align='C')
        pdf.ln(4)  # Add some vertical space after the title

        # Set the default font for the content
        pdf.set_font("Arial", size=10)

        # Loop through each group and write its details
        for g in groups:
            # Print group header in bold: group id, total width, and reference length
            pdf.set_font("Arial", style='B', size=11)
            group_text = f"Group {g.id} - Width: {g.total_width()} - Length: {g.ref_length()}"
            pdf.cell(0, 8, group_text, ln=True)

            # Switch back to normal font for listing items inside the group
            pdf.set_font("Arial", size=9)
            
            for it in g.items:
                # Each line describes one used carpet item
                # Use very short text to avoid spacing issues
                line = f"ID:{it.rect_id} W:{it.width} L:{it.length} Q:{it.used_qty}"
                # Use cell instead of multi_cell to avoid spacing issues
                pdf.cell(0, 5, line, ln=True)

            pdf.ln(2)  # Small vertical space between groups

        # Finally, save the PDF file to the given path
        pdf.output(path)