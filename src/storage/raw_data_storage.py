"""
Raw data storage for scraped mutual fund data
Handles JSON/CSV storage with version control and timestamp tracking
"""
import json
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

from src.config import DATA_RAW_DIR, DATA_PROCESSED_DIR, DATA_CACHE_DIR
from src.models.fund_schema import FundScheme, ScrapedData


class RawDataStorage:
    """
    Storage manager for raw scraped data
    Supports JSON and CSV formats with versioning
    """
    
    def __init__(self, base_dir: str = None):
        """
        Initialize storage manager
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = Path(base_dir) if base_dir else Path(DATA_RAW_DIR)
        self.raw_dir = self.base_dir / "raw"
        self.processed_dir = Path(DATA_PROCESSED_DIR)
        self.cache_dir = Path(DATA_CACHE_DIR)
        
        # Create directories if they don't exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories"""
        for directory in [self.raw_dir, self.processed_dir, self.cache_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
            # Create .gitkeep file to track empty directories in git
            gitkeep = directory / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.touch()
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _generate_filename(self, prefix: str, extension: str) -> str:
        """Generate filename with timestamp"""
        timestamp = self._get_timestamp()
        return f"{prefix}_{timestamp}.{extension}"
    
    def save_to_json(
        self, 
        data: Any, 
        prefix: str = "scraped_data",
        include_timestamp: bool = True
    ) -> str:
        """
        Save data to JSON file
        
        Args:
            data: Data to save (dict, list, or FundScheme objects)
            prefix: Filename prefix
            include_timestamp: Whether to include timestamp in filename
            
        Returns:
            Path to saved file
        """
        if include_timestamp:
            filename = self._generate_filename(prefix, "json")
        else:
            filename = f"{prefix}.json"
        
        filepath = self.raw_dir / filename
        
        # Convert Pydantic models to dict
        if hasattr(data, 'dict'):
            data = data.dict(exclude_none=True)
        elif isinstance(data, list):
            data = [item.dict(exclude_none=True) if hasattr(item, 'dict') else item for item in data]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Data saved to {filepath}")
        return str(filepath)
    
    def save_to_csv(
        self, 
        data: List[Dict[str, Any]], 
        prefix: str = "scraped_data",
        include_timestamp: bool = True
    ) -> str:
        """
        Save data to CSV file
        
        Args:
            data: List of dictionaries to save
            prefix: Filename prefix
            include_timestamp: Whether to include timestamp in filename
            
        Returns:
            Path to saved file
        """
        if not data:
            raise ValueError("No data to save")
        
        if include_timestamp:
            filename = self._generate_filename(prefix, "csv")
        else:
            filename = f"{prefix}.csv"
        
        filepath = self.raw_dir / filename
        
        # Convert Pydantic models to dicts
        rows = []
        for item in data:
            if hasattr(item, 'dict'):
                rows.append(item.dict(exclude_none=True))
            else:
                rows.append(item)
        
        # Write to CSV
        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False)
        
        logger.info(f"Data saved to CSV: {filepath}")
        return str(filepath)
    
    def load_from_json(self, filename: str) -> Any:
        """
        Load data from JSON file
        
        Args:
            filename: Name of the JSON file
            
        Returns:
            Loaded data
        """
        filepath = self.raw_dir / filename
        
        if not filepath.exists():
            # Try absolute path
            filepath = Path(filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_latest_json(self, prefix: str = "scraped_data") -> Optional[Any]:
        """
        Load the most recent JSON file with given prefix
        
        Args:
            prefix: Filename prefix to search for
            
        Returns:
            Loaded data or None if no files found
        """
        pattern = f"{prefix}_*.json"
        files = list(self.raw_dir.glob(pattern))
        
        if not files:
            return None
        
        # Sort by modification time (newest first)
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        
        logger.info(f"Loading latest file: {latest_file}")
        return self.load_from_json(latest_file.name)
    
    def save_scraped_data(
        self, 
        fund_schemes: List[FundScheme],
        format: str = "both"
    ) -> Dict[str, str]:
        """
        Save scraped fund schemes to storage
        
        Args:
            fund_schemes: List of FundScheme objects
            format: Storage format ('json', 'csv', or 'both')
            
        Returns:
            Dictionary with paths to saved files
        """
        saved_files = {}
        
        # Convert to serializable format
        data = [scheme.dict(exclude_none=True) for scheme in fund_schemes]
        
        # Add metadata
        metadata = {
            "scraped_at": datetime.now().isoformat(),
            "total_funds": len(fund_schemes),
            "fund_names": [scheme.fund_name for scheme in fund_schemes]
        }
        
        if format in ["json", "both"]:
            json_path = self.save_to_json({
                "metadata": metadata,
                "data": data
            }, prefix="mutual_funds")
            saved_files["json"] = json_path
        
        if format in ["csv", "both"]:
            csv_path = self.save_to_csv(data, prefix="mutual_funds")
            saved_files["csv"] = csv_path
        
        return saved_files
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics
        
        Returns:
            Dictionary with storage stats
        """
        json_files = list(self.raw_dir.glob("*.json"))
        csv_files = list(self.raw_dir.glob("*.csv"))
        
        total_size = sum(f.stat().st_size for f in self.raw_dir.glob("*"))
        
        return {
            "json_files_count": len(json_files),
            "csv_files_count": len(csv_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "raw_directory": str(self.raw_dir),
            "processed_directory": str(self.processed_dir),
            "cache_directory": str(self.cache_dir)
        }
    
    def cleanup_old_files(self, days: int = 30) -> int:
        """
        Remove files older than specified days
        
        Args:
            days: Number of days threshold
            
        Returns:
            Number of files deleted
        """
        import time
        
        current_time = time.time()
        threshold_seconds = days * 24 * 60 * 60
        deleted_count = 0
        
        for file in self.raw_dir.iterdir():
            if file.is_file():
                file_age = current_time - file.stat().st_mtime
                if file_age > threshold_seconds:
                    file.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old file: {file.name}")
        
        logger.info(f"Cleanup complete. Deleted {deleted_count} files")
        return deleted_count
    
    def export_for_processing(self, output_format: str = "json") -> str:
        """
        Export data in format suitable for processing pipeline
        
        Args:
            output_format: Output format ('json' or 'csv')
            
        Returns:
            Path to exported file
        """
        # Load latest data
        data = self.load_latest_json("mutual_funds")
        
        if not data:
            raise FileNotFoundError("No scraped data found")
        
        # Extract just the data array
        if isinstance(data, dict) and "data" in data:
            funds_data = data["data"]
        else:
            funds_data = data
        
        # Save to processed directory
        if output_format == "json":
            filepath = self.processed_dir / f"funds_{self._get_timestamp()}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(funds_data, f, indent=2, ensure_ascii=False, default=str)
        elif output_format == "csv":
            filepath = self.processed_dir / f"funds_{self._get_timestamp()}.csv"
            df = pd.DataFrame(funds_data)
            df.to_csv(filepath, index=False)
        else:
            raise ValueError(f"Unsupported format: {output_format}")
        
        logger.info(f"Data exported for processing: {filepath}")
        return str(filepath)


# Import logging at module level
import logging
logger = logging.getLogger(__name__)


def main():
    """Example usage"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize storage
    storage = RawDataStorage()
    
    # Example: Save sample data
    sample_data = [
        {
            "fund_name": "HDFC ELSS Tax Saver Fund",
            "category": "ELSS",
            "expense_ratio": 0.68,
            "minimum_sip": 500.0
        }
    ]
    
    # Save to both formats
    saved_files = storage.save_scraped_data(sample_data, format="both")
    print(f"Saved files: {saved_files}")
    
    # Get stats
    stats = storage.get_storage_stats()
    print(f"\nStorage Stats: {stats}")
    
    # Load latest data
    latest_data = storage.load_latest_json("mutual_funds")
    print(f"\nLatest data loaded: {latest_data is not None}")


if __name__ == "__main__":
    main()
