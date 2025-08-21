# -*- coding: utf-8 -*-
import os
from datetime import datetime, date
from io import BytesIO
from flask import (
    Flask, render_template, request, redirect, url_for, flash,
    send_file, session
)
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import pandas as pd
from sqlalchemy import or_
from flask import send_file
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet

# -------------------- App & Config --------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

app = Flask(__name__)
app.secret_key = "voc_center_secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "voc.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)

# -------------------- Simple i18n --------------------
LANGS = ["vi", "en", "ko"]
T = {
  "vi": {
    "voc_center": "VOC Center",
    "feedback": "Góp ý",
    "praise": "Khen",
    "menu": "Thực đơn",
    "order": "Đăng ký món",
    "posts": "Bài viết",
    "login": "Đăng nhập",
    "logout": "Đăng xuất",
    "dashboard": "Dashboard",
    "admin": "Quản trị",
    "name": "Họ tên",
    "email": "Email",
    "title": "Tiêu đề",
    "content": "Nội dung",
    "type": "Loại góp ý",
    "rating": "Số sao",
    "image": "Hình ảnh minh họa",
    "submit": "Gửi",
    "success_feedback": "Đã gửi góp ý thành công!",
    "today_menu": "Thực đơn hôm nay",
    "week_menu": "Thực đơn tuần",
    "price_vnd": "đ",
    "employee_code": "Mã nhân viên",
    "choose_food_type": "Chọn loại món",
    "salad": "Salad",
    "vegetarian": "Chay",
    "place": "Địa điểm",
    "public_posts": "Bài viết công khai",
    "filter": "Lọc",
    "from_date": "Từ ngày",
    "to_date": "Đến ngày",
    "export_excel": "Xuất Excel",
    "manage_menu": "Quản lý thực đơn",
    "add": "Thêm",
    "edit": "Sửa",
    "delete": "Xóa",
    "save": "Lưu",
    "orders": "Đơn đăng ký món",
    "users": "Người dùng",
    "locations": "Địa điểm",
    "password": "Mật khẩu"
  },
  "en": {
    "voc_center": "VOC Center",
    "feedback": "Feedback",
    "praise": "Praise",
    "menu": "Menu",
    "order": "Meal registration",
    "posts": "Posts",
    "login": "Login",
    "logout": "Logout",
    "dashboard": "Dashboard",
    "admin": "Admin",
    "name": "Full name",
    "email": "Email",
    "title": "Title",
    "content": "Content",
    "type": "Type",
    "rating": "Rating",
    "image": "Illustration image",
    "submit": "Submit",
    "success_feedback": "Feedback submitted!",
    "today_menu": "Today's menu",
    "week_menu": "Weekly menu",
    "price_vnd": "VND",
    "employee_code": "Employee code",
    "choose_food_type": "Choose type",
    "salad": "Salad",
    "vegetarian": "Vegetarian",
    "place": "Location",
    "public_posts": "Public posts",
    "filter": "Filter",
    "from_date": "From",
    "to_date": "To",
    "export_excel": "Export Excel",
    "manage_menu": "Manage menu",
    "add": "Add",
    "edit": "Edit",
    "delete": "Delete",
    "save": "Save",
    "orders": "Orders",
    "users": "Users",
    "locations": "Locations",
    "password": "Password"
  },
  "ko": {
    "voc_center": "VOC 센터",
    "feedback": "의견",
    "praise": "칭찬",
    "menu": "메뉴",
    "order": "식사 등록",
    "posts": "게시글",
    "login": "로그인",
    "logout": "로그아웃",
    "dashboard": "대시보드",
    "admin": "관리",
    "name": "이름",
    "email": "이메일",
    "title": "제목",
    "content": "내용",
    "type": "유형",
    "rating": "별점",
    "image": "이미지",
    "submit": "보내기",
    "success_feedback": "전송되었습니다!",
    "today_menu": "오늘의 메뉴",
    "week_menu": "주간 메뉴",
    "price_vnd": "VND",
    "employee_code": "사번",
    "choose_food_type": "종류 선택",
    "salad": "샐러드",
    "vegetarian": "채식",
    "place": "지점",
    "public_posts": "공개 게시글",
    "filter": "필터",
    "from_date": "시작",
    "to_date": "끝",
    "export_excel": "엑셀 내보내기",
    "manage_menu": "메뉴 관리",
    "add": "추가",
    "edit": "수정",
    "delete": "삭제",
    "save": "저장",
    "orders": "주문",
    "users": "사용자",
    "locations": "지점",
    "password": "비밀번호"
  }
}

