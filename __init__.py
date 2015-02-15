from flask import Flask
from gibberish import config
from celery import Celery

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'amqp://'
app.config['CELERY_RESULT_BACKEND'] = 'amqp://'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
celery.conf.update(app.config)


from sqlalchemy import Column, Integer, String, Boolean, create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
engine = create_engine('sqlite:///gibberish.db')
Base = declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

#session = Session()
class GibData(Base):
    __tablename__='gib'
    _id = Column('id', Integer, primary_key=True)
    text = Column('text', String(length=500))
    handFlag = Column('handFlag', Boolean)

    def __init__(self):
        """Intialize db with simple list of gibberish and nongibberish."""
        pass

    def __repr__(self):
        return("<gib_data(_id='%s', text='%s', handFlag='%s')>" % (self._id, self.text, self.handFlag))


from gibberish import views
