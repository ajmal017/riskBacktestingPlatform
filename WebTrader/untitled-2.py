from app.models import Post,User

from app import app, db,lm , celery 

#print User.login_check('test','test')

posts = db.session.query(Post).filter(Post.title =='s9').one()

print posts.content    