def tr(key):
    lang = session.get("lang", "vi")
    return T.get(lang, T["vi"]).get(key, key)

app.jinja_env.globals["tr"] = tr

@app.route("/lang/<code>")
def set_lang(code):
    if code in LANGS:
        session["lang"] = code
    return redirect(request.referrer or url_for("index"))

# -------------------- Models --------------------
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    role = db.Column(db.String(20), default="user")  # admin/user/kitchen
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"))
    location = db.relationship("Location")

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    fb_type = db.Column(db.String(50))  # voc/khen/complaint
    rating = db.Column(db.Integer, default=5)
    image_path = db.Column(db.String(255))
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"))
    location = db.relationship("Location")
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# class MenuItem(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(120))
#     description = db.Column(db.Text)
#     price = db.Column(db.Integer)
#     image_path = db.Column(db.String(255))
#     location_id = db.Column(db.Integer, db.ForeignKey("location.id"))
#     location = db.relationship("Location")
#     is_salad = db.Column(db.Boolean, default=False)
#     is_vegetarian = db.Column(db.Boolean, default=False)
#     weekday = db.Column(db.Integer, default=0)  # 0=Mon ... 6=Sun

# -------------------- Models: WeeklyMenu & SpecialMenu --------------------
# -------------------- Models: WeeklyMenu & SpecialMenu --------------------
class WeeklyMenu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class SpecialMenu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text)
    price = db.Column(db.Integer)
    image_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120))
    employee_code = db.Column(db.String(50))
    item_id = db.Column(db.Integer, db.ForeignKey("special_menu.id"))
    item = db.relationship("SpecialMenu")
    quantity = db.Column(db.Integer, default=1)
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"))
    location = db.relationship("Location")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# -------------------- Helpers --------------------
def current_user():
    uid = session.get("uid")
    if uid:
        return User.query.get(uid)
    return None

def require_admin():
    u = current_user()
    return (u and u.role == "admin")

app.jinja_env.globals["current_user"] = current_user

def save_upload(file):
    if not file or file.filename == "":
        return None
    fname = datetime.utcnow().strftime("%Y%m%d%H%M%S_") + secure_filename(file.filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], fname)
    file.save(path)
    return "uploads/" + fname

# -------------------- Routes: Public --------------------
@app.route("/")
def index():
    return render_template("index.html", active="home")

@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        image_rel = save_upload(request.files.get("image"))
        fb = Feedback(
            name=request.form.get("name"),
            email=request.form.get("email"),
            title=request.form.get("title"),
            message=request.form.get("message"),
            fb_type=request.form.get("fb_type","voc"),
            rating=int(request.form.get("rating", 5)),
            image_path=image_rel,
            location_id=int(request.form.get("location_id")) if request.form.get("location_id") else None,
            is_public=True
        )
        db.session.add(fb)
        db.session.commit()
        flash(tr("success_feedback"))
        return redirect(url_for("feedback"))
    locations = Location.query.all()
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).limit(20).all()
    return render_template("feedback.html", active="feedback", locations=locations, feedbacks=feedbacks)

