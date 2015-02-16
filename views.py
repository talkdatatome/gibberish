from flask import jsonify, url_for, redirect, request, render_template
import time
import random
from re import sub
from gibberish import app, celery, Session, GibData, prep_data, sanitize, this_model

@celery.task(bind=True)
def _eval_model(self, text):
    message = "calculating..."
#   self.update_state(state='PROGRESS',
#                    meta={'current':0, 'total': 1, 'status':message})
    safe_text = sanitize(text)
    #run against model here
    X, = prep_data([{"text":safe_text}])
    prediction = this_model.predict(X)
    return(prediction)#word_rating.rate(safe_text))

@celery.task(bind=True)
def _fit_model(self):
    #grab data from database
    total = 3
    message = "Starting to fit model. Querying data."
    self.update_state(state='PROGRESS',
                     meta={'current':0, 'total': total, 'status':message})
    session = Session()
    all_data = session.query(GibData).all()
    all_data_json = [{"text":d.text, "flag":d.handFlag} for d in all_data ] 

    #run model
    message = "Prepping data. Using " + str(len(all_data_json)) + " datapoints."
    self.update_state(state='PROGRESS',
                          meta={'current':1, 'total': total, 'status':message})
    X, y = prep_data(all_data_json)

    message = "Fitting model with " + str(len(y)) + " datapoints."
    self.update_state(state='PROGRESS',
                          meta={'current':2, 'total': total, 'status':message})
    this_model.fit(X, y)
#    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
#    adj = ['master', 'radiant', 'silent', 'harmonic', 'fast']
#    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'it']
#    message = ''
#    total = random.randint(5, 10)
#    for i in range(total):
#        if not message or random.random() < 0.25:
#            message = '{0} {1} {2}...'.format(random.choice(verb),
#                                              random.choice(adj),
#                                              random.choice(noun))
#        self.update_state(state='PROGRESS',
#                          meta={'current':i, 'total': total, 'status':message})
#        time.sleep(1)
    return({'current':100, 'total':100, 'status': 'Task completed!', 
            'result':"Model updated successfully!"})


@app.route('/', methods=['GET', 'POST'])
def index(show=None, text=None, result=None):
    if result is None:
        return(render_template('index.html', show=False, text="", result=""))
    else:
        return(render_template('index.html', show=show, text=text, result=result))

@app.route('/add', methods=['POST'])
def add():
    text = request.form['for_add_text']
    is_correct = request.form['is_correct']
    value_correct = request.form['for_add_value_correct']
    value_incorrect = request.form['for_add_value_incorrect']
    clean_text = sanitize(text)
    if is_correct == 'True':
        new_thing = GibData(text=clean_text, handFlag=int(value_correct))
    else:
        new_thing = GibData(text=clean_text, handFlag=int(value_incorrect))

    session = Session()
    session.add(new_thing)
    session.commit()
    session.close()

    return(redirect(url_for('index')))

@app.route('/eval', methods=['POST'])
def eval():
    text = request.form['unsafe_text_input']
    result = _eval_model(text)[0]
    return(render_template('index.html', show=True, text=text,result=result))
#   task = _eval_model.apply_async(args=[text])
#   return jsonify({}), 202, {'Location': url_for('evalstatus',
#                               task_id=task.id)}

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
        
if __name__=="__main__":
    app.run(debug=True)
