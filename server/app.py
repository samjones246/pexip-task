from flask import Flask, request
app = Flask(__name__)

@app.route("/", methods=["POST"])
def main():
    data = request.get_json()
    print(data)
    return "received"

if __name__ == "__main__":
    app.run(debug=True)