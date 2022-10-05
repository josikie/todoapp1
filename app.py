# This TODO app is Build with Flask 
# import Flask class from flask
import inspect
import sys
from flask import Flask, request, render_template, redirect, url_for, jsonify, abort
# import SQLAlchemy class from flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy
# import Migrate class from flask_migrate
from flask_migrate import Migrate

# give the application name as the file name
app = Flask(__name__)

# add configuration for database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/examples'

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
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)
    def __repr__ (self):
        return f'<You should: {self.description}, parent: {self.list_id}\n'

#create table todo list
class TodoList(db.Model):
  __tablename__ = 'todolists'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)
  todos = db.relationship('Todo', backref='list', lazy=True, cascade="all, delete-orphan")
  completed = db.Column(db.Boolean, nullable=True, default=False)
  def __repr__ (self):
        return f'<List\'s name: {self.name}, Id: {self.id}\n'

# particular TodoList's route
@app.route('/lists/<list_id>')
def get_list_todos(list_id):
  return render_template('index.html', 
  lists=TodoList.query.order_by('id').all(),
  active_list = TodoList.query.get(list_id),
  todos=Todo.query.filter_by(list_id=list_id).order_by('id')
  .all())

# route to index/home
@app.route('/')
def index():
  return redirect(url_for('get_list_todos', list_id=1))

# route to create lists
@app.route('/list/create', methods=['POST'])
def create_list():
  list_id = 0
  error = False
  try:
    name = request.get_json()['name']
    list = TodoList(name=name)
    db.session.add(list)
    db.session.commit()
    list_id = list.id
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  
  if(error):
    return abort(400)
  else:
    return redirect(url_for('get_list_todos', list_id = list_id)) 

# route to update completed on particular list's
@app.route('/lists/<list_id>/set-completed', methods=['POST'])
def set_completed_list(list_id):
  error = False
  try:
    completed = request.get_json()['completed']
    list = TodoList.query.get(list_id)
    list.completed = completed
    todos = list.todos
    for todo in todos:
      todo.completed = completed
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  
  if error:
    return abort(400)
  else:
    return redirect(url_for('get_list_todos', list_id = list_id)) 

# route to delete list and its items
@app.route('/lists/<list_id>', methods=['DELETE'])
def delete_list(list_id):
  nextId = 0
  error = False
  try:
    list = TodoList.query.get(list_id)
    db.session.delete(list)
    db.session.commit()
    nextId = TodoList.query.first()['id']
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  
  if error:
    return abort(400)
  else:  
    return redirect(url_for('index'))

# route to delete particular todo's
@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
  try:
    todo = Todo.query.get(todo_id)
    db.session.delete(todo)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })

# route to update completed of particular todo
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

# route to create todo
@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    try:
        description = request.get_json()['description']
        list_id = request.get_json()['list_id']
        todo = Todo(description=description, list_id = list_id)
        db.session.add(todo)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(400)
    else:
        return redirect(url_for('get_list_todos', list_id = list_id)) 

if __name__ == '__main__':
    app.debug=True
    app.run(host="0.0.0.0")