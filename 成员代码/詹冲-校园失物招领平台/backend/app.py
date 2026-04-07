# =========================
# 基础配置与初始化
# =========================
import os
from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
from flask_cors import CORS
from datetime import datetime, timedelta
import random
from openai import OpenAI
import hashlib
from pytz import timezone
import cloudinary
import psycopg2
import cloudinary.uploader

# --- LLM、文件上传、数据库等配置 ---
LLM_API_KEY = os.environ.get("LLM_API_KEY")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
DATABASE_URL = os.environ.get('DATABASE_URL')
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'))

cloudinary_ready = all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET])
if cloudinary_ready:
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True
    )

CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['JSON_AS_ASCII'] = False
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
llm_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL) if LLM_API_KEY else None

# =========================
# 数据库与工具函数
# =========================
def get_db_connection():
    """
    获取数据库连接。
    返回数据库连接对象，连接失败时返回 None。
    """
    try:
        if not DATABASE_URL:
            app.logger.error('数据库连接失败: 未配置 DATABASE_URL')
            return None

        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as ex:
        app.logger.error('数据库连接失败: %s', ex)
        return None


def get_json_body():
    return request.get_json(silent=True) or {}


def error_response(message, status_code=400):
    return jsonify({'success': False, 'message': message}), status_code


def empty_list_response(status_code=500):
    return jsonify([]), status_code


def row_to_dict(cursor, row=None):
    if row is None:
        row = cursor.fetchone()
    if row is None:
        return None

    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))


def rows_to_dicts(cursor, rows=None):
    if rows is None:
        rows = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def normalize_event_time(event_time_str):
    event_time = datetime.fromisoformat(event_time_str)
    if event_time.tzinfo is None:
        offset_hours = int(datetime.now().astimezone().utcoffset().total_seconds() // 3600)
        return event_time + timedelta(hours=8 - offset_hours)

    return event_time.astimezone(timezone(timedelta(hours=8))).replace(tzinfo=None)


def upload_image(file):
    if not cloudinary_ready:
        raise RuntimeError('图片服务未配置')

    upload_result = cloudinary.uploader.upload(file)
    return upload_result.get('secure_url')


def log_exception(message):
    app.logger.exception(message)

def allowed_file(filename):
    """
    检查文件名后缀是否为允许的图片类型。
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hash_password(password):
    """
    对明文密码进行 SHA256 哈希，返回哈希值。
    """
    if not password:
        return ''
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def generate_item_id(item_type, cursor):
    """
    根据物品类型生成唯一的物品ID。
    item_type: 'Lost' 或 'Found'。
    """
    prefix = 'L' if item_type == 'Lost' else 'F'
    while True:
        random_part = str(random.randint(100000000, 999999999))
        item_id = prefix + random_part
        cursor.execute('SELECT COUNT(*) FROM "Items" WHERE "ItemID" = %s', (item_id,))
        if cursor.fetchone()[0] == 0:
            return item_id

def create_notification(cursor, user_id, message, notif_type='General', item_id_1=None, item_id_2=None):
    """
    向数据库插入一条通知消息。
    """
    if user_id:
        sql = """
            INSERT INTO "Notifications" ("UserID", "Message", "NotificationType", "RelatedItemID_1", "RelatedItemID_2") 
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (user_id, message, notif_type, item_id_1, item_id_2))

# =========================
# 静态文件与根路由
# =========================
@app.route('/')
def serve_root():
    """
    根路由，重定向到登录页面。
    """
    return redirect(url_for('serve_static', path='login.html'))

@app.route('/<path:path>')
def serve_static(path):
    """
    静态文件服务路由。
    """
    if path == 'volunteer.html':
         return send_from_directory(app.static_folder, 'volunteer.html')
    return send_from_directory(app.static_folder, path)

# =========================
# 用户认证与管理
# =========================

