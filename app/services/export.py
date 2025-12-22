"""
Data export service for CSV and visual formats
"""
from typing import List, Dict, Any
import csv
import io
from fastapi.responses import StreamingResponse


class ExportService:
    """Service for exporting data in various formats"""
    
    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filename: str = "export.csv") -> StreamingResponse:
        """
        Export data to CSV format
        
        Args:
            data: List of dictionaries containing data
            filename: Name of the CSV file
            
        Returns:
            StreamingResponse with CSV data
        """
        if not data:
            # Return empty CSV with headers
            output = io.StringIO()
            output.write("No data available\n")
            output.seek(0)
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        # Get all unique keys from data
        headers = set()
        for row in data:
            headers.update(row.keys())
        headers = sorted(list(headers))
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
        
        # Return as streaming response
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    @staticmethod
    def prepare_chart_data(data: List[Dict[str, Any]], x_field: str, y_field: str) -> Dict[str, Any]:
        """
        Prepare data for chart visualization
        
        Args:
            data: List of dictionaries
            x_field: Field name for X-axis
            y_field: Field name for Y-axis
            
        Returns:
            Dictionary with chart data in format suitable for Chart.js or similar
        """
        labels = []
        values = []
        
        for row in data:
            if x_field in row and y_field in row:
                labels.append(str(row[x_field]))
                values.append(row[y_field])
        
        return {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": y_field,
                    "data": values,
                    "backgroundColor": "rgba(102, 126, 234, 0.6)",
                    "borderColor": "rgba(102, 126, 234, 1)",
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "scales": {
                    "y": {
                        "beginAtZero": True
                    }
                }
            }
        }
    
    @staticmethod
    def prepare_table_data(data: List[Dict[str, Any]], limit: int = 100) -> Dict[str, Any]:
        """
        Prepare data for table visualization
        
        Args:
            data: List of dictionaries
            limit: Maximum rows to return
            
        Returns:
            Dictionary with table structure
        """
        if not data:
            return {
                "headers": [],
                "rows": [],
                "total": 0
            }
        
        # Get headers from first row
        headers = list(data[0].keys())
        
        # Prepare rows
        rows = []
        for row in data[:limit]:
            rows.append([row.get(h, "") for h in headers])
        
        return {
            "headers": headers,
            "rows": rows,
            "total": len(data),
            "displayed": len(rows)
        }
