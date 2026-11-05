from dataclasses import dataclass
from enum import Enum


class TaskPriority(Enum):
    LOW = "Низький"
    MEDIUM = "Середній"
    HIGH = "Високий"
    CRITICAL = "Критичний"


class TaskStatus(Enum):
    TODO = "До виконання"
    IN_PROGRESS = "В роботі"
    DONE = "Виконано"


@dataclass
class Task:
    """Модель завдання проєкту для демонстрації роботи колекції в ЛР №5."""
    task_id: str
    title: str
    assignee: str
    priority: TaskPriority
    estimated_hours: float
    is_overdue: bool = False
    status: TaskStatus = TaskStatus.TODO

    def get_info(self) -> str:
        overdue_str = "ПРОСТРОЧЕНО" if self.is_overdue else "Вчасно"
        return (
            f"[{self.task_id}] '{self.title}' | Виконавець: {self.assignee} | "
            f"Пріоритет: {self.priority.value} | Час: {self.estimated_hours} год | "
            f"Статус: {self.status.value} | Термін: {overdue_str}"
        )


# === ЧАСТИНА 1: ФУНКТОР (БІЗНЕС-ЛОГІКА ЗІ ЗБЕРЕЖЕННЯМ СТАНУ) ===
class TaskCostEstimator:
    """Функтор для розрахунку вартості виконання завдання та обліку бюджету."""

    def __init__(self, hourly_rate: float = 500.0):
        self.hourly_rate = float(hourly_rate)
        self.calls_count = 0
        self.total_estimated_cost = 0.0
        self.history: list[str] = []

    def __call__(self, task: Task) -> float:
        self.calls_count += 1
        multipliers = {
            TaskPriority.LOW: 1.0,
            TaskPriority.MEDIUM: 1.2,
            TaskPriority.HIGH: 1.5,
            TaskPriority.CRITICAL: 2.0,
        }
        weight = multipliers[task.priority]
        cost = round(task.estimated_hours * self.hourly_rate * weight, 2)
        self.total_estimated_cost = round(self.total_estimated_cost + cost, 2)
        record = (
            f"Виклик #{self.calls_count}: [{task.task_id}] '{task.title}' "
            f"({task.priority.value}, x{weight}) -> {cost} грн"
        )
        self.history.append(record)
        return cost

    def get_stats(self) -> str:
        lines = [
            f"Кількість викликів функтора: {self.calls_count}",
            f"Накопичений бюджет проєкту: {self.total_estimated_cost} грн",
            "Історія розрахунків:",
        ]
        for item in self.history:
            lines.append(f"  - {item}")
        return "\n".join(lines)


# === ЧАСТИНА 2: ВЛАСНИЙ ІТЕРАТОР (ФІЛЬТРАЦІЯ НЕВИКОНАНИХ ЗАВДАНЬ) ===
class PendingTaskIterator:
    """Кастомний ітератор для обходу лише невиконаних завдань проєкту."""

    def __init__(self, tasks: list[Task]):
        self.tasks = tasks
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self) -> Task:
        while self.index < len(self.tasks):
            current_task = self.tasks[self.index]
            self.index += 1
            if current_task.status != TaskStatus.DONE:
                return current_task
        raise StopIteration


# === ЧАСТИНА 3: КЛАС-МЕНЕДЖЕР ТА ГЕНЕРАТОРИ (ОПТИМІЗАЦІЯ ПАМ'ЯТІ) ===
class ProjectManager:
    """Клас-менеджер проєкту з підтримкою функтора, ітератора та генераторів."""

    def __init__(self, project_name: str, hourly_rate: float = 500.0):
        self.project_name = project_name
        self._tasks: list[Task] = []
        self.estimator = TaskCostEstimator(hourly_rate=hourly_rate)

    def add_task(self, task: Task) -> float:
        self._tasks.append(task)
        return self.estimator(task)

    def change_status(self, index: int, new_status: TaskStatus) -> Task:
        if index < 0 or index >= len(self._tasks):
            raise IndexError("Завдання з вказаним порядковим номером не існує!")
        self._tasks[index].status = new_status
        return self._tasks[index]

    def get_pending_tasks(self) -> PendingTaskIterator:
        return PendingTaskIterator(self._tasks)

    def generate_overdue_tasks(self):
        for task in self._tasks:
            if task.is_overdue:
                yield task

    def generate_tasks_by_assignee(self, assignee_name: str):
        target = assignee_name.strip().lower()
        for task in self._tasks:
            if task.assignee.lower() == target:
                yield task

    def show_all(self) -> None:
        print(f"\n=== УСІ ЗАВДАННЯ ПРОЄКТУ '{self.project_name}' ===")
        if not self._tasks:
            print("Список завдань порожній.")
            return
        for idx, t in enumerate(self._tasks, 1):
            print(f"{idx}. {t.get_info()}")


