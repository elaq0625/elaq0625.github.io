import random
import sys
import datetime
import time

def main():
    sys_argv = sys.argv
    batch_count = 5
    make_log_running_time = 60
    log_file_dir_path = "./"

    if len(sys_argv) > 3:
        batch_count = int(sys_argv[1])
        make_log_running_time = int(sys_argv[2])
        log_file_dir_path = sys_argv[3]

    choice_list = ["c++", "python", "java",
                   "javascript", "kotlin", "scala", "ruby"]

    now_date = datetime.datetime.today()
    filename = "".join([log_file_dir_path, str(now_date.date()), ".log"])

    for batch_no in range(batch_count):
        with open(filename, "a") as file_object:
            for i in range(make_log_running_time):
                time.sleep(0.999999)
                created_at = time.strftime("%Y/%m/%dT%H:%M:%S")
                log_message = "{}-{}    {}    {}\n".format(
                    batch_no, i, created_at, random.choice(choice_list))
                file_object.write(log_message)
    print("make log end!")


if __name__ == "__main__":
    main()