@app.route("/praise", methods=["GET","POST"])
def praise():
    # use same form but fb_type=khen
    if request.method == "POST":
        fb = Feedback(
            name=request.form.get("name"),
            email=request.form.get("email"),
            title=request.form.get("title"),
            message=request.form.get("message"),
            fb_type="khen",
            rating=5,
            location_id=int(request.form.get("location_id")) if request.form.get("location_id") else None,
            is_public=True
        )
        db.session.add(fb)
        db.session.commit()
        flash(tr("success_feedback"))
        return redirect(url_for("praise"))
    locations = Location.query.all()
    praises = Feedback.query.filter_by(fb_type="khen").order_by(Feedback.created_at.desc()).limit(20).all()
    return render_template("praise.html", active="praise", locations=locations, feedbacks=praises)

# @app.route("/menu")
# def menu():
#     loc_id = request.args.get("loc", type=int)
#     weekday = datetime.today().weekday()  # 0 Mon
#     q = MenuItem.query
#     if loc_id:
#         q = q.filter_by(location_id=loc_id)
#     today_items = q.filter_by(weekday=weekday).all()
#     week_items = q.order_by(MenuItem.weekday).all()
#     locations = Location.query.all()
#     return render_template("menu.html", active="menu",
#                            today_items=today_items, week_items=week_items,
#                            weekday=weekday, locations=locations, loc_id=loc_id)


# -------------------- Public Menu --------------------
# @app.route("/menu")
# def menu():
#     weekly = WeeklyMenu.query.first()
#     specials = SpecialMenu.query.order_by(SpecialMenu.id.desc()).all()
#     return render_template("menu.html", active="menu", weekly=weekly, specials=specials)
@app.route("/menu")
def menu():
    view = request.args.get("view", "weekly")  # weekly / special

    weekly = WeeklyMenu.query.first()
    specials = SpecialMenu.query.order_by(SpecialMenu.id.desc()).all()

    return render_template("menu.html", 
                           active="menu", 
                           weekly=weekly, 
                           specials=specials, 
                           view=view)


# -------------------- Order --------------------
@app.route("/order", methods=["GET","POST"])
def order():
    if request.method == "POST":
        order_date = request.form.get("order_date")
        o = Order(
            customer_name=request.form.get("name"),
            employee_code=request.form.get("employee_code"),
            item_id=int(request.form.get("item_id")),
            location_id=int(request.form.get("location_id")),
            created_at=datetime.fromisoformat(order_date) if order_date else datetime.utcnow()
        )
        db.session.add(o)
        db.session.commit()
        flash("Đăng ký thành công!")
        return redirect(url_for("order"))

    items = SpecialMenu.query.all()
    locations = Location.query.all()
    return render_template(
        "order.html",
        active="order",
        items=items,
        locations=locations,
        today=date.today().isoformat()
    )

# -------------------- Admin: Weekly Menu --------------------
@app.route("/admin/menu_weekly", methods=["GET", "POST"])
def admin_menu_weekly():
    if not require_admin():
        return redirect(url_for("login"))

    weekly = WeeklyMenu.query.first()

    if request.method == "POST":
        file = request.files.get("image")
        if file:
            img_path = save_upload(file)
            if weekly:
                # xóa ảnh cũ nếu có
                if weekly.image_path:
                    try:
                        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], os.path.basename(weekly.image_path)))
                    except:
                        pass
                weekly.image_path = img_path
            else:
                weekly = WeeklyMenu(image_path=img_path)
                db.session.add(weekly)
            db.session.commit()
            flash("Đã cập nhật thực đơn tuần", "success")
        return redirect(url_for("admin_menu_weekly"))

    return render_template("admin/menu_weekly.html", weekly=weekly)


# -------------------- Admin: Special Menu --------------------
# ----- Admin Special Menu -----
@app.route("/admin/menu_special", methods=["GET","POST"])
def admin_menu_special():
    if not require_admin():
        return redirect(url_for("login"))

    if request.method == "POST":
        img = save_upload(request.files.get("image"))
        new_item = SpecialMenu(
            name=request.form.get("name"),
            description=request.form.get("description"),
            price=int(request.form.get("price") or 0),
            image_path=img
        )
        db.session.add(new_item)
        db.session.commit()
        flash("Đã thêm món đặc biệt!", "success")
        return redirect(url_for("admin_menu_special"))

    # 👇 Đây là phần quan trọng: query danh sách để hiển thị
    items = SpecialMenu.query.order_by(SpecialMenu.id.desc()).all()
    return render_template("admin/menu_special.html", items=items)

