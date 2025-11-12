import sqlite3


class DatabaseManager:
    def __init__(self, db_name="task.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT DEFAULT '#95a5a6'
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                completed BOOLEAN DEFAULT FALSE,
                category_id INTEGER,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        default_categories = [
            ("Общие", "#95a5a6"),
            ("Работа", "#3498db"),
            ("Личное", "#2ecc71"),
            ("Учеба", "#9b59b6"),
            ("Покупки", "#e67e22"),
            ("Здоровье", "#e74c3c")
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO categories (name, color) VALUES (?, ?)",
            default_categories
        )
        conn.commit()
        conn.close()

    def connectt(self):
        return sqlite3.connect(self.db_name)

    def getatt(self):
        conn = self.connectt()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.id, t.text, t.completed, c.name, c.color, t.created
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            ORDER BY t.created DESC
        ''')
        tasks = cursor.fetchall()
        conn.close()
        return tasks

    def addtsk(self, text, category_id):
        conn = self.connectt()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (text, category_id) VALUES (?, ?)",
            (text, category_id)
        )
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def upts(self, task_id, completed):
        conn = self.connectt()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET completed = ? WHERE id = ?",
            (completed, task_id)
        )
        conn.commit()
        conn.close()

    def deltsk(self, task_id):
        conn = self.connectt()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

    def clrct(self):
        conn = self.connectt()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE completed = TRUE")
        conn.commit()
        conn.close()

    def getctg(self):
        conn = self.connectt()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, color FROM categories ORDER BY name")
        categories = cursor.fetchall()
        conn.close()
        return categories

    def addctg(self, name, color="#95a5a6"):
        conn = self.connectt()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO categories (name, color) VALUES (?, ?)",
                (name, color)
            )
            category_id = cursor.lastrowid
            conn.commit()
            return category_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def deletectg(self, category_id):
        conn = self.connectt()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM categories WHERE name = 'Общие'")
        general_category = cursor.fetchone()
        if general_category:
            cursor.execute(
                "UPDATE tasks SET category_id = ? WHERE category_id = ?",
                (general_category[0], category_id)
            )
        cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
        conn.close()

    def getts(self):
        conn = self.connectt()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tasks")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = TRUE")
        completed = cursor.fetchone()[0]
        cursor.execute('''
            SELECT c.name, COUNT(t.id)
            FROM categories c
            LEFT JOIN tasks t ON c.id = t.category_id
            GROUP BY c.id, c.name
        ''')
        by_category = cursor.fetchall()
        conn.close()
        return total, completed, by_category
