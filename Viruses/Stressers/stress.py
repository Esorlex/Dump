import multiprocessing
import os

def stress_cpu():
    while True:
        pass  

def stress_memory():
    try:
        mem_eater = []
        while True:
            mem_eater.append(bytearray(10000 * 10240 * 10240))
    except MemoryError:
        pass

if __name__ == "__main__":
    cpu_count = multiprocessing.cpu_count()

    cpu_processes = [multiprocessing.Process(target=stress_cpu) for _ in range(cpu_count)]
    for p in cpu_processes:
        p.start()

    mem_process = multiprocessing.Process(target=stress_memory)
    mem_process.start()

    for p in cpu_processes:
        p.join()
    mem_process.join()