# ----- EDIT SpecialMenu -----
@app.route("/admin/menu_special_edit/<int:id>", methods=["GET", "POST"])
def admin_menu_special_edit(id):
    if not require_admin():
        return redirect(url_for("login"))

    item = SpecialMenu.query.get_or_404(id)

    if request.method == "POST":
        item.name = request.form.get("name")
        item.description = request.form.get("description")
        item.price = int(request.form.get("price", 0))

        # Nếu có upload ảnh mới thì thay ảnh cũ
        img = request.files.get("image")
        if img and img.filename:
            item.image_path = save_upload(img)

        db.session.commit()
        flash("Đã cập nhật món đặc biệt")
        return redirect(url_for("admin_menu_special"))

    return render_template("admin/menu_special_edit.html", item=item)


# ----- DELETE SpecialMenu -----
@app.route("/admin/menu_special_delete/<int:id>", methods=["POST"])
def admin_menu_special_delete(id):
    if not require_admin():
        return redirect(url_for("login"))

    item = SpecialMenu.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash("Đã xóa món đặc biệt")
    return redirect(url_for("admin_menu_special"))


# @app.route("/admin/menu_special/<int:id>/delete")
# def admin_menu_special_delete(id):
#     if not require_admin():
#         return redirect(url_for("login"))

#     item = SpecialMenu.query.get_or_404(id)
#     if item.image_path:
#         try:
#             os.remove(os.path.join(app.config["UPLOAD_FOLDER"], os.path.basename(item.image_path)))
#         except:
#             pass
#     db.session.delete(item)
#     db.session.commit()
#     flash("Đã xóa món đặc biệt", "success")
#     return redirect(url_for("admin_menu_special"))

# @app.route("/order", methods=["GET","POST"])
# def order():
#     loc_id = request.args.get("loc", type=int)
#     q = MenuItem.query
#     if loc_id:
#         q = q.filter_by(location_id=loc_id)
#     items = q.all()
#     if request.method == "POST":
#         o = Order(
#             customer_name=request.form.get("name"),
#             employee_code=request.form.get("employee_code"),
#             item_id=int(request.form.get("item_id")) if request.form.get("item_id") else None,
#             quantity=int(request.form.get("quantity",1)),
#             is_salad_choice=(request.form.get("food_type")=="salad"),
#             is_vegetarian_choice=(request.form.get("food_type")=="vegetarian"),
#             location_id=int(request.form.get("location_id")) if request.form.get("location_id") else None
#         )
#         db.session.add(o)
#         db.session.commit()
#         flash("Đăng ký thành công!")
#         return redirect(url_for("order"))
#     locations = Location.query.all()
#     return render_template("order.html", active="order", items=items, locations=locations, loc_id=loc_id)

# @app.route("/posts")
# def posts():
#     page = int(request.args.get("page", 1))
#     per_page = 10
#     q = Feedback.query.order_by(Feedback.created_at.desc())
#     total = q.count()
#     posts = q.offset((page-1)*per_page).limit(per_page).all()
#     return render_template("posts.html", posts=posts, page=page, per_page=per_page, total=total)
# app.py (đảm bảo đã import request)
from flask import request, render_template

