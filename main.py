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

raw_file = 'list.xls'
db_name = 'data.pickle'
url_file = 'https://g2b.ito.gov.ir/index.php/site/page/view/download'


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
        print("IP not found.")
        return None
    for result in results:
        string = "'%s' network detail:\n" % (str(result[0]))
        string += "                  site         |      date \n"
        string += "------------------------------------------\n"
        for detail in result[1]:
            string += "%30s| %10s\n" % (detail[0], detail[1])
        print(string)
        
def download_file(url, filename):
    http = urllib3.PoolManager(num_pools=50)
    r = http.request('get', url, preload_content=False)
    if r.status == 200:
        with open(filename, "wb") as handle:
            for data in tqdm(r.stream(1), unit=' B', desc='Downloading: ', ncols=70):
                handle.write(data)
        r.release_conn()
    else:
        print("Download failed.")


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
    
    
    ip = ip_address('185.88.153.218')
    results = search_in_database(db, ip)
    beautiful_result(results)


if __name__ == "__main__":
    main()
