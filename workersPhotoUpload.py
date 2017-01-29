import boto3
from datetime import datetime
import uuid
import sys
import io
import time
import threading
import queueFotos
from boto.s3.connection import S3Connection
import S3

bucketName = "picamtgk"

# number of worker threads to complete the processing
num_worker_threads = 3

# process that each worker thread will execute until the Queue is empty
def worker(hostname):
    while True:
        # get item from queue, do work on it, let queue know processing is done for one item
        item = queueFotos.myQueue.get()
        # Pujem la foto al S3.
        i = datetime.now()

        stringNom = hostname + "_" + i.strftime('%Y_%m_%d__%H_%M_%S_%f') + '.jpeg'

        # Per pujar al Amaozn S3
        S3.uploadStreamToBucket(bucketName,stringNom,item)
        #S3.saveToFileLocal(bucketName,stringNom,item)


# launch all of our queued processes
def main(hostname):
    # Launches a number of worker threads to perform operations using the queue of inputs
    for i in range(num_worker_threads):
         t = threading.Thread(target=worker, args=(hostname,))
         t.daemon = True
         t.start()
    print "Workers per pujar fotos al S3 iniciats."
    # put items on the input queue (numbers to be squared)
#    for item in range(10):
#        q_in.put(item)

    # wait for two queues to be emptied (and workers to close)   
    queueFotos.myQueue.join()       # block until all tasks are done
