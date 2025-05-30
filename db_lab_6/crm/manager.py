import psycopg2
from psycopg2 import sql, extras
from psycopg2.extras import DictCursor
import sys


class TaskManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="crm",
            user="postgres",
            password="password.for.db",
            host="localhost"
        )
        self.conn.autocommit = False
        self.cursor = self.conn.cursor(cursor_factory=DictCursor)

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def get_most_active_employees(self, limit=5):
        """Аналитический запрос 1: Самые активные сотрудники по количеству задач"""
        query = """
            SELECT e.employee_id, 
                   e.employee_email, 
                   COUNT(t.task_id) AS total_tasks
            FROM employees e
            JOIN tasks t ON e.employee_id = t.fk_employee_id
            GROUP BY e.employee_id
            ORDER BY total_tasks DESC
            LIMIT %s
        """
        if not self.execute_query(query, (limit,)):
            return None
        return self.cursor.fetchall()

    def get_tasks_after_date(self, start_date, end_date=None):
        """Аналитический запрос 2: Задачи, созданные в указанный период"""
        if end_date is None:
            end_date = '2100-01-01'  # Далекая будущая дата, если конечная дата не указана

        query = """
            SELECT *
            FROM tasks
            WHERE task_creation_date BETWEEN %s AND %s
            ORDER BY task_creation_date
        """
        if not self.execute_query(query, (start_date, end_date)):
            return None
        return self.cursor.fetchall()

    def execute_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return True
        except psycopg2.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")
            self.conn.rollback()  # Откатываем транзакцию при ошибке
            return False

    def create_task(self, description, status, creation_date, employee_id=None):
        # Проверяем существование сотрудника, если указан
        if employee_id is not None:
            if not self._employee_exists(employee_id):
                print("Ошибка: Сотрудник с указанным ID не существует")
                return None

        try:
            # Получаем следующее значение последовательности
            self.cursor.execute("SELECT nextval('tasks_task_id_seq')")
            next_id = self.cursor.fetchone()[0]

            # Вставляем новую задачу
            query = sql.SQL("""
                INSERT INTO tasks (task_id, task_description, task_status, task_creation_date, fk_employee_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING task_id
            """)
            self.cursor.execute(query, (next_id, description, status, creation_date, employee_id))
            task_id = self.cursor.fetchone()['task_id']
            self.conn.commit()
            print(f"Задача успешно создана с ID: {task_id}")
            return task_id

        except psycopg2.IntegrityError as e:
            self.conn.rollback()
            if "tasks_pkey" in str(e):
                # Если проблема с первичным ключом, сбрасываем последовательность
                self._reset_task_sequence()
                print("Обнаружен конфликт ID. Последовательность сброшена. Попробуйте снова.")
            else:
                print(f"Ошибка при создании задачи: {e}")
            return None

        except Exception as e:
            self.conn.rollback()
            print(f"Неожиданная ошибка при создании задачи: {e}")
            return None

    def _employee_exists(self, employee_id):
        """Проверяет существование сотрудника"""
        self.cursor.execute("SELECT 1 FROM employees WHERE employee_id = %s", (employee_id,))
        return self.cursor.fetchone() is not None

    def _reset_task_sequence(self):
        """Сбрасывает последовательность для task_id"""
        self.cursor.execute("SELECT MAX(task_id) FROM tasks")
        max_id = self.cursor.fetchone()[0] or 0
        self.cursor.execute(f"ALTER SEQUENCE tasks_task_id_seq RESTART WITH {max_id + 1}")
        self.conn.commit()
        print(f"Последовательность task_id сброшена. Новое начальное значение: {max_id + 1}")

    def get_all_tasks(self):
        query = "SELECT * FROM tasks ORDER BY task_id"
        if not self.execute_query(query):
            return []
        return self.cursor.fetchall()

    def get_task(self, task_id):
        query = "SELECT * FROM tasks WHERE task_id = %s"
        if not self.execute_query(query, (task_id,)):
            return None
        return self.cursor.fetchone()

    def update_task(self, task_id, description=None, status=None, employee_id=None):
        updates = []
        params = []

        if description is not None:
            updates.append("task_description = %s")
            params.append(description)
        if status is not None:
            updates.append("task_status = %s")
            params.append(status)
        if employee_id is not None:
            updates.append("fk_employee_id = %s")
            params.append(employee_id)

        if not updates:
            return False

        params.append(task_id)
        query = sql.SQL("UPDATE tasks SET {} WHERE task_id = %s").format(
            sql.SQL(", ").join(map(sql.SQL, updates)))

        if not self.execute_query(query, params):
            return False
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_task(self, task_id):
        # Сначала удаляем все подзадачи
        if not self.execute_query("DELETE FROM subtasks WHERE fk_task_id = %s", (task_id,)):
            return False

        # Затем удаляем саму задачу
        if not self.execute_query("DELETE FROM tasks WHERE task_id = %s", (task_id,)):
            return False
        self.conn.commit()
        return self.cursor.rowcount > 0

    def create_subtask(self, task_id, description, status=False):
        # Проверяем существование задачи
        if not self.get_task(task_id):
            print("Ошибка: Задача с указанным ID не существует")
            return None

        try:
            # Используем DEFAULT для автоматического получения ID
            query = sql.SQL("""
                INSERT INTO subtasks (subtask_description, subtask_status, fk_task_id)
                VALUES (%s, %s, %s)
                RETURNING subtask_id
            """)
            self.cursor.execute(query, (description, status, task_id))
            subtask_id = self.cursor.fetchone()['subtask_id']
            self.conn.commit()
            print(f"Подзадача успешно создана с ID: {subtask_id}")
            return subtask_id
        except psycopg2.IntegrityError as e:
            self.conn.rollback()
            if "subtasks_pkey" in str(e):
                # Если проблема с первичным ключом, сбрасываем последовательность
                self.cursor.execute("SELECT MAX(subtask_id) FROM subtasks")
                max_id = self.cursor.fetchone()[0] or 0
                self.cursor.execute(f"ALTER SEQUENCE subtasks_subtask_id_seq RESTART WITH {max_id + 1}")
                self.conn.commit()
                print("Обнаружен конфликт ID. Последовательность сброшена. Попробуйте снова.")
            else:
                print(f"Ошибка при создании подзадачи: {e}")
            return None
        except Exception as e:
            self.conn.rollback()
            print(f"Неожиданная ошибка: {e}")
            return None

    def get_all_subtasks(self, task_id=None):
        if task_id:
            query = "SELECT * FROM subtasks WHERE fk_task_id = %s ORDER BY subtask_id"
            if not self.execute_query(query, (task_id,)):
                return []
        else:
            query = "SELECT * FROM subtasks ORDER BY subtask_id"
            if not self.execute_query(query):
                return []
        return self.cursor.fetchall()

    def get_subtask(self, subtask_id):
        query = "SELECT * FROM subtasks WHERE subtask_id = %s"
        if not self.execute_query(query, (subtask_id,)):
            return None
        return self.cursor.fetchone()

    def update_subtask(self, subtask_id, description=None, status=None):
        updates = []
        params = []

        if description is not None:
            updates.append("subtask_description = %s")
            params.append(description)
        if status is not None:
            updates.append("subtask_status = %s")
            params.append(status)

        if not updates:
            return False

        params.append(subtask_id)
        query = sql.SQL("UPDATE subtasks SET {} WHERE subtask_id = %s").format(
            sql.SQL(", ").join(map(sql.SQL, updates)))

        if not self.execute_query(query, params):
            return False
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_subtask(self, subtask_id):
        if not self.execute_query("DELETE FROM subtasks WHERE subtask_id = %s", (subtask_id,)):
            return False
        self.conn.commit()
        return self.cursor.rowcount > 0