@app.route("/posts")
def posts():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    posts = Feedback.query.filter_by(is_public=True).order_by(Feedback.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    return render_template("posts.html", posts=posts)

# -------------------- Auth --------------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        u = User.query.filter_by(email=email, password=password).first()
        if u:
            session["uid"] = u.id
            flash("Xin chào " + u.name)
            return redirect(url_for("index"))
        flash("Sai thông tin đăng nhập")
    return render_template("login.html", active="login")

@app.route("/logout")
def logout():
    session.pop("uid", None)
    return redirect(url_for("index"))

# -------------------- Admin --------------------
@app.route("/admin")
def admin_home():
    if not require_admin():
        return redirect(url_for("login"))
    count_voc = Feedback.query.filter_by(fb_type="voc").count()
    count_praise = Feedback.query.filter_by(fb_type="khen").count()
    count_orders = Order.query.count()
    return render_template("admin/index.html", active="admin",
                           count_voc=count_voc, count_praise=count_praise,
                           count_orders=count_orders)

# Locations CRUD
@app.route("/admin/locations", methods=["GET","POST"])
def admin_locations():
    if not require_admin():
        return redirect(url_for("login"))
    if request.method == "POST":
        name = request.form.get("name")
        if name:
            db.session.add(Location(name=name))
            db.session.commit()
            flash("Đã thêm địa điểm")
            return redirect(url_for("admin_locations"))
    locs = Location.query.all()
    return render_template("admin/locations.html", locations=locs)

@app.route("/admin/locations/<int:id>/delete")
def admin_locations_delete(id):
    if not require_admin():
        return redirect(url_for("login"))
    Location.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for("admin_locations"))

# Users CRUD (minimal)
@app.route("/admin/users", methods=["GET","POST"])
def admin_users():
    if not require_admin():
        return redirect(url_for("login"))
    if request.method == "POST":
        db.session.add(User(
            name=request.form.get("name"),
            email=request.form.get("email"),
            password=request.form.get("password"),
            role=request.form.get("role","user"),
            location_id=request.form.get("location_id")
        ))
        db.session.commit()
        return redirect(url_for("admin_users"))
    users = User.query.all()
    locs = Location.query.all()
    return render_template("admin/users.html", users=users, locations=locs)

@app.route("/admin/users/<int:id>/delete")
def admin_users_delete(id):
    if not require_admin():
        return redirect(url_for("login"))
    User.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for("admin_users"))

# # Menu Manage
# @app.route("/admin/menu", methods=["GET","POST"])
# def admin_menu():
#     if not require_admin():
#         return redirect(url_for("login"))
#     if request.method == "POST":
#         img = save_upload(request.files.get("image"))
#         db.session.add(MenuItem(
#             name=request.form.get("name"),
#             description=request.form.get("description"),
#             price=int(request.form.get("price",0)),
#             image_path=img,
#             location_id=request.form.get("location_id"),
#             is_salad=("is_salad" in request.form),
#             is_vegetarian=("is_vegetarian" in request.form),
#             weekday=int(request.form.get("weekday",0))
#         ))
#         db.session.commit()
#         return redirect(url_for("admin_menu"))
#     items = MenuItem.query.order_by(MenuItem.weekday).all()
#     locs = Location.query.all()
#     return render_template("admin/menu.html", items=items, locations=locs)

# @app.route("/admin/menu/<int:id>/delete")
# def admin_menu_delete(id):
#     if not require_admin():
#         return redirect(url_for("login"))
#     MenuItem.query.filter_by(id=id).delete()
#     db.session.commit()
#     return redirect(url_for("admin_menu"))

# Feedback management + filters + export
# @app.route("/admin/feedback", methods=["GET"])
# def admin_feedback():
#     if not require_admin():
#         return redirect(url_for("login"))
#     fb_type = request.args.get("type")
#     start = request.args.get("start")
#     end = request.args.get("end")
#     rating = request.args.get("rating", type=int)
#     q = Feedback.query
#     if fb_type:
#         q = q.filter_by(fb_type=fb_type)
#     if rating:
#         q = q.filter(Feedback.rating>=rating)
#     if start:
#         q = q.filter(Feedback.created_at>=datetime.fromisoformat(start))
#     if end:
#         q = q.filter(Feedback.created_at<=datetime.fromisoformat(end)+" 23:59:59")
#     rows = q.order_by(Feedback.created_at.desc()).all()
#     return render_template("admin/feedback.html", rows=rows)
# ====== HÀM CHUNG: Build query có filter ======
def build_feedback_query():
    ftype   = request.args.get("type", "").strip()
    kw      = request.args.get("kw", "").strip()
    start_s = request.args.get("start", "").strip()
    end_s   = request.args.get("end", "").strip()

    q = Feedback.query

    if ftype:
        q = q.filter(Feedback.fb_type == ftype)

    if kw:
        like = f"%{kw}%"
        q = q.filter(or_(
            Feedback.name.ilike(like),
            Feedback.title.ilike(like),
            Feedback.message.ilike(like)
        ))

    if start_s:
        try:
            start_dt = datetime.fromisoformat(start_s)
            q = q.filter(Feedback.created_at >= start_dt)
        except ValueError:
            pass
    if end_s:
        try:
            end_dt = datetime.fromisoformat(end_s) + timedelta(days=1) - timedelta(seconds=1)
            q = q.filter(Feedback.created_at <= end_dt)
        except ValueError:
            pass

    return q.order_by(Feedback.created_at.desc())


