"""This file contains a custom implementation of a progress bar"""

import queue
import shutil
from collections.abc import Generator
from typing import Any


class ProgressWithLogging:
    """
    A progress bar that shows the progress and a log entry
    """
    channel: queue.Queue[str]
    width: int
    def __init__(self):
        """Creates a progress bar instance"""
        self.channel = queue.Queue()
        self.width = shutil.get_terminal_size()[0]
    def run_progress(self, items:list[Any])->Generator[Any]:
        """
        Updates the state of the progress bar

        Args:
            items (list[Any]): The generator/list being processed

        Yields:
            Generator[Any]: The iterator for the inner list, with progress being shown
        """
        def print_progress(perc:float):
            message = '\r'
            if self.width > 10:
                actual_width = self.width - 9
                active = int(perc * actual_width)
                blank = actual_width - active
                message = ('#' * active) + (' ' * blank)
                message = f'\r[{message}]'
            message += f"{(100 * perc):6.2F}%"
            print(message, end='')
        length = len(items)
        for itr, item in enumerate(items):
            print_progress(itr/length)
            yield item
            while self.channel.qsize() > 0:
                print(f"\rLog: {self.channel.get().ljust(self.width - 5)}")
        print_progress(1.0)
        print("\nTask completed!")


if __name__ == '__main__':
    import time
    delay_secs = [1.2, .2, .4, 1.7, 2.9, 1.5]
    pc = ProgressWithLogging()
    for item in pc.run_progress(delay_secs):
        pc.channel.put(f"Processing item: {item}")
        time.sleep(item)
