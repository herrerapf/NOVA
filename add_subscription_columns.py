import sqlite3
DB = 'gym.db'

def add_column_if_not_exists(conn, table, col_name, col_def):
    cur = conn.cursor()
    cols = [r[1] for r in cur.execute(f'PRAGMA table_info({table})').fetchall()]
    if col_name not in cols:
        cur.execute(f'ALTER TABLE {table} ADD COLUMN {col_def}')
        print(f'Added column {col_name} to {table}')
    else:
        print(f'Column {col_name} already exists')

def main():
    conn = sqlite3.connect(DB)
    try:
        add_column_if_not_exists(conn, 'user', 'subscription_date', "subscription_date DATE")
        add_column_if_not_exists(conn, 'user', 'subscription_days', "subscription_days INTEGER")
        conn.commit()
    finally:
        conn.close()

if __name__ == '__main__':
    main()
