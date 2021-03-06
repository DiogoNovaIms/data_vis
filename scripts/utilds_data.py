import os 
import pickle
import configparser

config = configparser.ConfigParser()

if 'config.ini' in os.listdir():
    config.read('config.ini')

MONTH_LIST = {"January":1,"February":2,"March":3,"April":4,"May":5,
"June":6,"July":7,"August":8,"September":9,"October":10,
"November":11,"December":12}

DATA_PATH = config['path']['data']
RAW_PATH = DATA_PATH + 'raw/'
PICKLE_PATH = DATA_PATH + 'pickle/'


def load_pickle(file_name):
    file_path = PICKLE_PATH + file_name
    with open(file_path, 'rb') as pfile:
        my_pickle = pickle.load(pfile)
    return my_pickle


def save_pickle(object_, file_name):
    file_path = PICKLE_PATH + file_name
    with open(file_path, 'wb') as pfile:
        # pickle.dump(object_, pfile, protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(object_, pfile, protocol=2)


def list_pickle():
    file_list = os.listdir(PICKLE_PATH)
    pickle_list = [i for i in file_list if '.p' in i]
    print(pickle_list)

    
def spacify_number(number):
    nb_rev = str(number)[::-1]
    new_chain = ''
    for val, letter in enumerate(nb_rev):
        if val%3==0:
            new_chain += ' '
        new_chain += letter
    final_chain = new_chain[::-1]
    return final_chain