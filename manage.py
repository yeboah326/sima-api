from flask.cli import FlaskGroup

from api import app, db

cli = FlaskGroup(app)

def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

if __name__=="__main__":
    recreate_db()
    cli()