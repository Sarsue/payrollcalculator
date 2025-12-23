"""
Database migration to add CASCADE delete to payroll_runs table.
Run this once to update existing databases.
"""
import sqlite3
import os

DB_PATH = "db/payroll.db"

def migrate_add_cascade():
    """Migrate existing database to add ON DELETE CASCADE."""
    if not os.path.exists(DB_PATH):
        print("Database doesn't exist yet. No migration needed.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    print("Starting migration: Adding CASCADE delete to payroll_runs...")
    
    # Step 1: Create new table with CASCADE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payroll_runs_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            pay_date TEXT NOT NULL,
            gross REAL NOT NULL,
            cpp_employee REAL,
            cpp_employer REAL,
            ei_employee REAL,
            ei_employer REAL,
            federal_withholding REAL,
            provincial_withholding REAL,
            total_deductions REAL,
            net REAL,
            period_count INTEGER DEFAULT 12,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
        )
    """)
    
    # Step 2: Copy data from old table to new table
    cursor.execute("""
        INSERT INTO payroll_runs_new 
        SELECT * FROM payroll_runs
    """)
    
    # Step 3: Drop old table
    cursor.execute("DROP TABLE payroll_runs")
    
    # Step 4: Rename new table to original name
    cursor.execute("ALTER TABLE payroll_runs_new RENAME TO payroll_runs")
    
    conn.commit()
    print("✅ Migration completed successfully!")
    print("   - payroll_runs table now has ON DELETE CASCADE")
    conn.close()

if __name__ == "__main__":
    migrate_add_cascade()
