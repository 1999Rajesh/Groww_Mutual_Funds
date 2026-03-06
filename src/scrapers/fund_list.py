"""List of mutual funds and data sources
Based on Source.csv.xlsx - Multi-source configuration
Includes: HDFC AMC, Groww, AMFI, SEBI, CAMS, KFintech
"""

# =============================================================================
# HDFC MUTUAL FUND SCHEMES - HDFC AMC & Groww Platform Only
# =============================================================================

# HDFC Mutual Fund Schemes with HDFC AMC and Groww URLs
HDFC_FUNDS = [
    {
        "name": "HDFC Top 100 Fund",
        "scheme_type": "Direct Growth",
        "category": "Large Cap",
        "amc": "HDFC Mutual Fund",
        "urls": {
            "hdfc_amc": "https://www.hdfcfund.com/product-solutions/overview/hdfc-top-100-fund/direct",
            "groww": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-plan-growth"
        }
    },
    {
        "name": "HDFC Flexi Cap Fund",
        "scheme_type": "Direct Growth",
        "category": "Flexi Cap",
        "amc": "HDFC Mutual Fund",
        "urls": {
            "hdfc_amc": "https://www.hdfcfund.com/product-solutions/overview/hdfc-flexi-cap-fund/direct",
            "groww": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth"
        }
    },
    {
        "name": "HDFC ELSS Tax Saver Fund",
        "scheme_type": "Direct Growth",
        "category": "ELSS",
        "amc": "HDFC Mutual Fund",
        "urls": {
            "hdfc_amc": "https://www.hdfcfund.com/product-solutions/overview/hdfc-elss-tax-saver/direct",
            "groww": "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth"
        }
    },
    {
        "name": "HDFC Mid-Cap Opportunities Fund",
        "scheme_type": "Direct Growth",
        "category": "Mid Cap",
        "amc": "HDFC Mutual Fund",
        "urls": {
            "hdfc_amc": "https://www.hdfcfund.com/product-solutions/overview/hdfc-mid-cap-opportunities-fund/direct",
            "groww": "https://groww.in/mutual-funds/hdfc-mid-cap-opportunities-fund-direct-growth"
        }
    },
]

# =============================================================================
# AMC STATUTORY DISCLOSURES
# =============================================================================
AMC_DISCLOSURES = [
    {
        "title": "HDFC MF Statutory Disclosure and Fees",
        "url": "https://www.hdfcfund.com/statutory-disclosure",
        "category": "Fees and Charges",
        "source": "HDFC AMC"
    },
]

# =============================================================================
# GROWW EDUCATIONAL GUIDES
# =============================================================================
GROWW_GUIDES = [
    {
        "title": "What is SIP (Systematic Investment Plan)",
        "url": "https://groww.in/p/sip-systematic-investment-plan",
        "category": "Groww Guide",
        "source": "Groww"
    },
    {
        "title": "How to Get Capital Gains Statement for Mutual Fund Investments",
        "url": "https://groww.in/blog/how-to-get-capital-gains-statement-for-mutual-fund-investments",
        "category": "Groww Guide",
        "source": "Groww"
    },
    {
        "title": "SIP vs Mutual Fund - Understanding the Difference",
        "url": "https://groww.in/blog/what-is-the-difference-between-sip-and-mutual-fund",
        "category": "Groww Guide",
        "source": "Groww"
    },
]

# =============================================================================
# AMFI EDUCATIONAL RESOURCES
# =============================================================================
AMFI_EDUCATION = [
    {
        "title": "Introduction to Mutual Funds",
        "url": "https://www.amfiindia.com/investor-corner/knowledge-center/introduction-to-mutual-funds.html",
        "category": "AMFI Education",
        "source": "AMFI India"
    },
    {
        "title": "Types of Mutual Fund Schemes",
        "url": "https://www.amfiindia.com/investor-corner/knowledge-center/types-of-mutual-fund-schemes.html",
        "category": "AMFI Education",
        "source": "AMFI India"
    },
    {
        "title": "Risk Factors in Mutual Funds",
        "url": "https://www.amfiindia.com/investor-corner/knowledge-center/risks-in-mutual-funds.html",
        "category": "AMFI Education",
        "source": "AMFI India"
    },
]

# =============================================================================
# SEBI REGULATORY RESOURCES
# =============================================================================
SEBI_REGULATIONS = [
    {
        "title": "SEBI MF Categorization and Rationalization Circular",
        "url": "https://www.sebi.gov.in/legal/circulars/oct-2017/categorization-and-rationalization-of-mutual-fund-schemes_36199.html",
        "category": "SEBI Regulation",
        "source": "SEBI"
    },
]

# =============================================================================
# CONSOLIDATED ACCOUNT STATEMENT (CAS) GUIDES
# =============================================================================
CAS_GUIDES = [
    {
        "title": "CAMS Consolidated Account Statement",
        "url": "https://www.camsonline.com/Investors/Statements/Consolidated-Account-Statement",
        "category": "CAS Guide",
        "source": "CAMS"
    },
    {
        "title": "KFintech Consolidated Account Statement",
        "url": "https://mfs.kfintech.com/investor/General/ConsolidatedAccountStatement",
        "category": "CAS Guide",
        "source": "KFintech"
    },
]

# Primary focus schemes for MVP (diverse categories)
PRIMARY_SCHEMES = [
    "HDFC ELSS Tax Saver Fund",  # ELSS
    "HDFC Top 100 Fund",  # Large Cap
    "HDFC Flexi Cap Fund",  # Flexi Cap
    "HDFC Mid-Cap Opportunities Fund",  # Mid Cap
]

# All funds combined
ALL_FUNDS = HDFC_FUNDS

# All educational and regulatory resources
ALL_RESOURCES = AMC_DISCLOSURES + GROWW_GUIDES + AMFI_EDUCATION + SEBI_REGULATIONS + CAS_GUIDES

# URL source priority (for citation)
SOURCE_PRIORITY = ["hdfc_amc", "groww"]

# Fund categories mapping
CATEGORY_MAPPING = {
    "ELSS": "Equity Linked Savings Scheme",
    "Large Cap": "Large Cap Fund",
    "Mid Cap": "Mid Cap Fund",
    "Small Cap": "Small Cap Fund",
    "Hybrid": "Hybrid Fund",
    "Focused": "Focused Fund",
    "Flexi Cap": "Flexi Cap Fund",
    "Sectoral": "Sectoral/Thematic Fund",
    "Gold ETF FoF": "Gold Fund of Fund",
    "Silver ETF FoF": "Silver Fund of Fund",
    "Children's Fund": "Children's Fund",
    "Retirement": "Retirement Fund",
    "FoF": "Fund of Funds",
    "Multi Asset": "Multi Asset Allocation",
    "Multi Cap": "Multi Cap Fund",
    "Debt": "Debt Fund",
    "Corporate Bond": "Corporate Bond Fund",
    "Money Market": "Money Market Fund",
    "Liquid": "Liquid Fund",
}
