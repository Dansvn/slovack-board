import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime
import pytz

app = Flask(__name__)
app.secret_key = "secret"

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "webm"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

DB = "posts.db"
TARGET_WIDTH = 1280
TARGET_HEIGHT = 720

ADMINS = {
    "admin1": "admin1",
    "admin1": "admin2"
}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            media TEXT,
            likes INTEGER DEFAULT 0,
            created_at TEXT,
            author TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            content TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def process_image(filepath):
    with Image.open(filepath) as img:
        img.thumbnail((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)
        background = Image.new('RGB', (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0))
        offset_x = (TARGET_WIDTH - img.width) // 2
        offset_y = (TARGET_HEIGHT - img.height) // 2
        background.paste(img, (offset_x, offset_y))
        background.save(filepath)

init_db()

@app.route("/", methods=["GET"])
def index():
    search = request.args.get("search", "").strip()
    conn = get_db_connection()
    if search:
        query = f"%{search}%"
        posts = conn.execute(
            "SELECT * FROM posts WHERE title LIKE ? OR content LIKE ? ORDER BY id DESC",
            (query, query)
        ).fetchall()
    else:
        posts = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("index.html", posts=posts, search=search)

@app.route("/load_more_posts", methods=["GET"])
def load_more_posts():
    offset = int(request.args.get("offset", 0))
    limit = 6
    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM posts ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset)).fetchall()
    conn.close()

    result = []
    for post in posts:
        media = post["media"].split(",")[0] if post["media"] else None
        result.append({
            "id": post["id"],
            "title": post["title"],
            "content": post["content"],
            "media": media
        })

    return jsonify(result)

@app.route("/post/<int:post_id>")
def view_post(post_id):
    conn = get_db_connection()
    post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    comments = conn.execute("SELECT * FROM comments WHERE post_id = ? ORDER BY id DESC", (post_id,)).fetchall()
    more_posts = conn.execute("SELECT * FROM posts WHERE id != ? ORDER BY id DESC LIMIT 6", (post_id,)).fetchall()
    conn.close()
    if not post:
        return "Post not found", 404
    created_at = post["created_at"]
    if created_at:
        try:
            utc_time = datetime.fromisoformat(created_at)
            brt = pytz.timezone("America/Sao_Paulo")
            local_time = utc_time.astimezone(brt)
            post_time_str = local_time.strftime("%d/%m/%Y %H:%M:%S")
        except Exception:
            post_time_str = "Data inválida"
    else:
        post_time_str = "Data não disponível"
    return render_template("post.html", post=post, more_posts=more_posts, comments=comments, post_time=post_time_str)

@app.route("/post/<int:post_id>/like", methods=["POST"])
def toggle_like(post_id):
    data = request.get_json()
    action = data.get("action") if data else None
    if action not in {"like", "unlike"}:
        return jsonify({"error": "Invalid action"}), 400
    conn = get_db_connection()
    if action == "like":
        conn.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))
    elif action == "unlike":
        conn.execute("UPDATE posts SET likes = CASE WHEN likes > 0 THEN likes - 1 ELSE 0 END WHERE id = ?", (post_id,))
    conn.commit()
    likes = conn.execute("SELECT likes FROM posts WHERE id = ?", (post_id,)).fetchone()["likes"]
    conn.close()
    return jsonify({"likes": likes})

@app.route("/post/<int:post_id>/comment", methods=["POST"])
def comment_post(post_id):
    comment = request.form.get("comment", "").strip()
    if comment:
        conn = get_db_connection()
        conn.execute("INSERT INTO comments (post_id, content) VALUES (?, ?)", (post_id, comment))
        conn.commit()
        conn.close()
    return redirect(url_for("view_post", post_id=post_id))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in ADMINS and ADMINS[username] == password:
            session["admin"] = username
            return redirect(url_for("admin"))
        else:
            flash("Usuário ou senha incorretos")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin():
    conn = get_db_connection()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        media_filenames = []
        if "media[]" in request.files:
            for file in request.files.getlist("media[]"):
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                    file.save(filepath)
                    if filename.rsplit('.', 1)[1].lower() in {"png", "jpg", "jpeg", "gif"}:
                        process_image(filepath)
                    media_filenames.append(filename)
        if title and content:
            utc_now = datetime.utcnow().replace(microsecond=0).isoformat()
            media = ",".join(media_filenames) if media_filenames else None
            author = session.get("admin", "unknown")
            conn.execute(
                "INSERT INTO posts (title, content, media, created_at, author) VALUES (?, ?, ?, ?, ?)",
                (title, content, media, utc_now, author)
            )
            conn.commit()
            flash("Post adicionado.")
        else:
            flash("Título e conteúdo são obrigatórios.")
        conn.close()
        return redirect(url_for("admin"))
    posts = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("admin.html", posts=posts, admin=session.get("admin"))

@app.route("/edit/<int:post_id>", methods=["POST"])
@admin_required
def edit(post_id):
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    conn = get_db_connection()
    conn.execute("UPDATE posts SET title = ?, content = ? WHERE id = ?", (title, content, post_id))
    conn.commit()
    conn.close()
    flash("Post atualizado.")
    return redirect(url_for("admin"))

@app.route("/delete/<int:post_id>", methods=["POST"])
@admin_required
def delete(post_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    flash("Post deletado.")
    return redirect(url_for("admin"))

@app.route("/index.html")
def index_html():
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
