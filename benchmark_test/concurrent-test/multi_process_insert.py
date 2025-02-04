from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
import numpy as np
from multiprocessing import Process
from multiprocessing import Pool, cpu_count
import time
import logging
import os
import sys

logging.basicConfig(filename='benchmark.log', level=logging.DEBUG)

MILVUS_HOST = "127.0.0.1"
MILVUS_PORT = 19530
DIM = 768

SHARD_NUM = 5

TOTAL_NUM = 1000000
BATCH_SIZE = 10000
PROCESS_NUM = 10

def create_collection(collection_name, dim=768):
    try:
        connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
        if not utility.has_collection(collection_name):
            field1 = FieldSchema(name="id", dtype=DataType.INT64, descrition="int64", is_primary=True, auto_id=True)
            field2 = FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, descrition="float vector", dim=dim,
                                 is_primary=False)
            schema = CollectionSchema(fields=[field1, field2], description="collection description")
            collection = Collection(name=collection_name, schema=schema, shards_num=SHARD_NUM)
            print("Create Milvus collection: {}".format(collection))
            return collection
    except Exception as e:
        logging.error("Failed to create milvus collection: {}".format(e))
        sys.exit(1)


def sub_insert(task_id, col_name):
    print("task_id {}, sub process {}".format(task_id, os.getpid()))
    vec = np.random.random((BATCH_SIZE, DIM)).tolist()
    connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
    collection = Collection(name=col_name)
    time_start = time.time()
    mr = collection.insert([vec])
    # ids = mr.primary_keys
    time_end = time.time()
    print("task {} cost time: {}".format(task_id, time_end - time_start))
    logging.info("task {}, process {}, insert number:{},insert time:{}".format(task_id, os.getpid(), len(ids),
                                                                               time_end - time_start))


def multi_insert_pool(collection_name):
    p = Pool(PROCESS_NUM)
    begin_time = time.time()
    loop = TOTAL_NUM // BATCH_SIZE
    print(loop)
    for i in range(loop):
        p.apply_async(sub_insert, (i, collection_name,))
    p.close()
    p.join()
    print("total cost time: {}".format(time.time() - begin_time))


if __name__ == "__main__":
    # collection_name = "concurrent_insert_0"
    collection_name = "test2"
    # create_collection(collection_name)
    multi_insert_pool(collection_name)