# Остальной код (display_tasks, display_subtasks, main) остается без изменений

def display_active_employees(employees):
    print("\nСамые активные сотрудники:")
    print("{:<10} {:<30} {:<15}".format("ID", "Email", "Кол-во задач"))
    for emp in employees:
        print("{:<10} {:<30} {:<15}".format(
            emp['employee_id'],
            emp['employee_email'],
            emp['total_tasks']
        ))

def display_tasks_by_date(tasks):
    display_tasks(tasks)  # Можно использовать существующую функци

def display_tasks(tasks):
    print("\nСписок задач:")
    print("{:<5} {:<30} {:<15} {:<15} {:<10}".format(
        "ID", "Описание", "Статус", "Дата создания", "ID сотрудника"))
    for task in tasks:
        print("{:<5} {:<30} {:<15} {:<15} {:<10}".format(
            task['task_id'],
            task['task_description'][:27] + '...' if len(task['task_description']) > 30 else task['task_description'],
            task['task_status'],
            str(task['task_creation_date']),
            task['fk_employee_id'] if task['fk_employee_id'] else 'None'
        ))


def display_subtasks(subtasks):
    print("\nСписок подзадач:")
    print("{:<5} {:<30} {:<10} {:<10}".format(
        "ID", "Описание", "Статус", "ID задачи"))
    for subtask in subtasks:
        print("{:<5} {:<30} {:<10} {:<10}".format(
            subtask['subtask_id'],
            subtask['subtask_description'][:27] + '...' if len(subtask['subtask_description']) > 30 else subtask[
                'subtask_description'],
            'Выполнена' if subtask['subtask_status'] else 'Не выполнена',
            subtask['fk_task_id']
        ))


