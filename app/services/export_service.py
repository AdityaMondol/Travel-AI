from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json
from app.core.logger import setup_logger
from app.core.file_manager import FileManager

logger = setup_logger(__name__)

class ExportService:
    """Handle export of travel guides in multiple formats"""
    
    @staticmethod
    def export_json(data: Dict[str, Any], destination: str) -> Optional[str]:
        """Export as JSON"""
        try:
            filename = f"output/{destination.lower().replace(' ', '_')}_guide_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            return filename if FileManager.save_json(data, filename) else None
        except Exception as e:
            logger.error(f"JSON export error: {e}")
            return None
    
    @staticmethod
    def export_markdown(data: Dict[str, Any], destination: str) -> Optional[str]:
        """Export as Markdown"""
        try:
            md_content = ExportService._generate_markdown(data, destination)
            filename = f"output/{destination.lower().replace(' ', '_')}_guide_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            return filename if FileManager.save_markdown(md_content, filename) else None
        except Exception as e:
            logger.error(f"Markdown export error: {e}")
            return None
    
    @staticmethod
    def _generate_markdown(data: Dict[str, Any], destination: str) -> str:
        """Generate markdown content"""
        md = f"# Travel Guide: {destination}\n\n"
        md += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if "places" in data:
            md += "## Top Places\n\n"
            for place in data.get("places", {}).get("places", [])[:5]:
                md += f"- **{place.get('name', 'Unknown')}**: {place.get('description', '')}\n"
            md += "\n"
        
        if "itinerary" in data:
            md += "## 3-Day Itinerary\n\n"
            for day in data.get("itinerary", {}).get("three_days", []):
                md += f"### Day {day.get('day', 1)}\n"
                for activity in day.get("activities", []):
                    md += f"- {activity}\n"
                md += "\n"
        
        if "food" in data:
            md += "## Must-Try Dishes\n\n"
            for dish in data.get("food", {}).get("must_try_dishes", [])[:10]:
                md += f"- {dish}\n"
            md += "\n"
        
        return md
    
    @staticmethod
    def export_html(data: Dict[str, Any], destination: str, template: Optional[str] = None) -> Optional[str]:
        """Export as HTML"""
        try:
            html_content = ExportService._generate_html(data, destination, template)
            filename = f"output/{destination.lower().replace(' ', '_')}_guide_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            return filename if FileManager.save_html(html_content, filename) else None
        except Exception as e:
            logger.error(f"HTML export error: {e}")
            return None
    
    @staticmethod
    def _generate_html(data: Dict[str, Any], destination: str, template: Optional[str] = None) -> str:
        """Generate HTML content"""
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Travel Guide: {destination}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
                h1 {{ color: #333; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }}
                h2 {{ color: #555; margin-top: 30px; }}
                .place {{ margin: 15px 0; padding: 15px; background: #f9f9f9; border-left: 4px solid #3b82f6; }}
                .place h3 {{ margin: 0 0 10px 0; }}
                .itinerary {{ margin: 15px 0; padding: 15px; background: #f0f7ff; border-radius: 5px; }}
                .day {{ font-weight: bold; color: #3b82f6; }}
                ul {{ line-height: 1.8; }}
                .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Travel Guide: {destination}</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        
        if "places" in data:
            html += "<h2>Top Places</h2>"
            for place in data.get("places", {}).get("places", [])[:5]:
                html += f"""
                <div class="place">
                    <h3>{place.get('name', 'Unknown')}</h3>
                    <p>{place.get('description', '')}</p>
                </div>
                """
        
        if "itinerary" in data:
            html += "<h2>3-Day Itinerary</h2>"
            for day in data.get("itinerary", {}).get("three_days", []):
                html += f"<div class='itinerary'><div class='day'>Day {day.get('day', 1)}</div><ul>"
                for activity in day.get("activities", []):
                    html += f"<li>{activity}</li>"
                html += "</ul></div>"
        
        if "food" in data:
            html += "<h2>Must-Try Dishes</h2><ul>"
            for dish in data.get("food", {}).get("must_try_dishes", [])[:10]:
                html += f"<li>{dish}</li>"
            html += "</ul>"
        
        html += """
                <div class="footer">
                    <p>This guide was generated by TravelAI. For more information, visit our website.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
