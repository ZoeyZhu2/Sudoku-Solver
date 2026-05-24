from flask import Flask, render_template, request, jsonify
import sudoku_solver as solver

app = Flask(__name__)

@app.route("/") #run index when someone is at homepage
def index():
    return render_template("index.html")  # serves your HTML page

@app.route("/solve", methods=["POST"]) #post is js sent to server
def solve():
    data = request.json          # the data sent from JavaScript converted form json to python dictionary
    board = data["board"]        # extracts the board
    solution = solver.solve(board)  # runs your solver!
    return jsonify({"solution": solution})  # sends result back in json form

if __name__ == "__main__":
    app.run(debug=True) #auto restart when I make changes