# app/main.py

from flask import Flask, render_template, session, redirect, url_for
from flask_session import Session
from app.routers.testing_router import testing_bp
from app.routers.classify_router import classify_bp
from app.routers.chatgpt_router import chatgpt_bp

app = Flask(__name__)
app.secret_key = "verysecretkey"

# ── Server-side session setup ────────────────────────────────────────────────
app.config["SESSION_TYPE"] = "filesystem"            # store sessions in local files
app.config["SESSION_FILE_DIR"] = ".flask_session"    # directory for session files
app.config["SESSION_PERMANENT"] = False              # expires on browser close
app.config["SESSION_USE_SIGNER"] = True              # cryptographically sign session IDs

Session(app)  # initialize

# ── Register blueprints ─────────────────────────────────────────────────────
app.register_blueprint(testing_bp)
app.register_blueprint(classify_bp)
app.register_blueprint(chatgpt_bp)

# ── Ensure per-user chat history exists ──────────────────────────────────────
@app.before_request
def ensure_history():
    if "history" not in session:
        session["history"] = []

# ── Routes ───────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatgpt")
def chatgpt():
    return render_template("chatgpt.html")

@app.route("/clear")
def clear_session():
    session.clear()
    return redirect(url_for("index"))

# ── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
