#!/usr/bin/env python

import os
import cgi
import html
import cgitb

import teradatasql
from configobj import ConfigObj


def insert_html_include(path, *args):
    with open(path, "r") as f:
        print(f.read() % args)


def parse_config_file(path):
    return ConfigObj(path)


def parse_input_form():
    return cgi.FieldStorage()


def retrieve_password(a, b, c, d, e):
    if a == 'password_os_userid' and b == 'password_application' \
            and c == 'dbc' and d == 'target_DBC' and e == 'passfile':
        return "dbc"
    else:
        return ""


def dba_connect_error(ex, admin_userid, target_DBC, target_hostname):
    print('<tr><td>Connection error! %s</td></tr>' % ex[:ex.index("\n")])
    print('<tr><td>%s, %s, %s</td></tr>' % (admin_userid, target_DBC, target_hostname))


def sql_error(ex, admin_userid, target_DBC, target_hostname, sql):
    print('<tr><td>SQL error! %s</td></tr>' % ex[:ex.index("\n")])
    print('<tr><td>%s, %s, %s</td></tr>' % (admin_userid, target_DBC, target_hostname))
    print('<tr><td>%s</td></tr>' % (sql))


def write_output(rows):
    ################################################################################
    #  Write the SQL results to the screen.
    #  This routine is expected to be different for each screen.  Examples:
    #    - field names
    #    - field count
    #    - centering attributes
    ################################################################################

    # Create table header
    print("      <tr>")
    print("        <th>Test Set ID</th>")
    print("        <th>Create Date</th>")
    print("        <th>Purpose</th>")
    print("        <th>Expiration<BR>Date</th>")
    print("      </tr>")

    # Create table detail lines.
    for row in rows:
        print("      <tr>")
        print("        <td align=\'center\'>%s</td>" % row[0])
        print("        <td align=\'center\'>%s</td>" % row[1])
        print("        <td>%s</td>" % row[2])
        print("        <td align=\'center\'>%s</td>" % row[3])
        print("      </tr>")


cgitb.enable()

script_dir = os.path.abspath(os.path.dirname(__file__))
os.chdir(script_dir)


# Setup the resulting web page.
print("Content-type: text/html")
print()

insert_html_include("../include/results_header.inc", "Teradata Test Set Listing", "Teradata Test Set Listing")

# Extract parameters passed by configuration file.
config_parameters = parse_config_file("../include/config.ini")

# Assign configuration parameters to local variables.
admin_userid = config_parameters["admin_userid"]
application_database = config_parameters["application_database"]

# Extract parameters passed by form.
form_parameters = parse_input_form()

# Assign form parameters to local variables.
target_DBC = html.escape(form_parameters.getfirst("TARGET_TD_SYSTEM", ""))

# 2011-02-01 - This section added
password_os_userid = config_parameters["password_os_userid"]
password_application = config_parameters["password_application"]
passfile = config_parameters["passfile"]
admin_password = retrieve_password(password_os_userid, password_application, admin_userid, target_DBC, passfile)

# Construct host name - used to connect to Teradata.
target_hostname = target_DBC + "cop1"

print('<TABLE border=1 align=\"center\" width=\"90%\">')

try:
    with teradatasql.connect(host=target_hostname, user=admin_userid, password=admin_password) as connection:
        with connection.cursor() as cur:
            sql = "LOCK ROW FOR ACCESS " \
                  "SELECT " \
                  "UPPER(T.TEST_SET_ID), " \
                  "CAST( T.CREATE_TS AS DATE) (FORMAT \'YYYY-MM-DD\') (CHAR(10)), " \
                  "T.TEST_SET_PURPOSE, " \
                  "EXPIRATION_DATE (FORMAT \'YYYY-MM-DD\') (CHAR(10)) " \
                  "FROM %s.TEST_SET T " \
                  "WHERE T.RESERVED_IND = \'N\' " \
                  "ORDER BY T.TEST_SET_ID;" % application_database
            try:
                cur.execute(sql)
                write_output(cur.fetchall())
            except teradatasql.OperationalError as ex:
                sql_error(str(ex), admin_userid, target_DBC, target_hostname, sql)
except teradatasql.OperationalError as ex:
    dba_connect_error(str(ex), admin_userid, target_DBC, target_hostname)

# Close out the web page.
print('</TABLE>')
insert_html_include("../include/results_footer.inc")
