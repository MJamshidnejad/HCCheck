""" 
        Half Charge Check
    @author: Mohammad Jamshidnejad
    This program chech that if the site
    is in half charge list and national network.
    
"""

import codecs
import sys
import collections 

import xlrd

db = collections.defaultdict(dict)
masks = collections.Counter()

test = dict()


def update_database(row: list):
    index = tuple(row[1].split('.')[0:2])
    ip = row[1]
    detail = (row[0], '-'.join(row[2].split('/'))) # Website, updating date
    db[index].setdefault(ip, []).append(detail)
    
def check_masks():
    xl = xlrd.open_workbook("list.xls")
    sheet = xl.sheet_by_index(0) 
    for i in range(1,20):
       cell = sheet.cell_value(i,1)
       mask = cell.split('/')[1]
       masks.update((mask,))
    print(mask)
    result = masks.most_common()
    print(result)

       
xl = xlrd.open_workbook("list.xls")
sheet = xl.sheet_by_index(0)
for i in range (1,sheet.nrows):
    row = sheet.row(i)
    row = [x.value for x in row]
    update_database(row)

print(len(db['185','4']))


    
