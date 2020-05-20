# HCCheck
**Half Charge Check, A simple personal project to practice Python**

In Iran, for some sites that serviced by national servers and register themselves in government list is calculated half internet charge.
I decided to write a program with python to find those by name or by IP addresses.
The list of these sites are in the following URL:
    * https://g2b.ito.gov.ir/index.php/site/list_ip

### **Usage:**

You can use search any words more than 5 letters. The search system is working with RegEx engine.
you also can search a valid IP in the following format: X.X.X.X

you can use -h or --help for getting help or -q, --quit, -e, --exit for quit.

### Notes:
> **Note:** Because xlrd module problem with xls files, i forced using pywin32 to open, save and close the exel file. I fix it later with web scraping.

> **Note:** for update the database, you should delete `list.xls` and `data.db`. I'll provide a solution tho this problem soon :).

