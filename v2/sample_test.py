import pytest
import teradatasql

from v2.flask import create_app


@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def fake_data():
    application_database = 'console'
    fake_table_flag = False
    with teradatasql.connect(host='target_DBCcop1', user='dbc', password='dbc') as con:
        with con.cursor() as cur:
            try:
                cur.execute("show table %s.test_set;" % application_database)
            except teradatasql.OperationalError as ex:
                if ("Object '%s.test_set' does not exist." % application_database) in str(ex):
                    try:
                        cur.execute("create multiset table %s.test_set ("
                                    "test_set_id varchar(100), "
                                    "create_ts timestamp, "
                                    "test_set_purpose varchar(100), "
                                    "expiration_date date, "
                                    "reserved_ind varchar(1) "
                                    ");" % application_database)
                        fake_table_flag = True
                        cur.execute("insert into %s.test_set (?, ?, ?, ?, ?);" % application_database, [
                            ["abc1", "2017-07-11 15:04:00", "abc", "2018-07-11", "N"],
                            ["def2", "2016-07-11 15:04:00", "def", "2017-07-11", "Y"],
                            ["abc3", "2014-07-11 15:04:00", "abc", "2015-07-11", "N"],
                            ["def4", "2019-07-11 15:04:00", "def", "2020-07-11", "N"]
                        ])
                    except teradatasql.OperationalError as ex:
                        print(ex)
            finally:
                yield
                if fake_table_flag:
                    cur.execute("drop table console.test_set;")


def test_empty_form(client):
    response = client.get('/')
    assert response.headers['Content-type'] == 'text/html; charset=utf-8'
    assert response.get_data(True) == '''<!doctype html>
<html lang="en">

<head>
    <title>Teradata Test Set Listing</title>
</head>

<body>
    
    <h3>Teradata Test Set Listing</h3>

    
    <TABLE border=1 align=\"center\" width=\"90%\">
    
    
    </TABLE>

</body>

</html>'''


def test_error_data_form(client):
    response = client.post('/', data={'TARGET_TD_SYSTEM': 'fake_target_DBC'})
    assert response.headers['Content-type'] == 'text/html; charset=utf-8'
    assert response.get_data(True) == '''<!doctype html>
<html lang="en">

<head>
    <title>Teradata Test Set Listing</title>
</head>

<body>
    
    <h3>Teradata Test Set Listing</h3>

    
    <TABLE border=1 align=\"center\" width=\"90%\">
    
    
        <tr><td>Connection error! [Version 16.20.0.48] [Session 0] [Teradata SQL Driver] Hostname lookup failed for fake_target_DBCcop1</td></tr>
    
        <tr><td>dbc, fake_target_DBC, fake_target_DBCcop1</td></tr>
    
    
    
    </TABLE>

</body>

</html>'''


def test_valid_data_form(client, fake_data):
    response = client.post('/', data={'TARGET_TD_SYSTEM': 'target_DBC'})
    assert response.headers['Content-type'] == 'text/html; charset=utf-8'
    assert response.get_data(True) == '''<!doctype html>
<html lang="en">

<head>
    <title>Teradata Test Set Listing</title>
</head>

<body>
    
    <h3>Teradata Test Set Listing</h3>

    
    <TABLE border=1 align=\"center\" width=\"90%\">
    
    
        <tr>
            <th>Test Set ID</th>
            <th>Create Date</th>
            <th>Purpose</th>
            <th>Expiration<BR>Date</th>
        </tr>
        
        <tr>
            <td align='center'>ABC1</td>
            <td align='center'>2017-07-11          </td>
            <td>abc</td>
            <td align='center'>2018-07-11          </td>
        </tr>
        
        <tr>
            <td align='center'>ABC3</td>
            <td align='center'>2014-07-11          </td>
            <td>abc</td>
            <td align='center'>2015-07-11          </td>
        </tr>
        
        <tr>
            <td align='center'>DEF4</td>
            <td align='center'>2019-07-11          </td>
            <td>def</td>
            <td align='center'>2020-07-11          </td>
        </tr>
        
    
    </TABLE>

</body>

</html>'''
