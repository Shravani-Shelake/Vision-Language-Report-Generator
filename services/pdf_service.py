from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from typing import Dict, Any
from io import BytesIO
from datetime import datetime

class PDFService:
    @staticmethod
    def generate_report_pdf(report_data: Dict[str, Any], report_id: str) -> BytesIO:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph("Business Analytics Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Report info
        info_text = f"Report ID: {report_id}<br/>Generated: {report_data.get('generated_at', 'N/A')}"
        story.append(Paragraph(info_text, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        summary = report_data.get('summary', 'No summary available')
        story.append(Paragraph(summary, styles['BodyText']))
        story.append(Spacer(1, 0.2*inch))
        
        # Key Metrics
        if report_data.get('key_metrics'):
            story.append(Paragraph("Key Metrics", heading_style))
            
            # Create table for metrics
            metrics_data = [['Metric', 'Value', 'Unit']]
            for metric in report_data['key_metrics']:
                metrics_data.append([
                    metric.get('name', 'N/A'),
                    str(metric.get('value', 'N/A')),
                    metric.get('unit', '-')
                ])
            
            metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch, 1.5*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(metrics_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Trends
        if report_data.get('trends'):
            story.append(Paragraph("Trends Analysis", heading_style))
            for idx, trend in enumerate(report_data['trends']):
                trend_text = f"<b>{idx+1}. {trend.get('description', 'N/A')}</b><br/>"
                trend_text += f"Direction: {trend.get('direction', 'N/A')} | "
                trend_text += f"Impact: {trend.get('impact', 'N/A')}"
                story.append(Paragraph(trend_text, styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            story.append(Spacer(1, 0.1*inch))
        
        # Correlations
        if report_data.get('correlations'):
            story.append(Paragraph("Key Correlations", heading_style))
            for idx, correlation in enumerate(report_data['correlations']):
                story.append(Paragraph(f"• {correlation}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Recommendations
        if report_data.get('recommendations'):
            story.append(Paragraph("Recommendations", heading_style))
            for idx, rec in enumerate(report_data['recommendations']):
                rec_text = f"<b>{idx+1}. [{rec.get('priority', 'N/A').upper()}] {rec.get('action', 'N/A')}</b><br/>"
                rec_text += f"{rec.get('rationale', 'N/A')}"
                story.append(Paragraph(rec_text, styles['Normal']))
                story.append(Spacer(1, 0.15*inch))
        
        # Visual Insights
        if report_data.get('visual_insights'):
            story.append(PageBreak())
            story.append(Paragraph("Visual Insights", heading_style))
            for idx, insight in enumerate(report_data['visual_insights']):
                story.append(Paragraph(f"• {insight}", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
