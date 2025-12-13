import pandas as pd
from typing import List, Dict, Any
import json

class CSVService:
    @staticmethod
    def read_csv(file_path: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            raise ValueError(f"Error reading CSV: {str(e)}")
    
    @staticmethod
    def analyze_csv(file_path: str) -> Dict[str, Any]:
        df = CSVService.read_csv(file_path)
        
        analysis = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "data_types": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "numeric_summary": {},
            "sample_data": df.head(5).to_dict(orient='records')
        }
        
        # Get statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            analysis["numeric_summary"][col] = {
                "mean": float(df[col].mean()) if not df[col].isnull().all() else None,
                "median": float(df[col].median()) if not df[col].isnull().all() else None,
                "std": float(df[col].std()) if not df[col].isnull().all() else None,
                "min": float(df[col].min()) if not df[col].isnull().all() else None,
                "max": float(df[col].max()) if not df[col].isnull().all() else None,
            }
        
        return analysis
    
    @staticmethod
    def analyze_multiple_csvs(file_paths: List[str]) -> List[Dict[str, Any]]:
        results = []
        for idx, path in enumerate(file_paths):
            try:
                analysis = CSVService.analyze_csv(path)
                analysis["csv_index"] = idx
                analysis["csv_path"] = path
                results.append(analysis)
            except Exception as e:
                results.append({
                    "csv_index": idx,
                    "csv_path": path,
                    "error": str(e)
                })
        return results
    
    @staticmethod
    def generate_data_summary(analysis_results: List[Dict[str, Any]]) -> str:
        summary_parts = []
        
        for result in analysis_results:
            if "error" in result:
                summary_parts.append(f"CSV {result['csv_index']}: Error - {result['error']}")
                continue
            
            part = f"\n--- CSV File {result['csv_index']} ---\n"
            part += f"Rows: {result['row_count']}, Columns: {result['column_count']}\n"
            part += f"Column Names: {', '.join(result['columns'])}\n"
            
            if result['numeric_summary']:
                part += "\nNumeric Statistics:\n"
                for col, stats in result['numeric_summary'].items():
                    part += f"  {col}: mean={stats['mean']:.2f}, min={stats['min']:.2f}, max={stats['max']:.2f}\n"
            
            summary_parts.append(part)
        
        return "\n".join(summary_parts)
