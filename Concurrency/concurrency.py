import numpy as np
import queue
import threading
import multiprocessing
import time

class RequestQueue:
    def __init__(self, maxsize=10, use_multiprocessing=False):
        self.queue = queue.Queue(maxsize=maxsize)
        self.use_multiprocessing = use_multiprocessing
        
        if use_multiprocessing:
            self.process = multiprocessing.Process(target=self.worker)
        else:
            self.thread = threading.Thread(target=self.worker)
        
        self.running = True
    
    def start(self):
        if self.use_multiprocessing:
            self.process.start()
        else:
            self.thread.start()
    
    def stop(self):
        self.running = False
        if self.use_multiprocessing:
            self.process.join()
        else:
            self.thread.join()
    
    def add_request(self, matrix1, matrix2):
        try:
            self.queue.put((matrix1, matrix2), timeout=1)
        except queue.Full:
            print("Queue is full, dropping request")
    
    def worker(self):
        while self.running:
            try:
                matrix1, matrix2 = self.queue.get(timeout=1)
                result = np.matmul(matrix1, matrix2)
                print("Processed matrix multiplication result shape:", result.shape)
                self.queue.task_done()
            except queue.Empty:
                pass

# Test configuration
queue_size = 10000
num_requests = 100
matrix_size = 10000 
use_multiprocessing = False

rq = RequestQueue(maxsize=queue_size, use_multiprocessing=use_multiprocessing)
rq.start()

for _ in range(num_requests):
    A = np.random.rand(matrix_size, matrix_size)
    B = np.random.rand(matrix_size, matrix_size)
    rq.add_request(A, B)
    time.sleep(0.1) 

rq.stop()