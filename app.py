# This TODO app is Build with Flask 
# import Flask class from flask
import sys
from flask import Flask, request, render_template, redirect, url_for, jsonify, abort
# import SQLAlchemy class from flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy
# import Migrate class from flask_migrate
from flask_migrate import Migrate

# give the application name as the file name
app = Flask(__name__)

# add configuration for database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/example'

# link the database to this Flask Application
db = SQLAlchemy(app)

# instantiate migrate so we can use migration to begin initializing, upgrade, and downgrade db in the future,
# linking the migrate to the application and the db
migrate = Migrate(app, db)

# create table Todo
class Todo(db.Model):
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__ (self):
        return f'<You should: {self.description}'

@app.route('/')
def index():
    return render_template('index.html', data=Todo.query.order_by('id').all())

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
  try:
    completed = request.get_json()['completed']
    print('completed', completed)
    todo = Todo.query.get(todo_id)
    todo.completed = completed
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body={}
    try:
        description = request.get_json()['description']
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        
    if error:
        abort(400)
    else:
        return jsonify(body)

if __name__ == '__main__':
    app.debug=True
    app.run(host="0.0.0.0")