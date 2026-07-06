from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy.exc import IntegrityError
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

import secrets
import re

app = Flask(__name__)

# =========================
# 数据库配置
# =========================
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# =========================
# 安全响应头
# =========================
@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Server"] = ""
    return response

# =========================
# 数据库初始化
# =========================
db = SQLAlchemy(app)

# =========================
# 限流
# =========================
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# =========================
# 用户模型
# =========================
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

# =========================
# 输入校验
# =========================
USERNAME_PATTERN = re.compile(
    r"^[A-Za-z0-9_]{6,20}$"
)

EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)

PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
)

# =========================
# 首页
# =========================
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# =========================
# 注册失败响应
# =========================
def register_failed():
    return jsonify({
        "success": False,
        "message": "注册失败"
    }), 400

# =========================
# 登录失败响应
# =========================
def auth_failed():
    return jsonify({
        "success": False,
        "message": "登录失败"
    }), 401

# =========================
# 注册接口
# =========================
@app.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    try:
        data = request.get_json(silent=True)

        if not data:
            return register_failed()

        username = str(
            data.get("username", "")
        ).strip()

        email = str(
            data.get("email", "")
        ).strip().lower()

        password = str(
            data.get("password", "")
        )

        # 输入校验
        if not USERNAME_PATTERN.fullmatch(username):
            return register_failed()

        if not EMAIL_PATTERN.fullmatch(email):
            return register_failed()

        if not PASSWORD_PATTERN.fullmatch(password):
            return register_failed()

        # 邮箱去重
        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            return register_failed()

        # 密码哈希
        password_hash = generate_password_hash(
            password,
            method="pbkdf2:sha256",
            salt_length=16
        )

        # 创建用户
        user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "注册成功"
        }), 201

    except IntegrityError:
        db.session.rollback()
        return register_failed()

    except Exception:
        return jsonify({
            "success": False,
            "message": "注册失败"
        }), 500

# =========================
# 登录接口
# =========================
@app.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    try:
        data = request.get_json(silent=True)

        if not data:
            return auth_failed()

        email = str(
            data.get("email", "")
        ).strip().lower()

        password = str(
            data.get("password", "")
        )

        if not EMAIL_PATTERN.fullmatch(email):
            return auth_failed()

        if len(password) < 8:
            return auth_failed()

        # 查询用户
        user = User.query.filter_by(
            email=email
        ).first()

        if not user:
            return auth_failed()

        # 校验密码
        if not check_password_hash(
            user.password_hash,
            password
        ):
            return auth_failed()

        # 生成 Token
        token = secrets.token_hex(32)

        return jsonify({
            "success": True,
            "message": "登录成功",
            "token": token
        }), 200

    except Exception:
        return auth_failed()

# =========================
# 限流错误处理
# =========================
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "success": False,
        "message": "请求过于频繁"
    }), 429

# =========================
# 404
# =========================
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "message": "接口不存在"
    }), 404

# =========================
# 启动
# =========================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    # 生产环境不要开启 debug
    # nosec B104: 本地测试需绑定0.0.0.0便于组内演示，生产环境应改为127.0.0.1
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )