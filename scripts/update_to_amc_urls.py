"""
Update sample data with official AMC (HDFC) URLs instead of INDMoney
AMC websites are more stable and reliable
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Sample data with official HDFC AMC URLs (more reliable)
sample_chunks = [
    {
        "fund_name": "HDFC ELSS Tax Saver Fund",
        "chunk_type": "lock_in_exit",
        "chunk_text": "HDFC ELSS Tax Saver Fund has a lock-in period of 3 years from the date of investment.",
        "source_url": "https://www.hdfcfund.com/products/equity-solutions/hdfc-elss"
    },
    {
        "fund_name": "HDFC ELSS Tax Saver Fund",
        "chunk_type": "investment_details",
        "chunk_text": "HDFC ELSS Tax Saver Fund Direct Plan has an expense ratio of 1.05% as of March 2024.",
        "source_url": "https://www.hdfcfund.com/products/equity-solutions/hdfc-elss"
    },
    {
        "fund_name": "HDFC Large Cap Fund",
        "chunk_type": "investment_details",
        "chunk_text": "HDFC Large Cap Fund Direct Plan has a total expense ratio (TER) of 0.95%.",
        "source_url": "https://www.hdfcfund.com/products/equity-solutions/hdfc-large-cap-fund"
    },
    {
        "fund_name": "HDFC Large Cap Fund",
        "chunk_type": "investment_details",
        "chunk_text": "HDFC Large Cap Fund allows SIP starting from ₹500 per month.",
        "source_url": "https://www.hdfcfund.com/products/equity-solutions/hdfc-large-cap-fund"
    },
    {
        "fund_name": "HDFC Small Cap Fund",
        "chunk_type": "investment_details",
        "chunk_text": "HDFC Small Cap Fund offers flexible SIP options.",
        "source_url": "https://www.hdfcfund.com/products/equity-solutions/hdfc-small-cap-fund"
    },
    {
        "fund_name": "HDFC Flexi Cap Fund",
        "chunk_type": "investment_details",
        "chunk_text": "HDFC Flexi Cap Fund requires minimum SIP of ₹500.",
        "source_url": "https://www.hdfcfund.com/products/equity-solutions/hdfc-flexi-cap-fund"
    },
    {
        "fund_name": "HDFC Mid Cap Fund",
        "chunk_type": "investment_details",
        "chunk_text": "HDFC Mid Cap Fund provides SIP facility.",
        "source_url": "https://www.hdfcfund.com/products/equity-solutions/hdfc-mid-cap-opportunities-fund"
    },
]

print("Updated sample chunks with OFFICIAL HDFC AMC URLs:")
for chunk in sample_chunks:
    print(f"  • {chunk['fund_name']}: {chunk['source_url']}")
