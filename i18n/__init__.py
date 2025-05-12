from flask_babel import Babel
from flask import session

babel = Babel()

def register_extensions(app):
    app.config['BABEL_DEFAULT_LOCALE'] = 'ar'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'i18n'
    babel.init_app(app)

    # Define the locale selector function (new way)
    def get_locale():
        return session.get('lang', 'ar')

    babel.locale_selector_func = get_locale
