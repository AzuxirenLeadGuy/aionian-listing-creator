import queue
import shutil
from typing import Any, Generator

class ProgressWithLogging:
    channel: queue.Queue[str]
    width: int
    def __init__(self):
        self.channel = queue.Queue()
        self.width = shutil.get_terminal_size()[0]
    def run_progress(self, items:list[Any])->Generator[Any]:
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
        # pc.channel.put("")
        pc.channel.put(f"Processing item: {item}")
        time.sleep(item)
