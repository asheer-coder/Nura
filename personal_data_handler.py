import sqlite3

class PersonalDataHandler:
    def __init__(self, db_name='navion_personal_data.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False) # Allow multi-threading
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS personal_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_phrase TEXT UNIQUE,
                value TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        print("PersonalDataHandler: Database table 'personal_info' checked/created.")

    def store_data(self, key_phrase, value):
        try:
            self.cursor.execute("UPDATE personal_info SET value = ?, timestamp = CURRENT_TIMESTAMP WHERE key_phrase = ?", (value, key_phrase))
            if self.cursor.rowcount == 0:
                self.cursor.execute("INSERT INTO personal_info (key_phrase, value) VALUES (?, ?)", (key_phrase, value))
            self.conn.commit()
            print(f"PersonalDataHandler: Stored/Updated: Key='{key_phrase}', Value='{value}'")
            return True
        except sqlite3.IntegrityError as e:
            print(f"PersonalDataHandler: Integrity error storing data for '{key_phrase}': {e}")
            return False
        except Exception as e:
            print(f"PersonalDataHandler: Error storing data: {e}")
            return False

    def get_data(self, key_phrase):
        self.cursor.execute("SELECT value FROM personal_info WHERE key_phrase = ?", (key_phrase,))
        result = self.cursor.fetchone()
        if result:
            print(f"PersonalDataHandler: Retrieved: Key='{key_phrase}', Value='{result[0]}'")
            return result[0]
        print(f"PersonalDataHandler: No data found for key: '{key_phrase}'")
        return None

    def close(self):
        self.conn.close()
        print("PersonalDataHandler: Database connection closed.")