@app.route('/api/register', methods=['POST'])
def register():
    """
    用户注册接口。
    接收用户名、密码、安全问题和答案进行注册。
    """
    data = get_json_body()
    username = data.get('username')
    password = data.get('password')
    security_question = data.get('securityQuestion')
    security_answer = data.get('securityAnswer')

    if not all([username, password, security_question, security_answer]):
        return error_response('所有字段均为必填项')

    password_hash = hash_password(password)
    answer_hash = hash_password(security_answer)

    conn = get_db_connection()
    if not conn:
        return error_response('数据库连接失败', 500)

    cursor = conn.cursor()
    try:
        cursor.execute('SELECT "UserID" FROM "Users" WHERE "Username" = %s', (username,))
        if cursor.fetchone():
            return error_response('用户名已存在', 409)

        sql = """
            INSERT INTO "Users" ("Username", "Password", "PasswordHash", "UserRole", "SecurityQuestion", "SecurityAnswerHash")
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (username, '', password_hash, '普通用户', security_question, answer_hash))
        conn.commit()
        return jsonify({'success': True, 'message': '注册成功！'})
    except Exception:
        conn.rollback()
        log_exception('Register error')
        return error_response('注册时发生服务器错误', 500)
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    """
    用户登录接口。
    接收用户名和密码，返回用户信息及登录状态。
    """
    data = get_json_body()
    username = data.get('username')
    password = data.get('password')

    if not password:
        return error_response('密码不能为空')

    password_hash = hash_password(password)

    conn = get_db_connection()
    if not conn:
        return error_response('数据库连接失败', 500)
    cursor = conn.cursor()

    sql = """
        SELECT "UserID", "Username", "UserRole", "SecurityQuestion"
        FROM "Users"
        WHERE "Username" = %s AND "PasswordHash" = %s
    """
    cursor.execute(sql, (username, password_hash))
    user_dict = row_to_dict(cursor)

    if user_dict:
        conn.close()
        return jsonify({'success': True, 'user': {
            'userID': user_dict['UserID'],
            'username': user_dict['Username'],
            'userRole': user_dict['UserRole'],
            'securityQuestion': user_dict['SecurityQuestion']
        }})

    conn.close()
    return error_response('用户名或密码错误', 401)

@app.route('/api/get-security-question', methods=['POST'])
def get_security_question():
    """
    根据用户名获取其设置的安全问题。
    """
    data = get_json_body()
    username = data.get('username')
    if not username:
        return error_response('必须提供用户名')

    conn = get_db_connection()
    if not conn:
        return error_response('数据库连接失败', 500)

    cursor = conn.cursor()
    cursor.execute('SELECT "SecurityQuestion" FROM "Users" WHERE "Username" = %s', (username,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data and user_data[0]:
        return jsonify({'success': True, 'question': user_data[0]})

    return error_response('未找到该用户或用户未设置安全问题', 404)

@app.route('/api/reset-password-with-answer', methods=['POST'])
def reset_password_with_answer():
    """
    验证安全问题答案并重置密码。
    """
    data = get_json_body()
    username = data.get('username')
    answer = data.get('answer')
    new_password = data.get('newPassword')

    if not all([username, answer, new_password]):
        return error_response('缺少必要参数')

    answer_hash = hash_password(answer)
    new_password_hash = hash_password(new_password)

    conn = get_db_connection()
    if not conn:
        return error_response('数据库连接失败', 500)

    cursor = conn.cursor()
    try:
        cursor.execute('SELECT "SecurityAnswerHash" FROM "Users" WHERE "Username" = %s', (username,))
        user_data = cursor.fetchone()

        if not user_data or user_data[0] != answer_hash:
            return error_response('安全问题答案不正确')

        update_sql = 'UPDATE "Users" SET "Password" = %s, "PasswordHash" = %s WHERE "Username" = %s'
        cursor.execute(update_sql, ('', new_password_hash, username))
        conn.commit()

        return jsonify({'success': True, 'message': '密码重置成功！'})
    except Exception as e:
        conn.rollback()
        log_exception('Reset password error')
        return error_response(f'密码重置失败: {e}', 500)
    finally:
        conn.close()

@app.route('/api/notifications/mark-read/<int:notification_id>', methods=['POST'])
def mark_notification_as_read(notification_id):
    """
    标记通知为已读。
    接收通知ID和用户ID，更新通知状态。
    """
    data = get_json_body()
    user_id = data.get('userID')
    if not user_id:
        return error_response('用户ID缺失')

    conn = get_db_connection()
    if not conn:
        return error_response('数据库连接失败', 500)

    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT "IsRead" FROM "Notifications" WHERE "NotificationID" = %s AND "UserID" = %s',
            (notification_id, user_id)
        )
        notification = cursor.fetchone()

        if not notification:
            return error_response('通知不存在或无权限', 404)

        if notification[0]:
            return jsonify({'success': True, 'message': '通知已经是已读状态'})

        cursor.execute(
            'UPDATE "Notifications" SET "IsRead" = TRUE WHERE "NotificationID" = %s AND "UserID" = %s',
            (notification_id, user_id)
        )
        conn.commit()

        if cursor.rowcount > 0:
            return jsonify({'success': True, 'message': '通知已标记为已读'})

        return error_response('操作失败')
    except Exception:
        conn.rollback()
        log_exception('Mark notification as read error')
        return error_response('服务器错误', 500)
    finally:
        conn.close()

@app.route('/api/user/update', methods=['POST'])
def update_user_info():
    """
    更新用户信息（现在只更新用户名）。
    """
    data = request.json
    user_id, username = data.get('userID'), data.get('username')
    conn = get_db_connection()
    if not conn: return jsonify({'success': False, 'message': '数据库错误'}), 500
    cursor = conn.cursor()
    try:
        sql = 'UPDATE "Users" SET "Username" = %s WHERE "UserID" = %s'
        cursor.execute(sql, (username, user_id))
        
        create_notification(cursor, user_id, f"您的用户名已成功修改为: {username}。")
        conn.commit()
        return jsonify({'success': True, 'message': '信息更新成功'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {e}'}), 500
    finally:
        conn.close()

@app.route('/api/user/update-security', methods=['POST'])
def update_user_security():
    """
    更新用户的安全问题和答案，需要验证当前密码。
    """
    data = request.json
    user_id = data.get('userID')
    password = data.get('password')
    new_question = data.get('newQuestion')
    new_answer = data.get('newAnswer')

    if not all([user_id, password, new_question, new_answer]):
        return jsonify({'success': False, 'message': '所有字段均为必填项'}), 400

    password_hash = hash_password(password)
    new_answer_hash = hash_password(new_answer)

    conn = get_db_connection()
    if not conn: return jsonify({'success': False, 'message': '数据库连接失败'}), 500
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT "PasswordHash" FROM "Users" WHERE "UserID" = %s', (user_id,))
        user_data = cursor.fetchone()
        if not user_data or user_data[0] != password_hash:
            return jsonify({'success': False, 'message': '当前密码不正确'}), 401
        
        sql = 'UPDATE "Users" SET "SecurityQuestion" = %s, "SecurityAnswerHash" = %s WHERE "UserID" = %s'
        cursor.execute(sql, (new_question, new_answer_hash, user_id))
        
        create_notification(cursor, user_id, "您的安全问题和答案已成功更新。")
        conn.commit()
        return jsonify({'success': True, 'message': '安全设置更新成功'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {e}'}), 500
    finally:
        conn.close()

@app.route('/api/user/change-password', methods=['POST'])
def change_password():
    """
    修改用户密码。
    接收用户ID、原密码和新密码，更新用户密码。
    """
    data = request.json
    user_id = data.get('userID')
    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')
    confirm_password = data.get('confirmPassword')

    if user_id is None or not old_password or not new_password or not confirm_password:
        return jsonify({'success': False, 'message': '所有字段均为必填项'}), 400

    if new_password != confirm_password:
        return jsonify({'success': False, 'message': '两次输入的新密码不一致'}), 400

    old_password_hash = hash_password(old_password)
    new_password_hash = hash_password(new_password)

    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库错误'}), 500
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT "PasswordHash" FROM "Users" WHERE "UserID" = %s', (user_id,))
        user_data = cursor.fetchone()
        if not user_data:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        if user_data[0] != old_password_hash:
            return jsonify({'success': False, 'message': '原密码不正确，请重新输入'}), 400

        sql = 'UPDATE "Users" SET "Password" = %s, "PasswordHash" = %s WHERE "UserID" = %s'
        cursor.execute(sql, ('', new_password_hash, user_id))
        
        create_notification(cursor, user_id, "您的密码已成功修改。")
        conn.commit()
        return jsonify({'success': True, 'message': '密码修改成功'})
    except Exception as e:
        conn.rollback()
        log_exception('Change password error')
        return jsonify({'success': False, 'message': f'修改失败: {e}'}), 500
    finally:
        conn.close()

# =========================
# 管理员功能
# =========================
@app.route('/api/admin/user/delete/<int:user_id_to_delete>', methods=['DELETE'])
def admin_delete_user(user_id_to_delete):
    """
    管理员删除用户。
    接收要删除的用户ID，执行用户删除操作。
    """
    data = request.json
    admin_id = data.get('adminID')
    
    conn = get_db_connection()
    if not conn: return jsonify({'success': False, 'message': '数据库错误'}), 500
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT "UserRole" FROM "Users" WHERE "UserID" = %s', (admin_id,))
        admin_data = cursor.fetchone()
        if not admin_data or admin_data[0] != '管理员':
            return jsonify({'success': False, 'message': '无权限操作'}), 403

        if admin_id == user_id_to_delete:
            return jsonify({'success': False, 'message': '不能删除自己的账户'}), 400

        cursor.execute('DELETE FROM "Users" WHERE "UserID" = %s', (user_id_to_delete,))
        conn.commit()
        
        if cursor.rowcount > 0:
            return jsonify({'success': True, 'message': '用户已永久删除'})
        else:
            return jsonify({'success': False, 'message': '未找到该用户'}), 404

    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'success': False, 'message': '删除失败。请先移除该用户发布的物品或关联的聊天记录。'}), 409
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'删除时发生错误: {e}'}), 500
    finally:
        conn.close()

@app.route('/api/admin/item/update', methods=['POST'])
def admin_update_item():
    """
    管理员更新物品信息。
    接收物品ID和更新的物品信息，修改物品记录。
    """
    data = request.json
    admin_id = data.get('adminID')
    
    conn = get_db_connection()
    if not conn: return jsonify({'success': False, 'message': '数据库错误'}), 500
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT "UserRole" FROM "Users" WHERE "UserID" = %s', (admin_id,))
        admin_data = cursor.fetchone()
        if not admin_data or admin_data[0] != '管理员':
            return jsonify({'success': False, 'message': '无权限操作'}), 403

        item_id = data.get('itemID')
        item_name = data.get('itemName')
        item_status = data.get('itemStatus')
        description = data.get('description')
        
        sql = """
            UPDATE "Items" SET "ItemName" = %s, "ItemStatus" = %s, "Description" = %s 
            WHERE "ItemID" = %s
        """
        cursor.execute(sql, (item_name, item_status, description, item_id))
        conn.commit()
        
        return jsonify({'success': True, 'message': '物品信息更新成功'})

    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {e}'}), 500
    finally:
        conn.close()

@app.route('/api/admin/item/delete/<string:item_id>', methods=['DELETE'])
def admin_delete_item(item_id):
    """
    管理员删除物品。
    接收物品ID，执行物品删除操作。
    """
    data = request.json
    admin_id = data.get('adminID')

    conn = get_db_connection()
    if not conn: return jsonify({'success': False, 'message': '数据库错误'}), 500
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT "UserRole" FROM "Users" WHERE "UserID" = %s', (admin_id,))
        admin_data = cursor.fetchone()
        if not admin_data or admin_data[0] != '管理员':
            return jsonify({'success': False, 'message': '无权限操作'}), 403
        
        cursor.execute('UPDATE "Items" SET "ItemStatus" = %s WHERE "ItemID" = %s', ('已删除', item_id))
        conn.commit()

        if cursor.rowcount > 0:
            return jsonify({'success': True, 'message': '物品已标记为删除'})
        else:
            return jsonify({'success': False, 'message': '未找到该物品'}), 404
            
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {e}'}), 500
    finally:
        conn.close()

# =========================
# 物品管理
# =========================

@app.route('/api/items', methods=['GET'])
def get_items():
    """
    获取物品列表。
    支持根据类型、搜索词和分类过滤。
    """
    item_type = request.args.get('type')
    search_term = request.args.get('search', '')
    categories = request.args.getlist('category')

    conn = get_db_connection()
    if not conn: return jsonify([]), 500
    cursor = conn.cursor()

    sql_query = """
        SELECT i.*, u."Username" as posterUsername
        FROM "Items" i
        LEFT JOIN "Users" u ON i."UserID" = u."UserID"
        WHERE i."ItemType" = %s AND i."ItemStatus" NOT IN ('已删除')
    """
    params = [item_type]

    if search_term:
        sql_query += ' AND (i."ItemName" LIKE %s OR i."Description" LIKE %s OR i."Location" LIKE %s)'
        search_like = f"%{search_term}%"
        params.extend([search_like, search_like, search_like])

    if categories:
        placeholders = ','.join(['%s'] * len(categories))
        sql_query += f' AND i."Category" IN ({placeholders})'
        params.extend(categories)

    sql_query += ' ORDER BY i."PostTime" DESC'

    cursor.execute(sql_query, params)
    items = rows_to_dicts(cursor)
    conn.close()
    return jsonify(items)

@app.route('/api/items', methods=['POST'])
def add_item():
    """
    发布新物品信息。
    接收物品的各类信息，插入数据库。
    """
    user_id = request.form.get('userID')
    conn = get_db_connection()
    if not conn: return jsonify({'success': False, 'message': '数据库连接失败'}), 500
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT "UserRole" FROM "Users" WHERE "UserID" = %s', (user_id,))
        user_data = cursor.fetchone()
        if not user_data or user_data[0] in ['志愿者', '管理员']:
            return jsonify({'success': False, 'message': '您没有权限发布信息'}), 403

        item_type = request.form.get('itemType')
        item_name = request.form.get('itemName')
        event_time_str = request.form.get('eventTime')

        if not all([item_type, item_name, event_time_str]):
            return jsonify({'success': False, 'message': '缺少必要信息'}), 400

        image_path = None
        if 'image' in request.files:
            if not cloudinary_ready:
                return jsonify({'success': False, 'message': '图片服务未配置'}), 500
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                image_path = upload_image(file)
        
        if item_type == 'Found' and not image_path:
            return jsonify({'success': False, 'message': '捡到物品必须上传图片'}), 400

        item_id = generate_item_id(item_type, cursor)
        
        event_time = normalize_event_time(event_time_str)

        sql = """
            INSERT INTO "Items" 
            ("ItemID", "UserID", "ItemType", "ItemName", "Category", "Color", "Location", "EventTime", "Description", "ImagePath", "ItemStatus") 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            item_id, user_id, item_type, request.form.get('itemName'), 
            request.form.get('category', '其他'), request.form.get('color', '未知'), 
            request.form.get('location', '未知'), event_time, 
            request.form.get('description', ''), image_path, '未找到'
        )
        cursor.execute(sql, params)
        conn.commit()
        return jsonify({'success': True, 'message': '信息发布成功！', 'itemID': item_id})
    except Exception as e:
        conn.rollback()
        log_exception('Add item error')
        return jsonify({'success': False, 'message': '发布失败'}), 500
    finally:
        conn.close()

