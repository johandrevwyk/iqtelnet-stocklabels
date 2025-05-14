1. Install Python 3 (add to PATH when installing)
2. Change the directory in copystock.bat to where the Stock database is located
3. Run the copystock.bat and it will copy over all the Stock files needed.
4. Open dbsys, then open the database, export the database to stock.txt in the root directory.
5. Change the telnet port in run.bat if needed
6. Open run.bat as Administrator
7. When you are done scanning, open the .sql file that will be generated in the same directory.
8. Open IQ and go to Utilities > Tools > Database Utilities, paste the file's contents here and click Run SQL
9. Print labels as normal