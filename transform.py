import MySQLdb
#====================================================
# license
#====================================================
MIT = """
-- The MIT License (MIT)
--
-- Copyright (c) 2015 www.codingninja.co.uk
--
-- Permission is hereby granted, free of charge, to any person obtaining a copy
-- of this software and associated documentation files (the "Software"), to deal
-- in the Software without restriction, including without limitation the rights
-- to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
-- copies of the Software, and to permit persons to whom the Software is
-- furnished to do so, subject to the following conditions:
--
-- The above copyright notice and this permission notice shall be included in
-- all copies or substantial portions of the Software.
--
-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-- IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-- FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-- AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-- LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
-- OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
-- THE SOFTWARE.""".replace("[YEAR]","2014").replace("[COPYRIGHT_HOLDER]","www.codingninja.co.uk")
#====================================================
# configuration
#====================================================
DB_HOST = "your_host"
DB_USER = "your_user"
DB_PASS = "your_password"
DB_NAME = "your_db_name"
#====================================================
# define a row class
#====================================================
class rx(object):
	def __init__(self, table, col, isKey):
		self.table 	= table
		self.col 	= col
		self.isKey 	= isKey
#====================================================
# schema meta
#====================================================
def get_meta_data():
	db = MySQLdb.connect(host  	= DB_HOST
						,user 	= DB_USER
						,passwd	= DB_PASS
						,db 	= DB_NAME)
	cur = db.cursor()
	cur.execute("select table_name, column_name, column_key from information_schema.columns where table_schema = '"+DB_NAME+"' and data_type = 'varchar' and character_maximum_length= 64")
	meta = []
	for row in cur.fetchall():
		meta.append(rx(row[0],row[1], row[2]))
	return meta
#====================================================
# sql script generation
#====================================================
data  = get_meta_data()

dsql  = "\n"
dsql += "-- ;===============================================\n"
dsql += "-- ; auto transform mssql guid to mysql bin(16)	\n"
dsql += "-- ;===============================================\n"
dsql += MIT

dsql += "\nUSE "+DB_NAME+";\n"

dsql += "\n"
dsql += "-- ;===============================================\n"
dsql += "-- ; mirror old columns							\n"
dsql += "-- ;===============================================\n"

for item in data:
	if item.isKey == "PRI":
		dsql += "ALTER TABLE `[TABLE]` ADD COLUMN `[COL]_x` BINARY(16) FIRST;\n".replace("[TABLE]", item.table).replace("[COL]", item.col)
	else:
		dsql += "ALTER TABLE `[TABLE]` ADD COLUMN `[COL]_x` BINARY(16) AFTER `[COL]`;\n".replace("[TABLE]", item.table).replace("[COL]", item.col)	


dsql += "\n"
dsql += "-- ;===============================================\n"
dsql += "-- ; transfer data across							\n"
dsql += "-- ;===============================================\n"

idx  = 0;
current_table = ""
move_col = "`[COL]_x` = UNHEX(REPLACE(`[COL]`,'-',''))"

for item in data:
	idx+=1
	if current_table == item.table:
		dsql+= ","+move_col.replace("[COL]", item.col)
	else:
		current_table = item.table
		dsql+= (";" if idx > 1 else "")+"\nUPDATE `[TABLE]` SET ".replace("[TABLE]", item.table)+move_col.replace("[COL]", item.col)

dsql +=";"

dsql += "\n"
dsql += "-- ;===============================================\n"
dsql += "-- ; kill old columns								\n"
dsql += "-- ;===============================================\n"

for item in data:
	dsql += "ALTER TABLE `[TABLE]` DROP `[COL]`;\n".replace("[TABLE]", item.table).replace("[COL]", item.col)

dsql += "\n"
dsql += "-- ;===============================================\n"
dsql += "-- ; reset to orginal column name					\n"
dsql += "-- ;===============================================\n"

for item in data:
	dsql += "ALTER TABLE `[TABLE]` CHANGE `[COL]_x` `[COL]` BINARY(16);\n".replace("[TABLE]", item.table).replace("[COL]", item.col)

dsql += "\n"
dsql += "-- ;===============================================\n"
dsql += "-- ; reset new primary keys						\n"
dsql += "-- ;===============================================\n"

for item in data:
	if item.isKey == "PRI":
		dsql += "ALTER TABLE `[TABLE]` ADD PRIMARY KEY(`[COL]`);\n".replace("[TABLE]", item.table).replace("[COL]", item.col)

print dsql
