""" 
        Half Charge Check
    @author: Mohammad Jamshidnejad
    This program chech that if the site
    is in half charge list and national network.
    
"""


import os
import re
import sqlite3
from ipaddress import ip_address, ip_network
# from time import perf_counter

import urllib3
import win32com.client
import xlrd
from prettytable import PrettyTable
from tqdm import tqdm

raw_file = 'list.xls'
db_name = 'data.pickle'
sql_name = 'data.db'
url_file = 'https://g2b.ito.gov.ir/index.php/site/page/view/download'

help_str = """This program check if IP is in national network or not.
it uses ITOs list for doing that.
    commands:
    IP: example of a valid IP: 185.5.250.6
    
    -h or --help: give help
    -e or --exit: exit
    -q or --quit: quit (!)\n"""

def create_database(connection: sqlite3.Connection):
    # t = perf_counter()
    table_creating_str = ''' 
    CREATE TABLE IF NOT EXISTS networks (
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        net_addr TEXT NOT NULL,
        domain TEXT NOT NULL,
        port VARCHAR(5) DEFAULT NULL,
        sub TEXT DEFAULT NULL,
        date char(10) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS ips (
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        ip VARCHAR(15) NOT NULL,
        net_id INTEGER NOT NULL
    );'''
    
    try:
        xcl = win32com.client.Dispatch('Excel.Application')
        wb = xcl.workbooks.open(os.getcwd()+'\\'+'list.xls')
        xcl.DisplayAlerts = False
        wb.Save()
        xcl.Quit()
        
        xl = xlrd.open_workbook(raw_file)
        sheet = xl.sheet_by_index(0)
    except:
        print(raw_file + " not found.") # problem is here
        quit()
    
    cur = connection.cursor()
    try:
        cur.executescript(table_creating_str)
    except:
        print('Tables are not created.')
        quit()

    for i in range(1, sheet.nrows):
        row = sheet.row_values(i)
        update_database(cur, row)
        
    cur.executescript('''
    WITH dups AS(
        SELECT ROW_NUMBER() OVER (
                    PARTITION BY net_addr, domain
                    ORDER BY date DESC
        ) RowNum, * FROM networks
    )
    DELETE FROM networks
    WHERE id IN ( SELECT id FROM dups WHERE RowNum > 1);

    DELETE FROM ips
    WHERE net_id NOT IN ( SELECT id FROM networks );
    ''')
    cur.execute('VACUUM')
    connection.commit()
    cur.close()
    # print('Creating time = ', str(perf_counter() - t))


def url_spliter(URL: str):
    domain = port = sub = None
    pattern = r"(?:https?:\/\/)?(?:www.)?(?:(?:(?P<url_p>[\w_\-\.]+):(?P<port>\d{0,5}))|(?P<url>[\w_\-\.]+))(?P<sub>\/[^\n]+)?"
    search_obj = re.search(pattern, URL, re.IGNORECASE)
    url_p, port, url, sub = search_obj.groups()
    domain = url if url else url_p
    return domain.lower(), port, sub


def update_database(cursor: sqlite3.Cursor, row: list):
    net_addr = ip_network(row[1], strict=False)
    date = '-'.join(row[2].split('/'))  # Website, updating date
    domain, port, sub = url_spliter(row[0])
    cursor.execute('''INSERT INTO networks (net_addr, domain, port, sub, date)
                    VALUES (?,?,?,?,?)''', (str(net_addr), domain, port, sub, date))
    
    net_id = cursor.lastrowid
    ip_list = [(str(ip),net_id) for ip in list(net_addr)]
    cursor.executemany("INSERT INTO ips (ip, net_id) VALUES (?,?)", ip_list)
    

def search_for_ip(connection: sqlite3.Connection, ip: ip_address):
    sql_str = '''
    SELECT ips.ip, networks.domain, networks.port, networks.sub, networks.net_addr, networks.date
    FROM ips
    JOIN networks
        ON networks.id = ips.net_id
    WHERE ips.ip = ?'''
    cur = connection.execute(sql_str, (str(ip),)) 
    return cur.fetchall()


def search_for_url(connection: sqlite3.Connection, url:str):
    sql_str = '''
    SELECT domain, port, sub, net_addr, date
    FROM networks WHERE domain REGEXP ?
    '''
    expr = '.*'+url.replace('.',r'\.')
    cur = connection.execute(sql_str, (expr,))
    return cur.fetchall()


def beautiful_result(results, url: str = None):
    if not results:
        print("Nothing found.\n")
    
    table = PrettyTable()
    table.field_names = ['Domain', 'Port', 'Sub', 'Network Address', 'Date']
    if len(results[0]) == 6:
        for result in results:
            table.add_row(list(result[1:]))
        print('\nResults for IP:', results[0][0])
    else:
        for result in results:
            table.add_row(list(result))
        print('\nResults for URL:', url)
    table.sortby = 'Domain'
    print(table,'\n')


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


def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None


def main():
    print("Welcome to HCCheck")
    try:
        conn = sqlite3.connect(sql_name)
        conn.create_function("REGEXP",2, regexp)    # Add regular expresions feature to Sqlite
        print('Database connected.')
    except:
        print("Something is wrong with database.")
        quit()

    result = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    result = result.fetchall()
    result = [x[0] for x in result]
    if 'networks' not in result: 
        # Database is new
        if os.path.exists('./' + raw_file):
            print("Loading data to database...")
            create_database(conn)
            print("Loading finished.")
        else:
            print("You need to download list file.")
            download_file(url_file, raw_file)
            print("The list downloaded.")
            print("Loading data to database...")
            create_database(conn)
            print("Loading finished.")
    
    while True:
        command = input("Input IP, URL or a command:\n> ")
        command = command.strip().lower()
        # print(command)
        if command.startswith('-'):
            if command in ('-h', '--help') :
                print(help_str)
            elif command in ('-q', '-e', '--quit', '--exit'):
                print('Thank you. Goog Luck!\n')
                conn.close()
                quit()
            else:
                print("Your command is not valid.\n"
                        +"Get help with -h or --help\n")
                
        elif is_ip_valid(command):
            ip = ip_address(command)
            results = search_for_ip(conn, ip)
            beautiful_result(results)
        
        elif len(command) >= 5:
            results = search_for_url(conn, command)
            beautiful_result(results, url=command)
            
        else:
            print("Your command is not valid.\n"
                    +"your URL length must be grater than 4.\n"
                    +"Get help with -h or --help\n")



if __name__ == "__main__":
    main()
	
