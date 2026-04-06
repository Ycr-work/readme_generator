import os
import time

from typing import List

from readme_generator.type import Run_code

def check_run(run_inform:Run_code):
    pass

def wait_next_run(state):
    print("## Waiting for 180 seconds")
    time.sleep(180)
    return state