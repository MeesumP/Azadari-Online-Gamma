from Website import create_app
from flask import render_template

app = create_app()

@app.errorhandler(404)
def page_not_found(e):
    return render_template('does-not-exist.html'), 404

if __name__ == '__main__':
    app.run(debug=True)