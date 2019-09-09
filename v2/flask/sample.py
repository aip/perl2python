#!/usr/bin/env python

import teradatasql
from flask import Blueprint, escape, request, render_template, current_app

bp = Blueprint("sample", __name__)


def retrieve_password(a, b, c, d, e):
    if a == 'password_os_userid' and b == 'password_application' \
            and c == 'dbc' and d == 'target_DBC' and e == 'passfile':
        return "dbc"
    else:
        return ""


@bp.route('/', methods=("GET", "POST"))
def index():
    target_dbc = None
    if request.method == "GET" and "TARGET_TD_SYSTEM" in request.args:
        target_dbc = escape(request.args.get("TARGET_TD_SYSTEM"))
    if request.method == "POST" and "TARGET_TD_SYSTEM" in request.form:
        target_dbc = escape(request.form.get("TARGET_TD_SYSTEM"))
    if target_dbc:
        admin_userid = current_app.config["ADMIN_USERID"]
        application_database = current_app.config["APPLICATION_DATABASE"]
        password_os_userid = current_app.config["PASSWORD_OS_USERID"]
        password_application = current_app.config["PASSWORD_APPLICATION"]
        passfile = current_app.config["PASSFILE"]
        admin_password = retrieve_password(password_os_userid, password_application, admin_userid, target_dbc, passfile)
        target_hostname = target_dbc + "cop1"
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
                        return render_template("sample.html", rows=cur.fetchall())
                    except teradatasql.OperationalError as ex:
                        error_message = str(ex)
                        return render_template(
                            "sample.html",
                            error_messages=[
                                'SQL error! %s' % error_message[:error_message.index("\n")],
                                '%s, %s, %s' % (admin_userid, target_dbc, target_hostname),
                                sql
                            ]
                        )
        except teradatasql.OperationalError as ex:
            error_message = str(ex)
            return render_template(
                "sample.html",
                error_messages=[
                    'Connection error! %s' % error_message[:error_message.index("\n")],
                    '%s, %s, %s' % (admin_userid, target_dbc, target_hostname)
                ]
            )
    else:
        return render_template("sample.html")