# ====== Admin Feedback list ======
@app.route("/admin/feedback")
def admin_feedback():
    if not require_admin():
        return redirect(url_for("login"))

    per_page = request.args.get("per_page", 20, type=int)
    page     = request.args.get("page", 1, type=int)

    q = build_feedback_query()
    rows = q.paginate(page=page, per_page=per_page, error_out=False)

    return render_template("admin/feedback.html", rows=rows)


# ====== Export Excel / PDF ======
@app.route("/admin/feedback/export")
def admin_feedback_export():
    if not require_admin():
        return redirect(url_for("login"))

    fmt = request.args.get("format", "excel")
    q = build_feedback_query()
    rows = q.all()

    data = [{
        "ID": r.id,
        "Người gửi": r.name,
        "Email": r.email,
        "Tiêu đề": r.title,
        "Nội dung": r.message,
        "Loại": r.fb_type,
        "Điểm": r.rating,
        "Địa điểm": (r.location.name if r.location else ""),
        "Công khai": ("Có" if r.is_public else "Ẩn"),
        "Thời gian": r.created_at.strftime("%Y-%m-%d %H:%M")
    } for r in rows]

    if not data:
        flash("Không có dữ liệu để xuất", "warning")
        return redirect(url_for("admin_feedback"))

    if fmt == "pdf":
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        table_data = [list(data[0].keys())] + [list(d.values()) for d in data]
        table = Table(table_data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.grey),
            ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
            ("ALIGN", (0,0), (-1,-1), "LEFT"),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0,0), (-1,0), 12),
            ("GRID", (0,0), (-1,-1), 0.25, colors.black),
        ]))
        doc.build([table])
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="feedback.pdf")

    # default excel
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="feedback")
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="feedback.xlsx")


# ====== Toggle Ẩn/Hiện ======
@app.post("/admin/feedback/<int:id>/toggle")
def admin_feedback_toggle(id):
    if not require_admin():
        return redirect(url_for("login"))
    fb = Feedback.query.get_or_404(id)
    fb.is_public = not fb.is_public
    db.session.commit()
    flash("Đã thay đổi trạng thái công khai.", "success")
    return redirect(url_for("admin_feedback", **request.args))


# ====== Xoá Feedback ======
@app.post("/admin/feedback/<int:id>/delete")
def admin_feedback_delete(id):
    if not require_admin():
        return redirect(url_for("login"))
    fb = Feedback.query.get_or_404(id)
    db.session.delete(fb)
    db.session.commit()
    flash("Đã xóa phản hồi.", "success")
    return redirect(url_for("admin_feedback", **request.args))

