from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)


@app.route('/')
def base():
    return redirect(url_for('mario'))

@app.route('/hello/<name>')
def hello_name(name):
   return 'Hello %s!' % name

@app.route('/mario')
def mario():
    return render_template('mario.html')

if __name__ == '__main__':
    app.run(debug=True)
