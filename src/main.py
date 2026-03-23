import asyncio
from typing import List, Any, Callable, Coroutine
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

@dataclass
class Task:
    func: Callable
    args: tuple
    priority: int = 0

class TaskQueue:
    def __init__(self, max_workers: int = 4):
        self.tasks: List[Task] = []
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running = False

    async def add_task(self, func: Callable, *args, priority: int = 0):
        task = Task(func=func, args=args, priority=priority)
        self.tasks.append(task)
        self.tasks.sort(key=lambda x: x.priority, reverse=True)

    async def process_tasks(self) -> List[Any]:
        if not self.tasks:
            return []

        self.running = True
        results = []

        while self.tasks and self.running:
            current_tasks = self.tasks[:self.executor._max_workers]
            self.tasks = self.tasks[self.executor._max_workers:]

            futures = []
            for task in current_tasks:
                future = self.executor.submit(task.func, *task.args)
                futures.append(future)

            for future in futures:
                try:
                    result = await asyncio.wrap_future(future)
                    results.append(result)
                except Exception as e:
                    results.append(e)

        return results

    def stop(self):
        self.running = False

async def main():
    # Example usage
    queue = TaskQueue(max_workers=2)

    def example_task(x: int) -> int:
        return x * 2

    # Add some sample tasks
    await queue.add_task(example_task, 1, priority=2)
    await queue.add_task(example_task, 2, priority=1)
    await queue.add_task(example_task, 3, priority=3)

    # Process all tasks and get results
    results = await queue.process_tasks()
    print(f"Results: {results}")

if __name__ == "__main__":
    asyncio.run(main())
