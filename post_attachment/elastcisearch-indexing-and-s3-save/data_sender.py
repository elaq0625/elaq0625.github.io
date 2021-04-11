import boto3
import json
import sys
import os

DATA_STREAM_NAME = "kevin-datastream-test"

def get_filelist_from_directory_path(dir_path):
    filelist = list()
    for (path, dir, files) in os.walk(dir_path):
        for filename in files:
            if filename[0] != "." and ".log" in filename:
                filelist.append("%s/%s" % (path, filename))
    return filelist


def get_datalist_from_filelist(filelist):
    datalist = list()

    for filename in filelist:
        with open(filename, "r") as opened_file:
            filecontents = opened_file.read()
            datalist.append(filecontents)

    return datalist


def get_datastream_client():
    session = boto3.Session()
    kinesis = session.client("kinesis")
    return kinesis


def put_records_to_data_stream(datalist):
    records_list = [
        {"Data": data, "PartitionKey": "This is Partition Key"} for data in datalist]

    kinesis = get_datastream_client()

    response = kinesis.put_records(
        StreamName=DATA_STREAM_NAME,
        Records=records_list
    )

    print("Send to Data Stream : {}".format(records_list))
    print(response)


def main():
    dir_path = "./input"

    filelist = get_filelist_from_directory_path(dir_path)
    datalist = get_datalist_from_filelist(filelist)
    put_records_to_data_stream(datalist)


if __name__ == "__main__":
    main()