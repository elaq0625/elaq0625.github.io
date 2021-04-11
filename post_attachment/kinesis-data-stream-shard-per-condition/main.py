import multiprocessing
import time
import sys
import os
import boto3
import json
from math import floor

multiprocessing.set_start_method('spawn', True)

# def get_time_now():
#     return time.time()
AWS_PROFILE_NAME = "st_kevin"
DATA_STREAM_NAME = "kevin-datastream-test"
PARTITION_KEY_BASE = "kevin-datastream-test"

get_time_now = time.time


def get_kinesis_client():
    session = boto3.Session(profile_name=AWS_PROFILE_NAME)
    kinesis = session.client("kinesis")
    return kinesis


def read_datarecords_from_file(filename):
    records_list = None
    with_partition_key_records_list = list()

    with open(filename, "r", encoding='UTF-8') as fileobject:
        lines = fileobject.readlines()
        records_list = list(map(json.loads, lines))

    for i, record in enumerate(records_list):
        with_partition_key_records_list.append({
            "Data": json.dumps(record, ensure_ascii=False),
            "PartitionKey": " ".join([PARTITION_KEY_BASE, str(i)])
        }
        )

    return with_partition_key_records_list


def put_datastream_everyseconds(index, timetable, records_list):
    pid = os.getpid()
    records_list_count = len(records_list)

    writelines_list = list()

    writelines_list.append("process id : {}\n".format(pid))

    kinesis = get_kinesis_client()

    total_success_count = 0
    total_fail_count = 0

    for epoch_time in timetable:
        while True:
            start_time = get_time_now()
            if start_time >= epoch_time:
                response = kinesis.put_records(
                    StreamName=DATA_STREAM_NAME, Records=records_list)
                elapsed_time = get_time_now() - start_time

                failed_count = response["FailedRecordCount"]
                success_count = records_list_count - failed_count

                total_fail_count += failed_count
                total_success_count += success_count

                writelines_list.append("%20.3f \t %20.3f \t %5d \t %5d \n" % (
                    start_time, elapsed_time, success_count, failed_count))
                break

    writelines_list.append("total_sucsess_count : {} \t total_fail_count : {} \n".format(
        total_success_count, total_fail_count))

    result_filename = "".join(["response_result_", str(index), ".log"])

    with open(result_filename, "w") as result_file:
        result_file.writelines(writelines_list)


if __name__ == '__main__':
    sys_argv = sys.argv

    process_count = 3
    delay_process_start_time = 5.
    duration_process_time = 60
    datarecords_filename = "datarecord_file.log"

    process_start_time = float(
        floor(get_time_now() + delay_process_start_time))
    records_list = read_datarecords_from_file(datarecords_filename)

    time_table = [(process_start_time + i)
                  for i in range(duration_process_time)]

    print(time_table)

    procs = list()

    for index in range(process_count):
        proc = multiprocessing.Process(target=put_datastream_everyseconds, args=(
            index, time_table, records_list))

        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()