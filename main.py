""" 
        Half Charge Check
    @author: Mohammad Jamshidnejad
    This program chech that if the site
    is in half charge list and national network.
    
"""

import collections
import os
import pickle
from ipaddress import ip_address, ip_network

import urllib3
import win32com.client
import xlrd
from tqdm import tqdm
import re

raw_file = 'list.xls'
db_name = 'data.pickle'
url_file = 'https://g2b.ito.gov.ir/index.php/site/page/view/download'

help_str = """This program check if IP is in national network or not.
it uses ITOs list for doing that.
    commands:
    IP: example of a valid IP: 185.5.250.6
    
    -h or --help: give help
    -e or --exit: exit
    -q or --quit: quit (!)\n"""

def create_database(filename):
    db = collections.defaultdict(dict)
    try:
        xcl = win32com.client.Dispatch('Excel.Application')
        wb = xcl.workbooks.open(os.getcwd()+'\\'+'list.xls')
        xcl.DisplayAlerts = False
        wb.Save()
        xcl.Quit()
        
        xl = xlrd.open_workbook(raw_file)
    except:
        print(raw_file + " not found.") # problem is here
        quit()

    sheet = xl.sheet_by_index(0)
    for i in range(1, sheet.nrows):
        row = sheet.row_values(i)
        update_database(db, row)

    with open(filename, 'wb') as fout:
        pickle.dump(db, fout, pickle.HIGHEST_PROTOCOL)

    return db


def update_database(database, row: list):
    index = tuple(row[1].split('.')[0:2])
    ip = ip_network(row[1], strict=False)
    detail = (row[0], '-'.join(row[2].split('/')))  # Website, updating date
    database[index].setdefault(ip, set()).add(detail)
    # if index in database:
    #     database[index].setdefault(ip, []).append(detail)
    # else:
    #     database[index] = dict()
    #     database[index].setdefault(ip, []).append(detail)


def load_database(filename):
    with open('data.pickle', 'rb') as fin:
        db = pickle.load(fin)
    return db


def search_in_database(database, ip: ip_address):
    result = []
    index = tuple(str(ip).split('.')[0:2])
    if index in database:
        for network in database[index]:
            if ip in network:
                result.append((network, database[index][network]))

    return result


def beautiful_result(results):
    if not results:
        print("IP not found.\n")
        return None
    for result in results:
        string = "'%s' network detail:\n" % (str(result[0]))
        string += "               site             |      date \n"
        string += "------------------------------------------\n"
        for detail in result[1]:
            string += "%30s| %10s\n" % (detail[0], detail[1])
        print(string)
    print('')


def download_file(url, filename):
    http = urllib3.PoolManager(num_pools=50)
    r = http.request('get', url, preload_content=False)
    if r.status == 200:
        with open(filename, "wb") as handle:
            for data in tqdm(r.stream(1), unit=' B', desc='Downloading: ', ncols=70):
                handle.write(data)
        r.release_conn()
    else:
        print("Download failed.\n")
        

def is_ip_valid(ip: str):
    byte_pattern = "(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)"
    pattern = r"^%s\.%s\.%s\.%s" % ((byte_pattern,)*4)
    if re.search(pattern, ip):
        return True
    return False


def main():
    print("Welcome to HCCheck")
    if os.path.exists('./' + db_name):
        if True: print("Loading database...")
        db = load_database(db_name)
        print("Database loaded.")
        
    elif os.path.exists('./' + raw_file):
        print("Creating database...")
        db = create_database(db_name)
        print("Database created.")
    else:
        print("You need to download list file.")
        download_file(url_file, raw_file)
        print("The list downloaded.")
        print("Creating database...")
        db = create_database(db_name)
        print("Database created.")
    
    while True:
        command = input("Input your IP or your command:\n> ")
        command = command.strip().lower()
        print(command)
        if command in ('-h', '--help') :
            print(help_str)
        
        elif command in ('-q', '-e', '--quit', '--exit'):
            print('Thank you. Have good!\n')
            quit()
        
        elif is_ip_valid(command):
            ip = ip_address(command)
            results = search_in_database(db, ip)
            beautiful_result(results)
        
        else:
            print("Your command is not valid.\n"
                    +"Get help with -h or --help\n")


if __name__ == "__main__":
    main()