def main():
    manager = TaskManager()

    while True:
        print("\nМеню управления задачами:")
        print("1. Управление задачами")
        print("2. Управление подзадачами")
        print("3. Аналитические запросы")
        print("0. Выход")

        choice = input("Выберите раздел: ")

        if choice == "0":
            break

        elif choice == "1":
            while True:
                print("\nУправление задачами:")
                print("1. Показать все задачи")
                print("2. Добавить задачу")
                print("3. Просмотреть задачу")
                print("4. Обновить задачу")
                print("5. Удалить задачу")
                print("0. Назад")

                task_choice = input("Выберите действие: ")

                if task_choice == "0":
                    break

                elif task_choice == "1":
                    tasks = manager.get_all_tasks()
                    display_tasks(tasks)

                elif task_choice == "2":
                    description = input("Введите описание задачи: ")
                    status = input("Введите статус задачи: ")
                    date = input("Введите дату создания (ГГГГ-ММ-ДД): ")
                    employee_id = input("Введите ID сотрудника (оставьте пустым, если нет): ")
                    employee_id = int(employee_id) if employee_id else None

                    try:
                        task_id = manager.create_task(description, status, date, employee_id)
                        print(f"Задача создана с ID: {task_id}")
                    except Exception as e:
                        print(f"Ошибка при создании задачи: {e}")

                elif task_choice == "3":
                    task_id = input("Введите ID задачи: ")
                    try:
                        task = manager.get_task(int(task_id))
                        if task:
                            display_tasks([task])
                            subtasks = manager.get_all_subtasks(int(task_id))
                            if subtasks:
                                display_subtasks(subtasks)
                            else:
                                print("У этой задачи нет подзадач")
                        else:
                            print("Задача не найдена")
                    except ValueError:
                        print("Неверный ID задачи")

                elif task_choice == "4":
                    task_id = input("Введите ID задачи для обновления: ")
                    description = input("Введите новое описание (оставьте пустым, чтобы не изменять): ")
                    status = input("Введите новый статус (оставьте пустым, чтобы не изменять): ")
                    employee_id = input("Введите новый ID сотрудника (оставьте пустым, чтобы не изменять): ")

                    try:
                        success = manager.update_task(
                            int(task_id),
                            description if description else None,
                            status if status else None,
                            int(employee_id) if employee_id else None
                        )
                        if success:
                            print("Задача успешно обновлена")
                        else:
                            print("Не удалось обновить задачу (возможно, задача не найдена)")
                    except ValueError:
                        print("Неверный формат данных")

                elif task_choice == "5":
                    task_id = input("Введите ID задачи для удаления: ")
                    try:
                        if manager.delete_task(int(task_id)):
                            print("Задача и все её подзадачи успешно удалены")
                        else:
                            print("Не удалось удалить задачу (возможно, задача не найдена)")
                    except ValueError:
                        print("Неверный ID задачи")

        elif choice == "2":
            while True:
                print("\nУправление подзадачами:")
                print("1. Показать все подзадачи")
                print("2. Добавить подзадачу")
                print("3. Просмотреть подзадачу")
                print("4. Обновить подзадачу")
                print("5. Удалить подзадачу")
                print("0. Назад")

                subtask_choice = input("Выберите действие: ")

                if subtask_choice == "0":
                    break

                elif subtask_choice == "1":
                    subtasks = manager.get_all_subtasks()
                    display_subtasks(subtasks)

                elif subtask_choice == "2":
                    task_id = input("Введите ID задачи для подзадачи: ")
                    description = input("Введите описание подзадачи: ")
                    status = input("Подзадача выполнена? (y/n): ").lower() == 'y'

                    try:
                        subtask_id = manager.create_subtask(int(task_id), description, status)
                        print(f"Подзадача создана с ID: {subtask_id}")
                    except Exception as e:
                        print(f"Ошибка при создании подзадачи: {e}")

                elif subtask_choice == "3":
                    subtask_id = input("Введите ID подзадачи: ")
                    try:
                        subtask = manager.get_subtask(int(subtask_id))
                        if subtask:
                            display_subtasks([subtask])
                        else:
                            print("Подзадача не найдена")
                    except ValueError:
                        print("Неверный ID подзадачи")

                elif subtask_choice == "4":
                    subtask_id = input("Введите ID подзадачи для обновления: ")
                    description = input("Введите новое описание (оставьте пустым, чтобы не изменять): ")
                    status_input = input("Подзадача выполнена? (y/n/пусто): ").lower()
                    status = None if status_input == '' else status_input == 'y'

                    try:
                        success = manager.update_subtask(
                            int(subtask_id),
                            description if description else None,
                            status
                        )
                        if success:
                            print("Подзадача успешно обновлена")
                        else:
                            print("Не удалось обновить подзадачу (возможно, подзадача не найдена)")
                    except ValueError:
                        print("Неверный формат данных")

                elif subtask_choice == "5":
                    subtask_id = input("Введите ID подзадачи для удаления: ")
                    try:
                        if manager.delete_subtask(int(subtask_id)):
                            print("Подзадача успешно удалена")
                        else:
                            print("Не удалось удалить подзадачу (возможно, подзадача не найдена)")
                    except ValueError:
                        print("Неверный ID подзадачи")

        elif choice == "3":
            while True:
                print("\nАналитические запросы:")
                print("1. Самые активные сотрудники")
                print("2. Задачи по дате создания")
                print("0. Назад")

                analytic_choice = input("Выберите запрос: ")

                if analytic_choice == "0":
                    break

                elif analytic_choice == "1":
                    try:
                        limit = int(input("Введите количество сотрудников для вывода: "))
                        employees = manager.get_most_active_employees(limit)
                        if employees:
                            display_active_employees(employees)
                        else:
                            print("Нет данных для отображения")
                    except ValueError:
                        print("Ошибка: введите целое число")

                elif analytic_choice == "2":
                    start_date = input("Введите начальную дату (ГГГГ-ММ-ДД): ")
                    end_date = input("Введите конечную дату (ГГГГ-ММ-ДД, оставьте пустым для всех последующих): ")

                    if not end_date.strip():
                        end_date = None

                    tasks = manager.get_tasks_after_date(start_date, end_date)
                    if tasks:
                        display_tasks_by_date(tasks)
                    else:
                        print("Нет задач в указанный период")


if __name__ == "__main__":
    main()