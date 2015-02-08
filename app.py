from flask import Flask, jsonify, url_for, redirect, request, render_template
from celery import Celery
from gibberish.model import _fit_model
import time
import random

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'amqp://'
app.config['CELERY_RESULT_BACKEND'] = 'amqp://'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
celery.conf.update(app.config)

@celery.task(bind=True)
def _fit_model(self):
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adj = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'it']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adj),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current':i, 'total': total, 'status':message})
        time.sleep(1)
        print(i)
    return({'current':100, 'total':100, 'status': 'Task completed!', 
            'result':42})


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return(render_template('index.html'))

    return(redirect(url_for('index'))) 

@app.route('/fit_model', methods=['POST'])
def fit_model():
    task = _fit_model.apply_async()
    return jsonify({}), 202, {'Location': url_for('taskstatus', 
                                                task_id=task.id)}
@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = _fit_model.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
       response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
       }
       if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),
        }
    return(jsonify(response))
        
if __name__=="__main__":
    app.run(debug=True)
