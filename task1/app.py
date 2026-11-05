from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB = "students.db"


def query(sql, params=(), fetch=None, commit=False):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(sql, params)
        if commit:
            conn.commit()
        if fetch == "all":
            return [dict(r) for r in cur.fetchall()]
        if fetch == "one":
            row = cur.fetchone()
            return dict(row) if row else None
        return cur
    finally:
        conn.close()


def init_db():
    query("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    """, commit=True)


def valid(data):
    return data and all(data.get(k) for k in ("name", "department", "email"))


@app.route("/students", methods=["GET"])
def get_students():
    return jsonify(query("SELECT * FROM students", fetch="all")), 200


@app.route("/students/<int:sid>", methods=["GET"])
def get_student(sid):
    student = query("SELECT * FROM students WHERE id = ?", (sid,), fetch="one")
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(student), 200


@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True)
    if not valid(data):
        return jsonify({"error": "name, department and email are required"}), 400
    try:
        cur = query(
            "INSERT INTO students (name, department, email) VALUES (?, ?, ?)",
            (data["name"], data["department"], data["email"]), commit=True)
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    return jsonify({"message": "Student added", "id": cur.lastrowid}), 201


@app.route("/students/<int:sid>", methods=["PUT"])
def update_student(sid):
    data = request.get_json(silent=True)
    if not valid(data):
        return jsonify({"error": "name, department and email are required"}), 400
    if not query("SELECT id FROM students WHERE id = ?", (sid,), fetch="one"):
        return jsonify({"error": "Student not found"}), 404
    try:
        query("UPDATE students SET name=?, department=?, email=? WHERE id=?",
              (data["name"], data["department"], data["email"], sid), commit=True)
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    return jsonify({"message": "Student updated"}), 200


@app.route("/students/<int:sid>", methods=["DELETE"])
def delete_student(sid):
    if not query("SELECT id FROM students WHERE id = ?", (sid,), fetch="one"):
        return jsonify({"error": "Student not found"}), 404
    query("DELETE FROM students WHERE id = ?", (sid,), commit=True)
    return jsonify({"message": "Student deleted"}), 200


if __name__ == "__main__":
    init_db()
    app.run(debug=True)