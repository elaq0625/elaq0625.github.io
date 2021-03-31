# test_fixture.py
import pytest
import os
import smtplib


# yield - Teardown
@pytest.fixture
def make_directory_and_txt_file_yield():
    directory_name = "/data/"
    directory_path = os.getcwd()+directory_name
    try:
        if not(os.path.isdir(directory_path)):
            os.makedirs(os.path.join(directory_path))
            print("\nmake directory", directory_path)
    except Exception as e:
        print("make_directory() has error \n error message: {}".format(e))    
    
    file_name = "temp_data.txt"
    print("make file", file_name)
    f = open(directory_path+file_name, 'w')
    yield f

    f.close()
    os.remove(directory_path+file_name)
    print("\ndelete temp file ", directory_path+file_name)
    os.rmdir(directory_path)
    print("delete directory ", directory_path)
    print("teardown complete")


def test_file_write_yield(make_directory_and_txt_file_yield):
    file_pointer = make_directory_and_txt_file_yield
    file_pointer.write("data write")
    print("data write to file")


# request.addfinalizer - Teardown
@pytest.fixture
def make_directory_and_txt_file_addfinalizer(request):
    directory_name = "/data/"
    directory_path = os.getcwd()+directory_name
    try:
        if not(os.path.isdir(directory_path)):
            os.makedirs(os.path.join(directory_path))
            print("\nmake directory", directory_path)
    except Exception as e:
        print("make_directory() has error \n error message: {}".format(e))    
    
    file_name = "temp_data.txt"
    print("make file", file_name)
    f = open(directory_path+file_name, 'w')

    def teardown():
        f.close()
        os.remove(directory_path+file_name)
        print("\ndelete temp file ", directory_path+file_name)
        os.rmdir(directory_path)
        print("delete directory ", directory_path)
        print("teardown complete")

    request.addfinalizer(teardown)

    return f

    
def test_file_write_addfinalizer(make_directory_and_txt_file_addfinalizer):
    file_pointer = make_directory_and_txt_file_addfinalizer
    file_pointer.write("data write")
    print("data write to file")