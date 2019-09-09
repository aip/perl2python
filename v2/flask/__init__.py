#!/usr/bin/env python

import os

from flask import Flask

app_dir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.abspath(os.path.join(app_dir, '..'))


def create_app():
    app = Flask(__name__, instance_path=instance_path, instance_relative_config=True)
    app.config.from_pyfile("flask/config.py", silent=False)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from v2.flask import sample
    app.register_blueprint(sample.bp)
    app.add_url_rule("/", endpoint="index")

    return app
