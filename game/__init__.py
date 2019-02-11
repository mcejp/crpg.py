from flask import Flask, redirect, url_for
from pathlib import Path

from game import game, data

package_base_path = Path(__file__).parent

def create_app():
    app = Flask(__name__)

    @app.context_processor
    def inject_app_info():
        return dict(bgpalette=data.bgpalette, fgpalette=data.fgpalette)

    # @app.context_processor
    # def keep_reloading_data_every_request():
    #     data.reload_data()
    #     return {}

    @app.route("/")
    def hello():
        return redirect(url_for('game.index'))

    app.register_blueprint(game.bp)

    return app
