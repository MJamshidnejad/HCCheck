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

import xlrd

raw_file = 'list.xls'
filename = 'data.pickle'

def create_database(filename):
    db = collections.defaultdict(dict)
    try:
        xl = xlrd.open_workbook(raw_file)
    except:
        print(raw_file + " not found.")
        quit()

    sheet = xl.sheet_by_index(0)
    for i in range (1,sheet.nrows): 
        row = [x.value for x in sheet.row(i)]
        update_database(db, row)

    with open(filename, 'wb') as fout:
        pickle.dump(db, fout, pickle.HIGHEST_PROTOCOL)
    
    return db

def update_database(database, row: list):
    index = tuple(row[1].split('.')[0:2])
    ip = ip_network(row[1], strict=False)
    detail = (row[0], '-'.join(row[2].split('/'))) # Website, updating date
    database[index].setdefault(ip, set()).add(detail)
    # if index in database:
    #     database[index].setdefault(ip, []).append(detail)
    # else:
    #     database[index] = dict()
    #     database[index].setdefault(ip, []).append(detail)
    
def load_database(filename):
    with open('data.pickle','rb') as fin:
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
         
def main():
    if not os.path.exists('./'+filename):
        db = create_database(filename)
    else:
        db = load_database(filename)
    
    ip = ip_address('185.4.3.14')
    result = search_in_database(db, ip)
    print(result)
    
if __name__ == "__main__":
    main()


a = set()
