# RAG Mutual Funds - Project Structure

## 📁 Directory Organization

```
RAG_Mutual_Funds/
├── docs/           # All documentation (30 files)
├── scripts/        # Executable Python scripts (14 files)
├── src/            # Source code (23 items)
├── frontend/       # Next.js frontend application
├── data/           # Data storage (raw, processed, cache)
├── chroma_db/      # Vector database storage
├── tests/          # Test files
└── .qoder/         # IDE configuration
```

## 🚀 Quick Start

### 1. Start Everything
```bash
.venv\Scripts\activate
python scripts/start_all.py
```

### 2. Access Applications
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📚 Documentation

All documentation is now organized in the `docs/` folder:
- See [`docs/INDEX.md`](docs/INDEX.md) for complete navigation
- Getting started guides
- Architecture documentation
- Phase-by-phase implementation details

## 🛠️ Scripts

All executable scripts are in the `scripts/` folder:
- See [`scripts/README.md`](scripts/README.md) for usage
- Phase runners
- Data loading scripts
- Application startup scripts
- Scrapers

## 📦 Key Folders

| Folder | Purpose | Items |
|--------|---------|-------|
| `src/` | Core Python source code | 23 |
| `frontend/` | Next.js React application | 9 |
| `data/` | Raw and processed data | 3 |
| `chroma_db/` | Vector database | 6 |
| `tests/` | Test suites | 4 |

## 🔧 Configuration Files

- `.env` - Environment variables
- `.gitignore` - Git ignore rules
- `frontend/.env.local` - Frontend configuration

---

**Clean structure implemented**: March 2026
- ✅ Root directory decluttered
- ✅ Documentation moved to `docs/`
- ✅ Scripts moved to `scripts/`
- ✅ Navigation improved