# Orders management
from sqlalchemy import func
@app.route("/admin/orders")
def admin_orders():
    if not require_admin():
        return redirect(url_for("login"))

    kw = request.args.get("kw", "").strip()
    loc_id = request.args.get("location_id", type=int)
    order_date = request.args.get("date")
    item_id = request.args.get("item_id", type=int)
    per_page = request.args.get("per_page", 20, type=int)
    page = request.args.get("page", 1, type=int)

    q = Order.query

    # lọc từ khoá
    if kw:
        like = f"%{kw}%"
        q = q.filter(or_(
            Order.customer_name.ilike(like),
            Order.employee_code.ilike(like)
        ))

    # lọc theo món ăn
    if item_id:
        q = q.filter(Order.item_id == item_id)

    # lọc ngày (mặc định = hôm nay)
    if order_date:
        try:
            dt = datetime.fromisoformat(order_date).date()
        except:
            dt = date.today()
    else:
        dt = date.today()
    q = q.filter(func.date(Order.created_at) == dt)

    rows = q.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    # tổng món đặc biệt theo ngày
    totals = db.session.query(
        Order.item_id,
        func.sum(Order.quantity)
    ).filter(func.date(Order.created_at) == dt).group_by(Order.item_id).all()

    totals_map = {}
    for iid, qty in totals:
        item = SpecialMenu.query.get(iid)
        if item:
            totals_map[item.name] = qty

    locations = Location.query.all()
    items = SpecialMenu.query.all()

    return render_template("admin/orders.html",
                           rows=rows, kw=kw,
                           date=dt.isoformat(),
                           items=items, item_id=item_id,
                           # loc_id=loc_id, locations=locations
                           totals_map=totals_map)

from sqlalchemy import func

@app.route("/admin/orders/export")
def admin_orders_export():
    if not require_admin():
        return redirect(url_for("login"))

    kw = request.args.get("kw", "").strip()
    item_id = request.args.get("item_id", type=int)
    order_date = request.args.get("date")

    q = Order.query

    if kw:
        like = f"%{kw}%"
        q = q.filter(or_(
            Order.customer_name.ilike(like),
            Order.employee_code.ilike(like)
        ))

    if item_id:
        q = q.filter(Order.item_id == item_id)

    if order_date:
        try:
            dt = datetime.fromisoformat(order_date).date()
        except:
            dt = date.today()
    else:
        dt = date.today()
    q = q.filter(func.date(Order.created_at) == dt)

    rows = q.order_by(Order.created_at.desc()).all()

    # Chuẩn bị data
    data = [{
        "ID": r.id,
        "Họ tên": r.customer_name,
        "Mã NV": r.employee_code,
        "Món": (r.item.name if r.item else ""),
        "Ngày đăng ký": r.created_at.date().isoformat(),
        "Số lượng": r.quantity,
    } for r in rows]

    if not data:
        flash("Không có dữ liệu để xuất", "warning")
        return redirect(url_for("admin_orders"))

    df = pd.DataFrame(data)

    # Tính tổng suất
    total_qty = df["Số lượng"].sum()
    total_row = pd.DataFrame([{
        "ID": "",
        "Họ tên": "",
        "Mã NV": "",
        "Món": "TỔNG CỘNG",
        "Ngày đăng ký": "",
        "Số lượng": total_qty,
    }])
    df = pd.concat([df, total_row], ignore_index=True)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="orders")
    output.seek(0)

    filename = f"Order_{dt.strftime('%d%m%Y')}.xlsx"
    return send_file(output, as_attachment=True, download_name=filename)

# -------------------- Init sample data --------------------
def seed():
    if Location.query.count() == 0:
        l1 = Location(name="Hà Nội")
        l2 = Location(name="HCM")
        db.session.add_all([l1, l2])
        db.session.commit()

    if User.query.count() == 0:
        db.session.add(User(
            name="Admin",
            email="admin@voc",
            password="admin",
            role="admin",
            location_id=1
        ))

    if WeeklyMenu.query.count() == 0:
        db.session.add(WeeklyMenu(image_path=None))

    # if SpecialMenu.query.count() == 0:
    #     db.session.add_all([
    #         SpecialMenu(name="Cơm gà", description="Cơm gà xối mỡ", price=35000),
    #         SpecialMenu(name="Bún chả", description="Bún chả Hà Nội", price=40000),
    #         SpecialMenu(name="Salad cá ngừ", description="Salad healthy", price=30000),
    #     ])

    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed()
    app.run(debug=True)
