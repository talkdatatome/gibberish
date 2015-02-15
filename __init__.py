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
from sqlalchemy.engine import reflection
from sqlalchemy.exc import OperationalError

Base = declarative_base()
class GibData(Base):
    __tablename__='gib'
    _id = Column('id', Integer, primary_key=True)
    text = Column('text', String(length=500))
    handFlag = Column('handFlag', Boolean)

    def __repr__(self):
        return("<gib_data(_id='%s', text='%s', handFlag='%s')>" % (self._id, self.text, self.handFlag))

engine = create_engine('sqlite:///gibberish.db')
insp = reflection.Inspector.from_engine(engine)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

session = Session()
try:
    if session.query(GibData).count() == 0:
        init_data = [("i am not gibberish", False), ("this is also a real answer", False), ("baglkd zzzzzzzz", True), ("asdfkadnsknn", True), ("", True)]
        for x in init_data:
            new_data = GibData(text=x[0], handFlag=x[1])
            session.add(new_data)
        session.commit()
        session.close()
except OperationalError:
    pass

from gibberish import views