@app.route('/api/items/<string:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """
    删除物品信息。
    接收物品ID，执行逻辑删除操作。
    """
    user_id = request.json.get('userID')
    conn = get_db_connection()
    if not conn: return jsonify({'success': False, 'message': '数据库错误'}), 500
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT "UserID", "UserRole" FROM "Users" WHERE "UserID" = %s', (user_id,))
        user_data = cursor.fetchone()
        
        cursor.execute('SELECT "UserID" FROM "Items" WHERE "ItemID" = %s', (item_id,))
        item_data = cursor.fetchone()

        if not user_data or not item_data:
            return jsonify({'success': False, 'message': '未找到用户或物品'}), 404

        user_columns = [desc[0] for desc in cursor.description]
        user = dict(zip(user_columns, user_data))
        
        item_owner_id = item_data[0]

        if user['UserID'] == item_owner_id or user['UserRole'] == '管理员':
            cursor.execute('UPDATE "Items" SET "ItemStatus" = %s WHERE "ItemID" = %s', ('已删除', item_id))
            conn.commit()
            return jsonify({'success': True, 'message': '删除成功'})
        else:
            return jsonify({'success': False, 'message': '无权删除'}), 403
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {e}'}), 500
    finally:
        conn.close()

@app.route('/api/items/user/<int:user_id>', methods=['GET'])
def get_user_items(user_id):
    """
    获取用户发布的物品列表。
    支持根据物品类型和状态过滤。
    """
    item_type_filter = request.args.get('type')
    status_filter = request.args.get('status')

    conn = get_db_connection()
    if not conn: return jsonify([]), 500
    cursor = conn.cursor()
    
    sql = 'SELECT * FROM "Items" WHERE "UserID" = %s AND "ItemStatus" <> %s'
    params = [user_id, '已删除']
    
    if item_type_filter:
        sql += ' AND "ItemType" = %s'
        params.append(item_type_filter)
    
    if status_filter:
        sql += ' AND "ItemStatus" = %s'
        params.append(status_filter)

    sql += ' ORDER BY "PostTime" DESC'
    
    cursor.execute(sql, params)
    items = rows_to_dicts(cursor)
    conn.close()
    return jsonify(items)

@app.route('/api/item/update', methods=['POST'])
def update_item():
    """
    更新物品信息。
    接收物品ID和要更新的字段，修改物品记录。
    """
    data = request.json
    user_id = data.get('userID')
    item_id = data.get('itemID')

    if not all([user_id, item_id]):
        return jsonify({'success': False, 'message': '缺少必要的用户或物品ID'}), 400

    conn = get_db_connection()
    if not conn: return jsonify({'success': False, 'message': '数据库连接失败'}), 500
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT "UserID" FROM "Items" WHERE "ItemID" = %s', (item_id,))
        item_data = cursor.fetchone()
        if not item_data or item_data[0] != user_id:
            return jsonify({'success': False, 'message': '无权限修改此物品'}), 403

        item_name = data.get('itemName')
        category = data.get('category')
        color = data.get('color')
        location = data.get('location')
        event_time = datetime.fromisoformat(data.get('eventTime'))
        description = data.get('description')
        item_status = data.get('itemStatus')

        sql_update = """
            UPDATE "Items" SET
            "ItemName" = %s, "Category" = %s, "Color" = %s, "Location" = %s,
            "EventTime" = %s, "Description" = %s, "ItemStatus" = %s
            WHERE "ItemID" = %s AND "UserID" = %s
        """
        params = (
            data.get('itemName'), data.get('category'), data.get('color'),
            data.get('location'), event_time, data.get('description'),
            data.get('itemStatus'), item_id, user_id
        )
        cursor.execute(sql_update, params)
        
        if data.get('itemStatus') == '已找回':
            cursor.execute('SELECT "MatchItemID" FROM "Items" WHERE "ItemID" = %s', (item_id,))
            match_item_row = cursor.fetchone()
            if match_item_row and match_item_row[0]:
                cursor.execute('UPDATE "Items" SET "ItemStatus" = %s WHERE "ItemID" = %s', ('已找回', match_item_row[0]))

        conn.commit()
        return jsonify({'success': True, 'message': '物品信息更新成功！'})

    except Exception as e:
        conn.rollback()
        log_exception('Update item error')
        return jsonify({'success': False, 'message': '更新失败，服务器发生错误'}), 500
    finally:
        conn.close()

# =========================
# 认领与聊天
# =========================

@app.route('/api/claim/initiate', methods=['POST'])
def initiate_claim():
    """
    发起认领请求。
    接收认领人ID和拾物ID，创建认领记录。
    """
    data = request.json
    claimant_id = data.get('userID')
    found_item_id = data.get('foundItemID')
    match_lost_item_id = data.get('matchLostItemID')

    if not claimant_id or not found_item_id:
        return jsonify({'success': False, 'message': '缺少必要参数'}), 400

    conn = get_db_connection()
    if not conn: return jsonify({'success': False, 'message': '数据库连接失败'}), 500
    cursor = conn.cursor()

    try:
        sql_found = """
            SELECT i."UserID", i."ItemName", u."Username" 
            FROM "Items" i JOIN "Users" u ON i."UserID" = u."UserID" 
            WHERE i."ItemID" = %s
        """
        cursor.execute(sql_found, (found_item_id,))
        found_item_data = cursor.fetchone()
        if not found_item_data:
            return jsonify({'success': False, 'message': '拾物信息不存在'}), 404

        columns = [desc[0] for desc in cursor.description]
        found_item = dict(zip(columns, found_item_data))
        
        finder_id = found_item['UserID']
        if int(claimant_id) == finder_id:
            return jsonify({'success': False, 'message': '您不能认领自己发布的拾物'}), 403

        lost_item_id_to_use = match_lost_item_id
        
        if not match_lost_item_id:
            lost_item_id_to_use = generate_item_id('Lost', cursor)
            item_name = f"对“{found_item['ItemName']}”的认领"
            description = f"此条目为系统自动生成，用于用户(ID: {claimant_id})与拾主(ID: {finder_id})就物品(ID: {found_item_id})进行沟通。"
            
            sql_insert_lost = """
                INSERT INTO "Items" ("ItemID", "UserID", "ItemType", "ItemName", "Description", "ItemStatus") 
                VALUES (%s, %s, 'Lost', %s, %s, '正在联系中')
            """
            cursor.execute(sql_insert_lost, (lost_item_id_to_use, claimant_id, item_name, description))
            lost_item_name = item_name
        else:
            cursor.execute('SELECT "ItemName" FROM "Items" WHERE "ItemID" = %s AND "UserID" = %s', (match_lost_item_id, claimant_id))
            lost_item_data = cursor.fetchone()
            if not lost_item_data:
                 return jsonify({'success': False, 'message': '您选择的失物信息无效或不属于您'}), 403
            lost_item_name = lost_item_data[0]

        new_status = '正在联系中'
        cursor.execute('UPDATE "Items" SET "ItemStatus" = %s, "MatchItemID" = %s WHERE "ItemID" = %s', (new_status, found_item_id, lost_item_id_to_use))
        cursor.execute('UPDATE "Items" SET "ItemStatus" = %s, "MatchItemID" = %s WHERE "ItemID" = %s', (new_status, lost_item_id_to_use, found_item_id))

        cursor.execute('SELECT "Username" FROM "Users" WHERE "UserID" = %s', (claimant_id,))
        claimant_username = cursor.fetchone()[0]
        
        msg_for_claimant = f"您已成功认领物品“{found_item['ItemName']}”，系统已为您开启与拾主“{found_item['Username']}”的私信，请尽快沟通确认。"
        create_notification(cursor, claimant_id, msg_for_claimant, 'Match', lost_item_id_to_use, found_item_id)
        
        msg_for_finder = f"用户“{claimant_username}”认领了您发布的拾物“{found_item['ItemName']}”，并关联到失物“{lost_item_name}”。请进入私信与对方确认。"
        create_notification(cursor, finder_id, msg_for_finder, 'Match', lost_item_id_to_use, found_item_id)

        conn.commit()
        return jsonify({
            'success': True, 
            'message': '认领成功，已开启私信！',
            'lostItemID': lost_item_id_to_use,
            'foundItemID': found_item_id
        })
    except Exception as e:
        conn.rollback()
        log_exception('Claim initiate error')
        return jsonify({'success': False, 'message': '操作失败'}), 500
    finally:
        conn.close()

@app.route('/api/messages/<lost_item_id>/<found_item_id>', methods=['GET'])
def get_messages(lost_item_id, found_item_id):
    """
    获取聊天记录。
    接收失物ID和拾物ID，返回两者之间的消息记录。
    """
    conn = get_db_connection()
    if not conn: return jsonify([]), 500
    cursor = conn.cursor()
    sql = """
        SELECT m."MessageID", m."SenderID", u_sender."Username" as senderName, m."Content", m."SentTime"
        FROM "Messages" m
        JOIN "Users" u_sender ON m."SenderID" = u_sender."UserID"
        WHERE m."LostItemID" = %s AND m."FoundItemID" = %s
        ORDER BY m."SentTime" ASC
    """
    cursor.execute(sql, (lost_item_id, found_item_id))
    messages = rows_to_dicts(cursor)
    
    conn.close()
    
    for msg in messages:
        if msg.get('SentTime'):
            msg['SentTime'] = msg['SentTime'].isoformat()
            
    return jsonify(messages)

@app.route('/api/messages', methods=['POST'])
def send_message():
    """
    发送消息。
    接收发送者ID、失物ID、拾物ID和消息内容，插入消息记录。
    """
    sender_id = request.form.get('senderID')
    lost_item_id = request.form.get('lostItemID')
    found_item_id = request.form.get('foundItemID')
    content = request.form.get('content')
    
    conn = get_db_connection()
    if not conn: return jsonify({'success': False, 'message': '数据库连接失败'}), 500
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT "UserID", "ItemName" FROM "Items" WHERE "ItemID" = %s', (lost_item_id,))
        lost_item_data = cursor.fetchone()
        cursor.execute('SELECT "UserID", "ItemName" FROM "Items" WHERE "ItemID" = %s', (found_item_id,))
        found_item_data = cursor.fetchone()

        if not lost_item_data or not found_item_data:
             return jsonify({'success': False, 'message': '关联物品不存在'}), 404
        
        lost_item_dict = {'UserID': lost_item_data[0], 'ItemName': lost_item_data[1]}
        found_item_dict = {'UserID': found_item_data[0], 'ItemName': found_item_data[1]}
        
        lost_user_id = lost_item_dict['UserID']
        found_user_id = found_item_dict['UserID']
        sender_id = int(sender_id)
        receiver_id = found_user_id if sender_id == lost_user_id else lost_user_id
        
        image_path_for_response = None
        message_sent = False

        if 'image' in request.files:
            if not cloudinary_ready:
                return jsonify({'success': False, 'message': '图片服务未配置'}), 500
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                image_path = upload_image(file)
                cursor.execute(
                    'INSERT INTO "Messages" ("SenderID", "ReceiverID", "LostItemID", "FoundItemID", "Content") VALUES (%s, %s, %s, %s, %s)',
                    (sender_id, receiver_id, lost_item_id, found_item_id, image_path)
                )
                message_sent = True
                image_path_for_response = image_path
        elif content:
            cursor.execute(
                'INSERT INTO "Messages" ("SenderID", "ReceiverID", "LostItemID", "FoundItemID", "Content") VALUES (%s, %s, %s, %s, %s)',
                (sender_id, receiver_id, lost_item_id, found_item_id, content)
            )
            message_sent = True

        if not message_sent:
            return jsonify({'success': False, 'message': '消息内容不能为空'}), 400

        notify_item_name = found_item_dict['ItemName'] if sender_id == lost_user_id else lost_item_dict['ItemName']
        notification_message = f"您收到关于物品“{notify_item_name}”的新消息。"
        create_notification(cursor, receiver_id, notification_message, 'NewMessage', lost_item_id, found_item_id)
        
        conn.commit()
        response_data = {'success': True, 'content': image_path_for_response} if image_path_for_response else {'success': True}
        return jsonify(response_data)
        
    except Exception as e:
        conn.rollback()
        log_exception('Send message error')
        return jsonify({'success': False, 'message': f'发送失败: {e}'}), 500
    finally:
        cursor.close()
        conn.close()

        
@app.route('/api/chats', methods=['GET'])
def get_user_chats():
    """
    获取用户的聊天会话列表。
    返回用户参与的所有聊天会话的简要信息。
    """
    user_id_str = request.args.get('userID')
    if not user_id_str: return jsonify([]), 400
    user_id = int(user_id_str)

    conn = get_db_connection()
    if not conn: return jsonify([]), 500
    cursor = conn.cursor()

    sql = """
    WITH "LastMessages" AS (
        SELECT
            "LostItemID", "FoundItemID", "Content", "SentTime",
            ROW_NUMBER() OVER(PARTITION BY "LostItemID", "FoundItemID" ORDER BY "SentTime" DESC) as rn
        FROM "Messages"
    ),
    "ChatPairs" AS (
        SELECT DISTINCT "LostItemID", "FoundItemID"
        FROM "Messages"
        WHERE "SenderID" = %s OR "ReceiverID" = %s
    )
    SELECT
        cp."LostItemID", i_lost."ItemName" as "LostItemName", i_lost."UserID" as "LostUserID",
        cp."FoundItemID", i_found."ItemName" as "FoundItemName", i_found."UserID" as "FoundUserID",
        lm."Content" as "LastMessage",
        lm."SentTime" as "LastMessageTime",
        CASE WHEN i_lost."UserID" = %s THEN u_found."Username" ELSE u_lost."Username" END as "OtherUsername",
        CASE WHEN i_lost."UserID" = %s THEN u_found."UserID" ELSE u_lost."UserID" END as "OtherUserID",
        i_lost."ItemStatus" as "LostItemStatus"
    FROM "ChatPairs" cp
    JOIN "Items" i_lost ON cp."LostItemID" = i_lost."ItemID"
    JOIN "Items" i_found ON cp."FoundItemID" = i_found."ItemID"
    JOIN "Users" u_lost ON i_lost."UserID" = u_lost."UserID"
    JOIN "Users" u_found ON i_found."UserID" = u_found."UserID"
    LEFT JOIN "LastMessages" lm ON cp."LostItemID" = lm."LostItemID" AND cp."FoundItemID" = lm."FoundItemID" AND lm.rn = 1
    WHERE i_lost."ItemStatus" <> '已删除' AND i_found."ItemStatus" <> '已删除'
    ORDER BY lm."SentTime" DESC;
    """
    try:
        cursor.execute(sql, (user_id, user_id, user_id, user_id))
        columns = [column[0] for column in cursor.description]
        chats = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        active_chats = [c for c in chats if c.get('LostItemStatus') != '已找回']
        return jsonify(active_chats)
    except Exception as e:
        log_exception('Error fetching chats')
        return jsonify([]), 500
    finally:
        conn.close()


@app.route('/api/chat/resolve', methods=['POST'])
def resolve_chat():
    """
    处理聊天认领结果。
    接收用户ID、失物ID、拾物ID和操作类型，更新物品状态。
    """
    data = request.json
    user_id, lost_item_id, found_item_id, action = data.get('userID'), data.get('lostItemID'), data.get('foundItemID'), data.get('action')

    if not all([user_id, lost_item_id, found_item_id, action]):
        return jsonify({'success': False, 'message': '缺少参数'}), 400

    conn = get_db_connection()
    if not conn: return jsonify({'success': False, 'message': '数据库连接失败'}), 500
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT "UserID", "ItemName" FROM "Items" WHERE "ItemID" = %s', (lost_item_id,))
        lost_item_data = cursor.fetchone()
        
        if not lost_item_data or user_id != lost_item_data[0]:
            return jsonify({'success': False, 'message': '只有失主才能操作'}), 403

        lost_item_name = lost_item_data[1]

        if action == 'found':
            cursor.execute('UPDATE "Items" SET "ItemStatus" = %s WHERE "ItemID" IN (%s, %s)', ('已找回', lost_item_id, found_item_id))
            message = '操作成功，物品已标记为“已找回”'
        elif action == 'not_found':
            if lost_item_name.startswith("对“") and lost_item_name.endswith("”的认领"):
                cursor.execute('UPDATE "Items" SET "ItemStatus" = %s WHERE "ItemID" = %s', ('已删除', lost_item_id))
            else:
                cursor.execute('UPDATE "Items" SET "ItemStatus" = %s, "MatchItemID" = NULL WHERE "ItemID" = %s', ('未找到', lost_item_id))
            
            cursor.execute('UPDATE "Items" SET "ItemStatus" = %s, "MatchItemID" = NULL WHERE "ItemID" = %s', ('未找到', found_item_id))
            message = '操作成功，已取消匹配'
        else:
            return jsonify({'success': False, 'message': '无效的操作'}), 400

        conn.commit()
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        conn.rollback()
        log_exception('Resolve chat error')
        return jsonify({'success': False, 'message': '操作失败'}), 500
    finally:
        conn.close()

# =========================
# 通知系统
# =========================

@app.route('/api/notifications/<int:user_id>', methods=['GET'])
def get_notifications(user_id):
    """
    获取用户通知列表。
    接收用户ID，返回该用户的所有通知。
    """
    conn = get_db_connection()
    if not conn: return jsonify([]), 500
    cursor = conn.cursor()
    try:
        sql = """
            SELECT "NotificationID", "RelatedItemID_1", "RelatedItemID_2", "Message", "IsRead", "CreationTime", "NotificationType" 
            FROM "Notifications" WHERE "UserID" = %s 
            ORDER BY "CreationTime" DESC
        """
        cursor.execute(sql, (user_id,))
        notifications = rows_to_dicts(cursor)
        return jsonify(notifications)
    except Exception as e:
        log_exception('Error fetching notifications')
        return jsonify([]), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/volunteer/match', methods=['POST'])
def volunteer_ai_match():
    """
    志愿者AI智能匹配接口。
    接收物品ID，返回与之匹配的物品列表。
    """
    data = request.json
    item_id = data.get('itemID')
    if not item_id:
        return jsonify({'success': False, 'message': '缺少物品ID'}), 400
    if llm_client is None:
        return jsonify({'success': False, 'message': 'AI服务未配置'}), 500
    
    conn = get_db_connection()
    if not conn: return jsonify({'success': False, 'message': '数据库连接失败'}), 500
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM "Items" WHERE "ItemID" = %s', (item_id,))
        source_item_data = cursor.fetchone()
        if not source_item_data:
            return jsonify({'success': False, 'message': '物品不存在'}), 404
        
        columns = [desc[0] for desc in cursor.description]
        source_item = dict(zip(columns, source_item_data))

        source_item_type = source_item['ItemType']
        target_item_type = 'Found' if source_item_type == 'Lost' else 'Lost'

        source_item_desc = f"物品名: {source_item['ItemName']}, 类别: {source_item['Category']}, 颜色: {source_item['Color']}, 地点: {source_item['Location']}, 描述: {source_item['Description']}"
        
        cursor.execute('SELECT * FROM "Items" WHERE "ItemType" = %s AND "ItemStatus" = %s AND "UserID" <> %s', 
                       (target_item_type, '未找到', source_item['UserID']))
        target_items_data = cursor.fetchall()
        
        target_columns = [desc[0] for desc in cursor.description]
        potential_matches = []

        for target_item_tuple in target_items_data:
            target_item = dict(zip(target_columns, target_item_tuple))
            target_item_desc = f"物品名: {target_item['ItemName']}, 类别: {target_item['Category']}, 颜色: {target_item['Color']}, 地点: {target_item['Location']}, 描述: {target_item['Description']}"
           
            try:
                if source_item_type == 'Lost':
                    prompt_content = f"失物: {source_item_desc}\n拾物: {target_item_desc}"
                else:
                    prompt_content = f"失物: {target_item_desc}\n拾物: {source_item_desc}"

                completion = llm_client.chat.completions.create(
                    model="qwen-turbo",
                    messages=[
                        {'role': 'system', 'content': '你是一个失物招领匹配助手。请判断以下两个物品是否高度相似，只需要回答“是”或“否”。'},
                        {'role': 'user', 'content': prompt_content}
                    ],
                    temperature=0
                )
                is_match = completion.choices[0].message.content
                if '是' in is_match:
                    potential_matches.append(target_item)

            except Exception as llm_error:
                app.logger.warning(
                    'LLM API call failed for item %s: %s',
                    target_item['ItemID'],
                    llm_error
                )
                continue
        
        return jsonify({'success': True, 'matches': potential_matches})

    except Exception as e:
        log_exception('AI Match error')
        return jsonify({'success': False, 'message': 'AI匹配时发生服务器错误'}), 500
    finally:
        conn.close()

@app.route('/api/volunteer/link', methods=['POST'])
def volunteer_link_items():
    """
    志愿者人工匹配接口。
    接收志愿者ID、失物ID和拾物ID，执行物品关联操作。
    """
    data = request.json
    operator_id = data.get('operatorID') or data.get('volunteerID')
    lost_item_id = data.get('lostItemID')
    found_item_id = data.get('foundItemID')

    conn = get_db_connection()
    if not conn: return jsonify({'success': False, 'message': '数据库连接失败'}), 500
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT "UserRole" FROM "Users" WHERE "UserID" = %s', (operator_id,))
        operator = cursor.fetchone()
        if not operator:
            return jsonify({'success': False, 'message': '无效的用户ID或未登录'}), 403

        cursor.execute('SELECT "UserID", "ItemName" FROM "Items" WHERE "ItemID" = %s', (lost_item_id,))
        lost_item_data = cursor.fetchone()
        cursor.execute('SELECT "UserID", "ItemName" FROM "Items" WHERE "ItemID" = %s', (found_item_id,))
        found_item_data = cursor.fetchone()

        if not lost_item_data or not found_item_data:
            return jsonify({'success': False, 'message': '物品不存在'}), 404

        lost_user_id, lost_item_name = lost_item_data
        found_user_id, found_item_name = found_item_data

        if lost_user_id == found_user_id:
            return jsonify({'success': False, 'message': '不能匹配同一个用户发布的失物和拾物信息！'}), 400

        new_status = '正在联系中'
        cursor.execute('UPDATE "Items" SET "ItemStatus" = %s, "MatchItemID" = %s WHERE "ItemID" = %s', (new_status, found_item_id, lost_item_id))
        cursor.execute('UPDATE "Items" SET "ItemStatus" = %s, "MatchItemID" = %s WHERE "ItemID" = %s', (new_status, lost_item_id, found_item_id))
        
        msg_for_loser = f"您已通过智能匹配将您的失物“{lost_item_name}”与拾物“{found_item_name}”进行关联。系统已为您开启私信，请尽快沟通确认。"
        msg_for_finder = f"用户通过智能匹配，认为您捡到的物品“{found_item_name}”是他们丢失的“{lost_item_name}”。系统已为你们开启私信，请进入查看详情。"

        create_notification(cursor, lost_user_id, msg_for_loser, 'Match', lost_item_id, found_item_id)
        create_notification(cursor, found_user_id, msg_for_finder, 'Match', lost_item_id, found_item_id)

        conn.commit()
        return jsonify({'success': True, 'message': '匹配成功，已通知双方用户'})
    except Exception as e:
        conn.rollback()
        log_exception('Volunteer link error')
        return jsonify({'success': False, 'message': '操作失败'}), 500
    finally:
        conn.close()

# =========================
# 管理员功能
# =========================
@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    """
    获取所有用户信息。
    """
    conn = get_db_connection()
    if not conn: return jsonify([]), 500
    cursor = conn.cursor()
    sql = 'SELECT "UserID", "Username", "UserRole", "RegistrationDate" FROM "Users"'
    cursor.execute(sql)
    users = rows_to_dicts(cursor)
    conn.close()
    return jsonify(users)

@app.route('/api/admin/items', methods=['GET'])
def get_all_items():
    """
    获取所有物品信息。
    管理员接口，返回系统中所有物品的详细信息。
    """
    conn = get_db_connection()
    if not conn: return jsonify([]), 500
    cursor = conn.cursor()
    sql = 'SELECT "ItemID", "ItemName", "ItemType", "ItemStatus", "UserID", "MatchItemID" FROM "Items" ORDER BY "PostTime" DESC'
    cursor.execute(sql)
    items = rows_to_dicts(cursor)
    conn.close()
    return jsonify(items)
    
@app.route('/api/admin/user/update', methods=['POST'])
def admin_update_user():
    """
    管理员更新用户信息。
    """
    data = request.json
    admin_id = data.get('adminID')
    user_id_to_edit = data.get('userID')
    
    conn = get_db_connection()
    if not conn: return jsonify({'success': False, 'message': '数据库错误'}), 500
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT "UserRole" FROM "Users" WHERE "UserID" = %s', (admin_id,))
        admin = cursor.fetchone()
        if not admin or admin[0] != '管理员':
            return jsonify({'success': False, 'message': '无权限操作'}), 403

        new_username, new_role = data.get('username'), data.get('userRole')
        
        sql = 'UPDATE "Users" SET "Username" = %s, "UserRole" = %s WHERE "UserID" = %s'
        cursor.execute(sql, (new_username, new_role, user_id_to_edit))
        
        msg = f"【管理员通知】您的账户信息已被管理员修改。新用户名: {new_username}, 新角色: {new_role}。"
        create_notification(cursor, user_id_to_edit, msg)

        conn.commit()
        return jsonify({'success': True, 'message': '用户信息更新成功'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {e}'}), 500
    finally:
        conn.close()

# =========================
# 物品详情接口
# =========================

@app.route('/api/item/<string:item_id>', methods=['GET'])
def get_item_detail(item_id):
    """
    获取单个物品的详细信息。
    接收物品ID，返回该物品的所有相关信息。
    """
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'}), 500
    cursor = conn.cursor()
    try:
        sql = """
            SELECT i.*, u."Username" as "posterUsername" 
            FROM "Items" i 
            LEFT JOIN "Users" u ON i."UserID" = u."UserID" 
            WHERE i."ItemID" = %s
        """
        cursor.execute(sql, (item_id,))
        item_dict = row_to_dict(cursor)
        if not item_dict:
            return jsonify({'success': False, 'message': '未找到该物品'}), 404

        return jsonify({'success': True, 'item': item_dict})
    except Exception as e:
        log_exception('Get item detail error')
        return jsonify({'success': False, 'message': '服务器错误'}), 500
    finally:
        conn.close()

# =========================
# 主程序入口
# =========================
if __name__ == '__main__':
    """
    主程序入口，启动 Flask 服务。
    """
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
