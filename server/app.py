from flask import Flask, request
app = Flask(__name__)

@app.route("/", methods=["POST"])
def add_files():
    data = request.get_json()
    print(data)
    return "received"

@app.route("/", methods=["DELETE"])
def remove_files():
    pass

@app.route("/", methods=["PUT"])
def update_files():
    pass

if __name__ == "__main__":
    app.run(debug=True)