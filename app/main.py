# app/main.py

from flask import Flask, render_template
from app.routers.testing_router import testing_bp    
from app.routers.classify_router import classify_bp  

app = Flask(__name__)

# Register existing blueprint
app.register_blueprint(testing_bp)

# Register the new image‐processing blueprint
app.register_blueprint(classify_bp)

@app.route("/")
def index():
    return render_template("index.html") 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
