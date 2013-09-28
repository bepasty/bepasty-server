from . import blueprint

@blueprint.route('/')
def index():
    from flask import render_template
    return render_template('index.html')