# === ЧАСТИНА 4: ІНТЕРАКТИВНЕ КОНСОЛЬНЕ МЕНЮ (CLI) ===
def select_priority() -> TaskPriority:
    print("Пріоритет: 1. Низький | 2. Середній | 3. Високий | 4. Критичний")
    choice = input("Ваш вибір (1-4): ").strip()
    mapping = {
        "1": TaskPriority.LOW,
        "2": TaskPriority.MEDIUM,
        "3": TaskPriority.HIGH,
        "4": TaskPriority.CRITICAL,
    }
    return mapping.get(choice, TaskPriority.MEDIUM)


if __name__ == "__main__":
    manager = ProjectManager("ERP-System v2.0", hourly_rate=500.0)
    print(f"=== Система управління завданнями проєкту (ЛР №5) ===")

    while True:
        print("\nОберіть дію:")
        print("1. Додати завдання та оцінити вартість (Функтор)")
        print("2. Змінити статус завдання")
        print("3. Показати статистику та історію стану Функтора")
        print("4. Вивести невиконані завдання (Власний Ітератор)")
        print("5. Пошук прострочених / за виконавцем (Генератор yield)")
        print("6. Показати всі завдання проєкту")
        print("7. Вийти з програми")
        choice = input("Ваш вибір (1-7): ").strip()

        try:
            if choice == "1":
                t_id = input("Код завдання (напр. T-101): ").strip()
                title = input("Назва завдання: ").strip()
                assignee = input("ПІБ виконавця: ").strip()
                hours = float(input("Плановий час (год): ").strip())
                priority = select_priority()
                overdue_in = input("Чи прострочене? (y/n): ").strip().lower()
                task = Task(t_id, title, assignee, priority, hours, overdue_in == "y")
                cost = manager.add_task(task)
                print(f"[Успіх] Додано: {task.get_info()}")
                print(
                    f"[Функтор] Вартість: {cost} грн | Викликів: {manager.estimator.calls_count} | "
                    f"Бюджет: {manager.estimator.total_estimated_cost} грн"
                )
            elif choice == "2":
                manager.show_all()
                idx = int(input("Номер завдання для зміни статусу: ").strip()) - 1
                print("Новий статус: 1. До виконання | 2. В роботі | 3. Виконано")
                s_choice = input("Статус (1-3): ").strip()
                s_map = {
                    "1": TaskStatus.TODO,
                    "2": TaskStatus.IN_PROGRESS,
                    "3": TaskStatus.DONE,
                }
                updated = manager.change_status(idx, s_map.get(s_choice, TaskStatus.TODO))
                print(f"[Оновлено] Статус '{updated.title}' -> '{updated.status.value}'")
            elif choice == "3":
                print("\n--- ВНУТРІШНІЙ СТАН ФУНКТОРА TaskCostEstimator ---")
                print(manager.estimator.get_stats())
            elif choice == "4":
                print("\n--- НЕВИКОНАНІ ЗАВДАННЯ (PendingTaskIterator) ---")
                for pt in manager.get_pending_tasks():
                    print(pt.get_info())
            elif choice == "5":
                print("1. Прострочені завдання (yield) | 2. Завдання виконавця (yield)")
                g_choice = input("Ваш вибір (1-2): ").strip()
                if g_choice == "1":
                    print("\n--- ПРОСТРОЧЕНІ ЗАВДАННЯ (Генератор yield) ---")
                    for ot in manager.generate_overdue_tasks():
                        print(ot.get_info())
                elif g_choice == "2":
                    target = input("Введіть ПІБ виконавця: ").strip()
                    print(f"\n--- ЗАВДАННЯ ВИКОНАВЦЯ '{target}' (Генератор yield) ---")
                    for at in manager.generate_tasks_by_assignee(target):
                        print(at.get_info())
            elif choice == "6":
                manager.show_all()
            elif choice == "7":
                print("Завершення роботи програми.")
                break
            else:
                print("[Помилка] Некоректний пункт меню. Оберіть число від 1 до 7.")
        except (ValueError, IndexError) as e:
            print(f"[Помилка введення даних]: {e}")