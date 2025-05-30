import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import manager

class TaskManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CRM System - Task Management")
        self.root.geometry("1000x600")

        self.manager = manager.TaskManager()

        self.create_widgets()
        self.load_tasks()

    def create_widgets(self):
        # Создаем вкладки
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка задач
        self.tasks_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.tasks_tab, text="Задачи")

        # Вкладка подзадач
        self.subtasks_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.subtasks_tab, text="Подзадачи")

        # Вкладка аналитики
        self.analytics_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_tab, text="Аналитика")

        # Создаем интерфейс для вкладки задач
        self.create_tasks_tab()
        self.create_subtasks_tab()
        self.create_analytics_tab()

    def create_tasks_tab(self):
        # Панель управления задачами
        control_frame = ttk.Frame(self.tasks_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(control_frame, text="Добавить задачу", command=self.show_add_task_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Редактировать", command=self.show_edit_task_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Удалить", command=self.delete_task).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Обновить список", command=self.load_tasks).pack(side=tk.LEFT, padx=2)

        # Таблица задач
        self.tasks_tree = ttk.Treeview(self.tasks_tab, columns=("description", "status", "date", "employee"),
                                       show="headings")
        self.tasks_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tasks_tree.heading("description", text="Описание")
        self.tasks_tree.heading("status", text="Статус")
        self.tasks_tree.heading("date", text="Дата создания")
        self.tasks_tree.heading("employee", text="Сотрудник")

        self.tasks_tree.column("description", width=400)
        self.tasks_tree.column("status", width=150)
        self.tasks_tree.column("date", width=150)
        self.tasks_tree.column("employee", width=200)

        # Привязываем двойной клик для просмотра подзадач
        self.tasks_tree.bind("<Double-1>", self.load_subtasks_for_task)

    def create_subtasks_tab(self):
        # Панель управления подзадачами
        control_frame = ttk.Frame(self.subtasks_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(control_frame, text="Добавить подзадачу", command=self.show_add_subtask_dialog).pack(side=tk.LEFT,
                                                                                                        padx=2)
        ttk.Button(control_frame, text="Редактировать", command=self.show_edit_subtask_dialog).pack(side=tk.LEFT,
                                                                                                    padx=2)
        ttk.Button(control_frame, text="Удалить", command=self.delete_subtask).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Обновить список", command=self.load_subtasks).pack(side=tk.LEFT, padx=2)

        # Таблица подзадач
        self.subtasks_tree = ttk.Treeview(self.subtasks_tab, columns=("description", "status", "task"), show="headings")
        self.subtasks_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.subtasks_tree.heading("description", text="Описание")
        self.subtasks_tree.heading("status", text="Статус")
        self.subtasks_tree.heading("task", text="Задача")

        self.subtasks_tree.column("description", width=500)
        self.subtasks_tree.column("status", width=150)
        self.subtasks_tree.column("task", width=300)

    def create_analytics_tab(self):
        # Аналитика по сотрудникам
        emp_frame = ttk.LabelFrame(self.analytics_tab, text="Самые активные сотрудники")
        emp_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(emp_frame, text="Количество сотрудников:").pack(side=tk.LEFT, padx=5)
        self.emp_limit = tk.IntVar(value=5)
        ttk.Spinbox(emp_frame, from_=1, to=20, textvariable=self.emp_limit, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Button(emp_frame, text="Показать", command=self.show_active_employees).pack(side=tk.LEFT, padx=5)

        self.emp_tree = ttk.Treeview(emp_frame, columns=("email", "tasks"), show="headings")
        self.emp_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.emp_tree.heading("email", text="Email сотрудника")
        self.emp_tree.heading("tasks", text="Количество задач")

        # Аналитика по датам
        date_frame = ttk.LabelFrame(self.analytics_tab, text="Задачи по дате создания")
        date_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(date_frame, text="С:").pack(side=tk.LEFT, padx=5)
        self.start_date = ttk.Entry(date_frame, width=10)
        self.start_date.pack(side=tk.LEFT, padx=5)

        ttk.Label(date_frame, text="По:").pack(side=tk.LEFT, padx=5)
        self.end_date = ttk.Entry(date_frame, width=10)
        self.end_date.pack(side=tk.LEFT, padx=5)

        ttk.Button(date_frame, text="Показать", command=self.show_tasks_by_date).pack(side=tk.LEFT, padx=5)

        self.date_tree = ttk.Treeview(date_frame, columns=("description", "status", "date", "employee"),
                                      show="headings")
        self.date_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.date_tree.heading("description", text="Описание")
        self.date_tree.heading("status", text="Статус")
        self.date_tree.heading("date", text="Дата создания")
        self.date_tree.heading("employee", text="Сотрудник")

    def load_tasks(self):
        # Очищаем текущий список
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)

        # Загружаем задачи из БД
        tasks = self.manager.get_all_tasks()
        for task in tasks:
            # Получаем email сотрудника, если он есть
            employee_email = ""
            if task['fk_employee_id']:
                employee = self.get_employee_by_id(task['fk_employee_id'])
                if employee:
                    employee_email = employee['employee_email']

            self.tasks_tree.insert("", tk.END,
                                   values=(task['task_description'],
                                           task['task_status'],
                                           str(task['task_creation_date']),
                                           employee_email),
                                   iid=f"task_{task['task_id']}")

    def load_subtasks(self, task_id=None):
        # Очищаем текущий список
        for item in self.subtasks_tree.get_children():
            self.subtasks_tree.delete(item)

        # Загружаем подзадачи из БД
        subtasks = self.manager.get_all_subtasks(task_id)
        for subtask in subtasks:
            # Получаем описание родительской задачи
            task_desc = ""
            if subtask['fk_task_id']:
                task = self.manager.get_task(subtask['fk_task_id'])
                if task:
                    task_desc = task['task_description'][:50] + "..." if len(task['task_description']) > 50 else task[
                        'task_description']

            self.subtasks_tree.insert("", tk.END,
                                      values=(subtask['subtask_description'],
                                              "Выполнена" if subtask['subtask_status'] else "Не выполнена",
                                              task_desc),
                                      iid=f"subtask_{subtask['subtask_id']}")

    def load_subtasks_for_task(self, event):
        # Получаем выбранную задачу
        selected_item = self.tasks_tree.selection()
        if not selected_item:
            return

        # Извлекаем ID задачи из iid
        task_id = int(selected_item[0].split("_")[1])

        # Переключаемся на вкладку подзадач
        self.notebook.select(self.subtasks_tab)

        # Загружаем подзадачи для выбранной задачи
        self.load_subtasks(task_id)

    def show_active_employees(self):
        # Очищаем текущий список
        for item in self.emp_tree.get_children():
            self.emp_tree.delete(item)

        # Загружаем данные из БД
        limit = self.emp_limit.get()
        employees = self.manager.get_most_active_employees(limit)

        if not employees:
            messagebox.showinfo("Информация", "Нет данных для отображения")
            return

        for emp in employees:
            self.emp_tree.insert("", tk.END,
                                 values=(emp['employee_email'],
                                         emp['total_tasks']))

    def show_tasks_by_date(self):
        # Очищаем текущий список
        for item in self.date_tree.get_children():
            self.date_tree.delete(item)

        # Получаем даты из полей ввода
        start_date = self.start_date.get()
        end_date = self.end_date.get() or None

        if not start_date:
            messagebox.showerror("Ошибка", "Введите начальную дату")
            return

        # Загружаем данные из БД
        tasks = self.manager.get_tasks_after_date(start_date, end_date)

        if not tasks:
            messagebox.showinfo("Информация", "Нет задач в указанный период")
            return

        for task in tasks:
            # Получаем email сотрудника, если он есть
            employee_email = ""
            if task['fk_employee_id']:
                employee = self.get_employee_by_id(task['fk_employee_id'])
                if employee:
                    employee_email = employee['employee_email']

            self.date_tree.insert("", tk.END,
                                  values=(task['task_description'],
                                          task['task_status'],
                                          str(task['task_creation_date']),
                                          employee_email))

    def show_add_task_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить задачу")
        dialog.geometry("400x300")

        ttk.Label(dialog, text="Описание:").pack(pady=(10, 0))
        description = tk.Text(dialog, height=5, width=40)
        description.pack(padx=10, pady=5)

        ttk.Label(dialog, text="Статус:").pack()
        status = ttk.Entry(dialog)
        status.pack(padx=10, pady=5)

        ttk.Label(dialog, text="Дата создания (ГГГГ-ММ-ДД):").pack()
        date = ttk.Entry(dialog)
        date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date.pack(padx=10, pady=5)

        ttk.Label(dialog, text="Email сотрудника (необязательно):").pack()
        employee_email = ttk.Entry(dialog)
        employee_email.pack(padx=10, pady=5)

        def save_task():
            desc = description.get("1.0", tk.END).strip()
            stat = status.get().strip()
            dt = date.get().strip()
            emp_email = employee_email.get().strip()

            if not desc or not stat or not dt:
                messagebox.showerror("Ошибка", "Заполните обязательные поля")
                return

            emp_id = None
            if emp_email:
                emp = self.get_employee_by_email(emp_email)
                if not emp:
                    messagebox.showerror("Ошибка", "Сотрудник с таким email не найден")
                    return
                emp_id = emp['employee_id']

            try:
                task_id = self.manager.create_task(desc, stat, dt, emp_id)
                if task_id:
                    messagebox.showinfo("Успех", "Задача успешно добавлена")
                    self.load_tasks()
                    dialog.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить задачу: {e}")

        ttk.Button(dialog, text="Сохранить", command=save_task).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

    def show_edit_task_dialog(self):
        selected_item = self.tasks_tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите задачу для редактирования")
            return

        # Извлекаем ID задачи из iid
        task_id = int(selected_item[0].split("_")[1])
        task = self.manager.get_task(task_id)
        if not task:
            messagebox.showerror("Ошибка", "Задача не найдена")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать задачу")
        dialog.geometry("400x300")

        ttk.Label(dialog, text="Описание:").pack(pady=(10, 0))
        description = tk.Text(dialog, height=5, width=40)
        description.insert("1.0", task['task_description'])
        description.pack(padx=10, pady=5)

        ttk.Label(dialog, text="Статус:").pack()
        status = ttk.Entry(dialog)
        status.insert(0, task['task_status'])
        status.pack(padx=10, pady=5)

        ttk.Label(dialog, text="Email сотрудника:").pack()
        employee_email = ttk.Entry(dialog)
        if task['fk_employee_id']:
            employee = self.get_employee_by_id(task['fk_employee_id'])
            if employee:
                employee_email.insert(0, employee['employee_email'])
        employee_email.pack(padx=10, pady=5)

        def save_changes():
            desc = description.get("1.0", tk.END).strip()
            stat = status.get().strip()
            emp_email = employee_email.get().strip()

            if not desc or not stat:
                messagebox.showerror("Ошибка", "Заполните обязательные поля")
                return

            emp_id = None
            if emp_email:
                emp = self.get_employee_by_email(emp_email)
                if not emp:
                    messagebox.showerror("Ошибка", "Сотрудник с таким email не найден")
                    return
                emp_id = emp['employee_id']

            try:
                success = self.manager.update_task(task_id, desc, stat, emp_id)
                if success:
                    messagebox.showinfo("Успех", "Задача успешно обновлена")
                    self.load_tasks()
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось обновить задачу")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить задачу: {e}")

        ttk.Button(dialog, text="Сохранить", command=save_changes).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

    def delete_task(self):
        selected_item = self.tasks_tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите задачу для удаления")
            return

        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение", "Удалить выбранную задачу и все её подзадачи?"):
            return

        # Извлекаем ID задачи из iid
        task_id = int(selected_item[0].split("_")[1])

        try:
            success = self.manager.delete_task(task_id)
            if success:
                messagebox.showinfo("Успех", "Задача и все её подзадачи удалены")
                self.load_tasks()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить задачу")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить задачу: {e}")

    def show_add_subtask_dialog(self):
        # Проверяем, выбрана ли задача
        selected_task = self.tasks_tree.selection()
        task_id = None
        task_desc = ""

        if selected_task:
            task_id = int(selected_task[0].split("_")[1])
            task = self.manager.get_task(task_id)
            if task:
                task_desc = task['task_description'][:50] + "..." if len(task['task_description']) > 50 else task[
                    'task_description']

        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить подзадачу")
        dialog.geometry("400x250")

        ttk.Label(dialog, text=f"Для задачи: {task_desc if task_id else 'не выбрана'}").pack(pady=(10, 0))

        if not task_id:
            ttk.Label(dialog, text="Выберите задачу в списке задач", foreground="red").pack()

        ttk.Label(dialog, text="Описание:").pack()
        description = tk.Text(dialog, height=5, width=40)
        description.pack(padx=10, pady=5)

        status_var = tk.BooleanVar()
        ttk.Checkbutton(dialog, text="Выполнена", variable=status_var).pack()

        def save_subtask():
            if not task_id:
                messagebox.showerror("Ошибка", "Выберите задачу в списке задач")
                return

            desc = description.get("1.0", tk.END).strip()
            if not desc:
                messagebox.showerror("Ошибка", "Введите описание подзадачи")
                return

            try:
                subtask_id = self.manager.create_subtask(task_id, desc, status_var.get())
                if subtask_id:
                    messagebox.showinfo("Успех", "Подзадача успешно добавлена")
                    self.load_subtasks(task_id)
                    dialog.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить подзадачу: {e}")

        ttk.Button(dialog, text="Сохранить", command=save_subtask).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

    def show_edit_subtask_dialog(self):
        selected_item = self.subtasks_tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите подзадачу для редактирования")
            return

        # Извлекаем ID подзадачи из iid
        subtask_id = int(selected_item[0].split("_")[1])
        subtask = self.manager.get_subtask(subtask_id)
        if not subtask:
            messagebox.showerror("Ошибка", "Подзадача не найдена")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать подзадачу")
        dialog.geometry("400x250")

        ttk.Label(dialog, text="Описание:").pack(pady=(10, 0))
        description = tk.Text(dialog, height=5, width=40)
        description.insert("1.0", subtask['subtask_description'])
        description.pack(padx=10, pady=5)

        status_var = tk.BooleanVar(value=subtask['subtask_status'])
        ttk.Checkbutton(dialog, text="Выполнена", variable=status_var).pack()

        def save_changes():
            desc = description.get("1.0", tk.END).strip()
            if not desc:
                messagebox.showerror("Ошибка", "Введите описание подзадачи")
                return

            try:
                success = self.manager.update_subtask(subtask_id, desc, status_var.get())
                if success:
                    messagebox.showinfo("Успех", "Подзадача успешно обновлена")
                    self.load_subtasks(subtask['fk_task_id'])
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось обновить подзадачу")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить подзадачу: {e}")

        ttk.Button(dialog, text="Сохранить", command=save_changes).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

    def delete_subtask(self):
        selected_item = self.subtasks_tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите подзадачу для удаления")
            return

        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение", "Удалить выбранную подзадачу?"):
            return

        # Извлекаем ID подзадачи из iid
        subtask_id = int(selected_item[0].split("_")[1])

        try:
            success = self.manager.delete_subtask(subtask_id)
            if success:
                messagebox.showinfo("Успех", "Подзадача удалена")
                # Получаем task_id для обновления списка
                subtask = self.manager.get_subtask(subtask_id)
                if subtask and subtask['fk_task_id']:
                    self.load_subtasks(subtask['fk_task_id'])
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить подзадачу")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить подзадачу: {e}")

    def get_employee_by_id(self, employee_id):
        """Получаем данные сотрудника по ID"""
        self.manager.cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (employee_id,))
        return self.manager.cursor.fetchone()

    def get_employee_by_email(self, email):
        """Получаем данные сотрудника по email"""
        self.manager.cursor.execute("SELECT * FROM employees WHERE employee_email = %s", (email,))
        return self.manager.cursor.fetchone()


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerGUI(root)
    root.mainloop()