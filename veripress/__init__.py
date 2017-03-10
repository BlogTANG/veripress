import json
import os

from flask import Flask, send_from_directory
from werkzeug.exceptions import NotFound


class CustomFlask(Flask):
    """
    Customize the original Flask class to fit the needs of this VeriPress project.
    """

    def send_static_file(self, filename):
        """
        Send static files from the static folder in the current selected theme prior to the global static folder.

        :param filename: static filename
        :return: response object
        """
        theme_static_folder = getattr(self, 'theme_static_folder', None)
        if theme_static_folder:
            try:
                return send_from_directory(theme_static_folder, filename)
            except NotFound:
                pass
        return super(CustomFlask, self).send_static_file(filename)


def create_app(config_filename, instance_path=None):
    """
    Factory function to create Flask application object.

    :param config_filename: absolute or relative (rel to the instance path) filename of the config file
    :param instance_path: the instance path to initialize or run a VeriPress app
    :return: a Flask app object
    """
    app_ = CustomFlask(__name__,
                       instance_path=instance_path or os.environ.get('VERIPRESS_INSTANCE_PATH') or os.getcwd(),
                       instance_relative_config=True)
    app_.config.from_pyfile(config_filename)

    theme_folder = os.path.join(app_.instance_path, 'themes', app_.config['THEME'])
    app_.template_folder = os.path.join(theme_folder, 'templates')  # use templates in the selected theme's folder
    app_.theme_static_folder = os.path.join(theme_folder, 'static')  # use static files in the selected theme's folder

    return app_


app = create_app('config.py')

with app.open_instance_resource('site.json', mode='r') as f:
    # load site meta info to the site object
    site = json.load(f)


@app.context_processor
def inject_site():
    """
    Inject the site object into the context of templates.
    """
    return dict(site=site)


from flask_caching import Cache
cache = Cache(app, config=app.config)  # create the cache object with the app's config

import veripress.model