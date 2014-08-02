from datetime import datetime

from .. import db



class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), unique=True)
    body = db.Column(db.Text())

    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow,
                                          onupdate=datetime.utcnow)

    def __init__(self, title="", body=""):
        self.title = title
        self.body = body

    def __repr__(self):
        return '<Blogpost - {}>'.format(self.title)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
    blog = db.relationship('Blog', backref=db.backref('comments',
                                                      lazy='dynamic'))

    username = db.Column(db.String(50))
    comment = db.Column(db.Text())
    visible = db.Column(db.Boolean(), default=False)

    created_on = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, post='', username='', comment=''):
        if post:
            self.blog = post
        self.username = username
        self.comment = comment

    def __repr__(self):
        return '<Comment: blog {}, {}>'.format(self.blog_id, self.comment[:20])
