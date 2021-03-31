import sys
import json
import random

from datetime import datetime
from time import sleep, time


def make_borad_id_pattern_random_datum(field_name, id_length):
    alphanumeric = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-'
    result_datum = dict()

    result_list = [random.choice(alphanumeric) for i in range(id_length - 1)]
    result_list.append(random.choice(alphanumeric[:-1]))

    result_datum[field_name] = "".join(result_list)

    return result_datum


def make_integer_random_datum(field_name, boundary_min, boundary_max):
    result_datum = dict()

    result_datum[field_name] = random.randint(boundary_min, boundary_max)

    return result_datum

def make_integer_random_datum_return_to_string_type(field_name, boundary_min, boundary_max):
    result_datum = dict()

    result_datum[field_name] = str(random.randint(boundary_min, boundary_max))

    return result_datum


def make_timestamp_pattern_random_datum(field_name, date_begin, date_end):
    epoch_date_begin = int(datetime.strptime(
        date_begin, "%Y-%m-%dT%H:%M:%SZ").timestamp())
    epoch_date_end = int(datetime.strptime(
        date_end, "%Y-%m-%dT%H:%M:%SZ").timestamp())

    random_date = random.randint(epoch_date_begin, epoch_date_end)

    result_datum = dict()
    result_datum[field_name] = datetime.fromtimestamp(
        random_date).strftime('%Y-%m-%dT%H:%M:%SZ')

    return result_datum


def make_selecting_predefine_random_datum(field_name_list, predefine_list):
    result_datum_list = dict()

    predefine_index = random.randint(0, len(predefine_list) - 1)
    selected_predefine = predefine_list[predefine_index]

    for i, key_name in enumerate(field_name_list):
        result_datum_list[key_name] = selected_predefine[i]

    return result_datum_list


def get_epoch_generate_fucntion_mapping():
    mapping_list = list()

    board_id_generator_datum_info = {
        "function": make_integer_random_datum,
        "parameter": {
            "field_name": "board_id",
            "boundary_min": 1,
            "boundary_max": 10000000,
        }
    }

    playtime_generator_datum_info = {
        "function": make_selecting_predefine_random_datum,
        "parameter": {
            "field_name_list": ["playtime", "minimum_play"],
            "predefine_list": [
                [0, "N"], [1, "N"], [2, "N"], [3, "N"], 
                [4, "N"], [5, "N"], [6, "N"], [7, "N"],  
                [8, "Y"],  [9, "Y"],  [10, "Y"], [11, "Y"], 
                [12, "Y"], [13, "Y"], [14, "Y"], [15, "Y"]
            ]
        }
    }

    timestamp_generator_datum_info = {
        "function": make_timestamp_pattern_random_datum,
        "parameter": {
            "field_name": "timestamp",
            "date_begin": "2019-01-01T00:00:0Z",
            "date_end": "2019-11-14T23:59:59Z"
        }
    }

    user_id_generator_datum_info = {
        "function": make_integer_random_datum,
        "parameter": {
            "field_name": "user_id",
            "boundary_min": 1,
            "boundary_max": 1000000,
        }
    }

    interest_generator_datum_info = {
        "function": make_selecting_predefine_random_datum,
        "parameter": {
            "field_name_list": ["interest"],
            "predefine_list": [
                [100], [101], [102],
                [103], [104], [105],
                [106], [107], [108],
                [109], [110], [111]
            ]
        }
    }

    mapping_list.append(board_id_generator_datum_info)
    mapping_list.append(playtime_generator_datum_info)
    mapping_list.append(timestamp_generator_datum_info)
    mapping_list.append(user_id_generator_datum_info)
    mapping_list.append(interest_generator_datum_info)

    return mapping_list


def main():
    directory_path = "./source"
    batch_count = 60
    line_count = 250

    sys_arg = sys.argv

    if len(sys_arg) > 2:
        batch_count = int(sys_arg[1])
        line_count = int(sys_arg[2])

    epoch_generate_mapping = get_epoch_generate_fucntion_mapping()

    for batch_index in range(batch_count):
        epoch_start_time = time()

        file_name = "test{}.log".format(batch_index)
        file_path = "/".join([directory_path, file_name])

        with open(file_path, "w", encoding='UTF-8') as writting_file:
            for _ in range(line_count):
                data_epoch = dict()

                for mapping_info in epoch_generate_mapping:
                    generate_function = mapping_info["function"]
                    parameters = mapping_info["parameter"]

                    datum = generate_function(**parameters)

                    data_epoch.update(datum)

                json_data_epoch = json.dumps(data_epoch, ensure_ascii=False)

                writting_file.write("".join([json_data_epoch, '\n']))

        epoch_elapsed_time = time() - epoch_start_time
        print("%12s - make random data file elapsed time : %.3f" % (file_name, epoch_elapsed_time))
        sleep(0.999 - epoch_elapsed_time)


if __name__ == "__main__":
    main()