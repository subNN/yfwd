import os
# 设置UTF-8编码，避免GBK编码问题
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 加载 .env 环境变量文件（如果存在）
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    load_dotenv(env_path, override=True)
    if os.path.exists(env_path):
        print(f"[启动] 已加载环境变量文件: {env_path}")
    else:
        print(f"[启动] 未找到 .env 文件，使用系统环境变量")
except ImportError:
    print(f"[启动] python-dotenv 未安装，跳过 .env 加载（请先 pip install python-dotenv）")
except Exception as e:
    print(f"[启动] 加载 .env 文件时出错: {e}")

from flask import Flask, request
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from models.database import Database

# 创建Flask应用
def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    app.config.from_object(Config)
    
    # 配置CORS
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        allow_headers=['Content-Type', 'Authorization', 'token'],
    )

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin')
        response.headers['Access-Control-Allow-Origin'] = origin or '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,token'
        response.headers['Access-Control-Max-Age'] = '86400'
        return response
    
    # 创建数据库实例
    db = Database(Config.DATABASE)
    
    # 注册蓝图 - 延迟导入以避免循环依赖
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.admin import admin_bp
    from routes.upload import upload_bp
    from routes.static import static_bp
    from routes.ai import ai_bp
    
    # 向蓝图传递db实例
    auth_bp.db = db
    user_bp.db = db
    admin_bp.db = db
    upload_bp.db = db
    ai_bp.db = db
    
    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(ai_bp, url_prefix='/api')
    app.register_blueprint(static_bp)
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(e):
        from flask import jsonify
        return jsonify({'error': '接口不存在', 'code': 'NOT_FOUND'}), 404
    
    @app.errorhandler(500)
    def server_error(e):
        print(f"[服务器] 错误: {e}")
        from flask import jsonify
        return jsonify({'error': '服务器内部错误', 'code': 'SERVER_ERROR'}), 500
    
    return app

app = create_app()

# 启动应用
if __name__ == '__main__':
    print("=" * 50)
    print("一饭为定管理系统启动中...")
    print("=" * 50)
    print(f"数据库: {Config.DATABASE}")
    print(f"SMTP邮箱: {Config.QQ_EMAIL}")
    print(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', 'default')}")
    print("=" * 50)
    
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)