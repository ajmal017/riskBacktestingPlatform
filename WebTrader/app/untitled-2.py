from app.models import Post,User

from app import app, db,lm , celery 

Post.query.filter_by(user_id='1').order_by(db.desc(Post.time))