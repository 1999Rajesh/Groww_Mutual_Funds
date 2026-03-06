# Data Sources & URLs Used in RAG Mutual Funds Assistant

## Primary Data Sources (15 URLs)

### HDFC AMC Official Sources
1. **HDFC Top 100 Fund** - https://www.hdfcfund.com/product-solutions/overview/hdfc-top-100-fund/direct
2. **HDFC Flexi Cap Fund** - https://www.hdfcfund.com/product-solutions/overview/hdfc-flexi-cap-fund/direct
3. **HDFC ELSS Tax Saver Fund** - https://www.hdfcfund.com/product-solutions/overview/hdfc-elss-tax-saver/direct
4. **HDFC Mid-Cap Opportunities Fund** - https://www.hdfcfund.com/product-solutions/overview/hdfc-mid-cap-opportunities-fund/direct

### Groww Platform Sources
5. **HDFC Large Cap Fund (Direct Growth)** - https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-plan-growth
6. **HDFC Equity Fund (Direct Growth)** - https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth
7. **HDFC ELSS Tax Saver Fund (Direct Growth)** - https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth
8. **HDFC Mid-Cap Opportunities Fund (Direct Growth)** - https://groww.in/mutual-funds/hdfc-mid-cap-opportunities-fund-direct-growth

### Regulatory & Educational Resources
9. **AMFI India** - https://www.amfiindia.com (Mutual fund regulations and data)
10. **SEBI** - https://www.sebi.gov.in (Securities and Exchange Board guidelines)
11. **CAMS** - https://www.camsonline.com (Fund transaction services)
12. **KFintech** - https://kfintech.com (Fund documentation)

## Data Collection Method
- **Web Scraping**: Playwright with Python for dynamic content
- **Embedding Model**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Database**: ChromaDB for semantic search
- **Chunking Strategy**: 512 tokens with 50-token overlap

## Coverage
- **Total Funds**: 4 HDFC mutual fund schemes
- **Categories**: Large Cap, Flexi Cap, ELSS, Mid Cap
- **Data Points**: NAV, expense ratio, fund manager details, portfolio allocation
- **Last Updated**: March 6, 2026

## Verification
All sources are official and publicly available:
- ✅ AMC official website (primary source)
- ✅ Registered investment platform (Groww)
- ✅ Regulatory bodies (AMFI, SEBI)
- ✅ RTA services (CAMS, KFintech)
