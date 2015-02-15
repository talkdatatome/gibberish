from flask import jsonify, url_for, redirect, request, render_template
import time
import random
from re import sub
from gibberish import app, celery, Session, GibData
from gibberish.config import word_rating

def sanitize(text):
    #BAD
    if(text.islower() and text.isalpha()):
        clean_text = text.strip()
    else:
        text = text.lower()
        text = sub('[^a-z ]', '', text)
        clean_text = text.strip()
        
    return(clean_text)

@celery.task(bind=True)
def _eval_model(self, text):
    safe_text = sanitize(text)
    #run against model here
    return(word_rating.rate(safe_text))

@celery.task(bind=True)
def _fit_model(self):
    #grab data from database
    session = Session()
    all_data = session.query(GibData).all()
    all_data_json = [{"text":d.text, "flag":d.handFlag} for d in all_data ] 

    #run model
    X = prep_data(all_data_json)
    y = [item['flag'] for item in all_data_json]
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adj = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'it']
    message = ''
    total = random.randint(5, 10)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adj),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current':i, 'total': total, 'status':message})
        time.sleep(1)
    return({'current':100, 'total':100, 'status': 'Task completed!', 
            'result':all_data[0].text})


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return(render_template('index.html'))

    return(redirect(url_for('index'))) 

@app.route('/eval', methods=['POST'])
def eval():
    if request.method == 'POST':
        text = request.form['unsafe_text_input']
        task = _eval_model.apply_async(args=[text])
        return jsonify({}), 202, {'Location': url_for('evalstatus',
                                task_id=task.id)}
    return(redirect(url_for('index')))

@app.route('/status/<task_id>')
def evalstatus(task_id):
    task = _eval_model.AsyncResult(task_id)
    if task.state != 'FAILURE':
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
        
def prep_data(input_data):
    """Expects a list of dicts, text and handFlag"""
    return(input_data)

if __name__=="__main__":
    app.run(debug=True)