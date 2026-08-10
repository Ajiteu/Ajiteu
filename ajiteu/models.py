from ajiteu import db
from sqlalchemy import Table

#중간테이블
post_liker = Table(
    'post_liker',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), primary_key=True)
)

comment_liker = Table(
    'comment_liker',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id', ondelete='CASCADE'), primary_key=True)
)

reply_liker = Table(
    'reply_liker',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('reply_id', db.Integer, db.ForeignKey('reply.id', ondelete='CASCADE'), primary_key=True)
)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    modify_date = db.Column(db.DateTime())
    #여러개 이미지
    image_path = db.Column(db.Text(), nullable=True)
    #User와 연결
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('post_set'))

    #sinae : 808 post가 지워지면 아래 comment들도 지워지게 설정
    comment_set = db.relationship('Comment', cascade='all, delete-orphan')

    #추천인(like)
    liker = db.relationship(
        'User',
        secondary=post_liker,
        backref=db.backref('post_liker_set', lazy='dynamic')
    )

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    #수정(처음 -  cascade='all, delete-orphan' 지우고 > ondelete='CASCADE' 넣었는데 오류나서 > 지움)
    
    # sinae : 808 Post(db.Model)에서 comment_set으로 post가 지워지면 comment도 지워지게.(위에서 relationship하면 여기서 backref 지워줘야한다고 함)
    # post = db.relationship('Post', backref=db.backref('comment_set'))
    post = db.relationship('Post')

    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    modify_date = db.Column(db.DateTime())
    #글쓴이 외래키 및 관계 설정
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('comment_set'))
    #추천인과 연결(like)
    liker = db.relationship('User', secondary=comment_liker, backref=db.backref('comment_liker_set', lazy='dynamic'))

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('reply_set'))
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    modify_date = db.Column(db.DateTime())
    #Post 테이블 및 Comment 테이블 다대일 관계 외래키매핑
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=True)
    post = db.relationship('Post', backref=db.backref('reply_set'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id', ondelete='CASCADE'), nullable=True)
    comment = db.relationship('Comment', backref=db.backref('reply_set'))
    #추천인과 연결(like)
    liker = db.relationship('User', secondary=reply_liker, backref=db.backref('reply_liker_set', lazy='dynamic'))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nickname = db.Column(db.String(120), nullable=False)
    user_intro = db.Column(db.Text(), nullable=True)
    image_path = db.Column(db.String(255), nullable=True)