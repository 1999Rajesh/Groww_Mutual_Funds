"""
Data models for Mutual Fund schemes
"""
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List


class FundScheme(BaseModel):
    """Pydantic model for structured mutual fund data"""
    fund_name: str = Field(..., description="Name of the mutual fund")
    scheme_type: str = Field(..., description="Type of scheme (Direct, Regular, Growth, Dividend)")
    category: str = Field(..., description="Fund category (ELSS, Large Cap, Mid Cap, Small Cap, etc.)")
    
    # Investment Details
    expense_ratio: Optional[float] = Field(None, ge=0, description="Annual fee as percentage of assets")
    lock_in_period: Optional[str] = Field(None, description="Lock-in period (e.g., '3 years' for ELSS)")
    minimum_sip: Optional[float] = Field(None, ge=0, description="Minimum SIP investment amount in INR")
    minimum_lumpsum: Optional[float] = Field(None, ge=0, description="Minimum lumpsum investment in INR")
    additional_investment: Optional[float] = Field(None, ge=0, description="Minimum additional investment amount")
    
    # Load & Risk Details
    exit_load: Optional[str] = Field(None, description="Exit load details (e.g., '1% if redeemed within 1 year')")
    risk_level: Optional[str] = Field(None, description="Risk level (Low, Moderate, High, Very High)")
    benchmark: Optional[str] = Field(None, description="Benchmark index for the fund")
    
    # Fund Management
    fund_manager: Optional[str] = Field(None, description="Name of the fund manager")
    aum: Optional[float] = Field(None, ge=0, description="Assets Under Management in Crores")
    inception_date: Optional[date] = Field(None, description="Fund inception date")
    
    # Returns
    returns_1y: Optional[float] = Field(None, description="1 year return percentage")
    returns_3y: Optional[float] = Field(None, description="3 year annualized return percentage")
    returns_5y: Optional[float] = Field(None, description="5 year annualized return percentage")
    since_inception: Optional[float] = Field(None, description="Returns since inception")
    
    # Additional Information
    nav: Optional[float] = Field(None, ge=0, description="Current Net Asset Value")
    nav_date: Optional[date] = Field(None, description="Date of NAV")
    isin: Optional[str] = Field(None, description="ISIN code for the fund")
    amfi_code: Optional[str] = Field(None, description="AMFI code for the fund")
    
    # Metadata
    source_url: Optional[str] = Field(None, description="URL from where data was scraped")
    last_updated: Optional[date] = Field(None, description="Last updated date")
    
    class Config:
        json_schema_extra = {
            "example": {
                "fund_name": "HDFC ELSS Tax Saver Fund",
                "scheme_type": "Direct Plan - Growth Option",
                "category": "ELSS",
                "expense_ratio": 0.68,
                "lock_in_period": "3 years",
                "minimum_sip": 500.0,
                "minimum_lumpsum": 5000.0,
                "exit_load": "Nil",
                "risk_level": "Very High",
                "benchmark": "NIFTY 500 TRI",
                "fund_manager": "Chirag Setalvad",
                "aum": 28500.5,
                "returns_1y": 12.5,
                "returns_3y": 15.2,
                "returns_5y": 18.7
            }
        }


class FundChunk(BaseModel):
    """Model for chunked fund data with metadata"""
    fund_name: str
    chunk_id: str
    chunk_text: str
    chunk_type: str = Field(..., description="Type of information (expense_ratio, sip, lock_in, etc.)")
    metadata: dict = Field(default_factory=dict)
    token_count: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "fund_name": "HDFC ELSS Tax Saver Fund",
                "chunk_id": "hdfc_elss_expense_ratio_001",
                "chunk_text": "HDFC ELSS Tax Saver Fund Direct Plan has an expense ratio of 0.68%",
                "chunk_type": "expense_ratio",
                "metadata": {
                    "source_url": "https://www.indmoney.com/mutual-funds/hdfc-elss-tax-saver-fund",
                    "scraped_at": "2024-01-15T10:30:00"
                },
                "token_count": 15
            }
        }


class QAPair(BaseModel):
    """Model for generated Q&A pairs"""
    question: str
    answer: str
    fund_name: str
    chunk_type: str
    confidence_score: float = Field(ge=0, le=1)
    source_chunk_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the expense ratio of HDFC ELSS Tax Saver Fund?",
                "answer": "The expense ratio of HDFC ELSS Tax Saver Fund Direct Plan is 0.68%",
                "fund_name": "HDFC ELSS Tax Saver Fund",
                "chunk_type": "expense_ratio",
                "confidence_score": 0.95
            }
        }


class ScrapedData(BaseModel):
    """Model for raw scraped data"""
    fund_name: str
    url: str
    scraped_at: str
    raw_html: Optional[str] = None
    parsed_data: dict
    status: str = Field(..., description="success or failed")
    error_message: Optional[str] = None
