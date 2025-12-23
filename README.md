# Payroll Calculator - Canadian Small Business MVP

Simple payroll calculator for Canadian small businesses. Calculates CPP, EI, federal/provincial taxes, and generates T4 slips.

## Quick Start

### Run the App (Development)

```bash
cd app
python main.py
```

That's it! The app will launch.

### Build Executable (Distribution)

```bash
cd app
pip install pyinstaller
pyinstaller --name "PayrollCalculator" --onefile \
  --add-data "data:data" \
  --add-data "logic:logic" \
  --add-data "db:db" \
  --add-data "ui:ui" \
  --add-data "utils:utils" \
  --noconfirm main.py
```

**Result:** `dist/PayrollCalculator` (standalone executable)

### Run the Built Executable

```bash
./dist/PayrollCalculator
```

Or double-click `PayrollCalculator` in Finder.

**No Python installation needed!**

## Requirements

- Python 3.8+
- macOS 10.13+ (for executable)
- No external dependencies needed (uses built-in tkinter, sqlite3)

## Features

✅ Payroll calculation (CPP, EI, taxes)  
✅ YTD tracking with annual maximums  
✅ CRA remittance totals  
✅ Employee management  
✅ T4 slip generation  
✅ Multi-province support  

## Project Structure

```
app/
├── main.py              # Entry point
├── data/                # Tax rates & T4 template
├── db/                  # Database operations
├── logic/               # Payroll calculations
├── ui/                  # GUI components
└── utils/               # Validators & helpers
```

## Important Notes

⚠️ Tax withholding is **simplified** (no TD1 credits)  
⚠️ Always verify with CRA PDOC calculator  
✅ Good for small businesses with straightforward payroll  

## Distribution

Share `dist/PayrollCalculator` with clients. They can double-click to run (no Python needed).

## License

[Your License]

---

**MVP 1.0** | December 2025
