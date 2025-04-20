"""
PDF generator module for PaperShelf.

This module handles generating PDF files from chat history.
"""

import os
from datetime import datetime
from typing import List, Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def generate_chat_history_pdf(output_path: str, session_info: Dict[str, Any], history: List[Dict[str, Any]]) -> str:
    """
    Generate a PDF file containing chat history.

    Args:
        output_path: Path to save the PDF file
        session_info: Information about the session
        history: List of chat entries

    Returns:
        Path to the generated PDF file
    """
    # Create a unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_history_{session_info['session_id']}_{timestamp}.pdf"
    filepath = os.path.join(output_path, filename)
    
    # Create the PDF document
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    styles.add(ParagraphStyle(
        name='Title',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='Heading2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name='Normal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name='Query',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='Answer',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=10
    ))
    
    # Build the document content
    content = []
    
    # Add title
    content.append(Paragraph("PaperShelf Chat History", styles['Title']))
    content.append(Spacer(1, 12))
    
    # Add session info
    session_date = datetime.fromisoformat(session_info['created_at'].replace('Z', '+00:00'))
    formatted_date = session_date.strftime("%Y-%m-%d %H:%M:%S")
    
    content.append(Paragraph(f"Session ID: {session_info['session_id']}", styles['Normal']))
    content.append(Paragraph(f"Created: {formatted_date}", styles['Normal']))
    content.append(Paragraph(f"Number of queries: {session_info['query_count']}", styles['Normal']))
    content.append(Spacer(1, 20))
    
    # Add chat history
    if not history:
        content.append(Paragraph("No chat history found for this session.", styles['Normal']))
    else:
        for i, entry in enumerate(history):
            # Add query number
            content.append(Paragraph(f"Query {i+1}", styles['Heading2']))
            
            # Add query
            content.append(Paragraph(f"Q: {entry['query']}", styles['Query']))
            
            # Add answer
            content.append(Paragraph(f"A: {entry['answer']}", styles['Answer']))
            
            # Add retrieved documents
            if entry['retrieved_documents']:
                content.append(Paragraph("Retrieved Documents:", styles['Normal']))
                
                for j, doc in enumerate(entry['retrieved_documents']):
                    doc_text = doc.get('text', '')
                    if len(doc_text) > 200:
                        doc_text = doc_text[:200] + "..."
                    
                    metadata = doc.get('metadata', {})
                    title = metadata.get('title', 'Unknown')
                    
                    content.append(Paragraph(f"{j+1}. {title}: {doc_text}", styles['Normal']))
            
            content.append(Spacer(1, 15))
    
    # Build the PDF
    doc.build(content)
    
    return filepath