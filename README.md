# Microsoft SQL Server GUID Transformer

The context of this is explanined over at https://www.codingninja.co.uk/the-joys-of-migrating-from-sql-server-to-mariadb/

## Usage

First clone down the repo:

```shell
$ git clone https://github.com/coding-ninja/mssql-guid-transform
$ cd mssql-guid-transform/
```

Next just modify the script to add in your MySql connection details as can be found from line  30:

```python
#====================================================
# configuration
#====================================================
DB_HOST = "your_host"
DB_USER = "your_user"
DB_PASS = "your_password"
DB_NAME = "your_db_name"
```

Now simply run the python script _(this is Python 2.7 IIRC)_:

```shell
$ python transform.py
```

