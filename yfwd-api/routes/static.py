from flask import Blueprint, send_from_directory

static_bp = Blueprint('static', __name__)

@static_bp.route('/')
def index():
    """首页"""
    return send_from_directory('static', 'index.html')

@static_bp.route('/<path:path>')
def static_file(path):
    """静态文件"""
    return send_from_directory('static', path)