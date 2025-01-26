from flask import Blueprint

# إنشاء Blueprint
bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return "مرحبًا بكم في تطبيق Flask!"
