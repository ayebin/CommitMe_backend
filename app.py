from flask import Flask
from models import db
from config import Config
from routes import initialize_routes
from flask_cors import CORS
from routes.user_routes import user_bp # 유저 번호 자동 생성
from routes.info_routes import info_bp
from routes.session_routes import session_bp # 세션
from routes.chatbot_routes import chat_bp # 메시지
import os

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/*": {"origins": "*"}})  

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # 현재 디렉토리 기준으로 'uploads' 폴더 생성
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 폴더가 없으면 자동 생성
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db.init_app(app)

# DB 초기화
with app.app_context():
    db.create_all()

# 라우트 초기화
initialize_routes(app)
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(info_bp, url_prefix='/info')
app.register_blueprint(session_bp, url_prefix = '/sesh')
app.register_blueprint(chat_bp, url_prefix='/chat')

if __name__ == '__main__':
    app.run(debug=True)