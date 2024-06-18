from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(100), nullable=True)
    date_posted = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now())
    date_created = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now())
    is_removed = db.Column(db.Boolean, nullable=False, default=False)
    date_removed = db.Column(db.DateTime(timezone=True), nullable=True)

    def to_dict(self, need_all=False):
        data = {
            'id': self.id,
            'company': self.company,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'link': self.link,
            'date_posted': self.date_posted.isoformat(),
        }
        if need_all:
            data.update({
                'date_created': self.date_created.isoformat(),
                'date_removed': self.date_removed.isoformat() if self.date_removed else None,
                'is_removed': self.is_removed,
            })
        return data


class Tracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), nullable=False, unique=True)
    secret = db.Column(db.String(100), nullable=False, unique=True)
    keyword = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    new_ids = db.Column(db.String(100), nullable=True)
    date_created = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now())
    is_expired = db.Column(db.Boolean, nullable=False, default=False)
    is_removed = db.Column(db.Boolean, nullable=False, default=False)
    date_removed = db.Column(db.DateTime(timezone=True), nullable=True)

    def to_dict(self, need_all=False):
        data = {
            'secret': self.secret,
            'keyword': self.keyword,
            'email': self.email,
            'duration': self.duration,
            'new_ids': self.new_ids,
            'is_expired': self.is_expired,
            'is_removed': self.is_removed,
            'date_created': self.date_created.isoformat(),
        }
        if need_all:
            data.update({
                'id': self.id,
                'token': self.token,
                'date_removed': self.date_removed.isoformat() if self.date_removed else None,
            })
        return data


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now())

    def to_dict(self, need_all=False):
        data = {
            'id': self.id,
            'email': self.email,
            'content': self.content,
            'date_created': self.date_created.isoformat()
        }
        if need_all:
            data.update({
                'token': self.token,
            })
        return data
    
