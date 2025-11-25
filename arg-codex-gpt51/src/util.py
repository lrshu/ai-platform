import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Iterable, List, Any
from functools import partial

from tqdm import tqdm

async def thread_pool_runner(
    func: Callable,
    tasks: Iterable[Any],
    max_workers: int = 5,
    *args,
    progress_label: str | None = None,
    **kwargs,
) -> List[Any]:
    """
    并发运行阻塞函数，并支持传递额外参数。
    
    :param func: 要运行的函数，第一个参数必须是任务项 (task)
    :param tasks: 任务列表 (task_list)
    :param max_workers: 线程池并发数
    :param args: 传递给 func 的额外位置参数
    :param kwargs: 传递给 func 的额外关键字参数
    :return: 结果列表
    """
    loop = asyncio.get_running_loop()
    task_list = list(tasks)
    total = len(task_list)
    label = f"[{progress_label}] " if progress_label else ""

    if total == 0:
        return []

    progress_bar = tqdm(total=total, desc=progress_label or "thread-pool", unit="task")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 使用 lambda 包装 func，将固定参数 (*args, **kwargs) 闭包进去
        # 这里的 t 代表 tasks 列表中的每一个 item
        completed = 0

        def _report_progress(_future: asyncio.Future):
            nonlocal completed
            completed += 1
            progress_bar.update(1)

        futures = [
            loop.run_in_executor(
                executor, 
                lambda t: func(t, *args, **kwargs), 
                task,
            )
            for task in task_list
        ]

        for future in futures:
            future.add_done_callback(_report_progress)
        
        try:
            results = await asyncio.gather(*futures, return_exceptions=True)
        finally:
            progress_bar.close()
        
    print(f"{label}✅ 并行任务完成: {len(results)} 个结果")
    return results
