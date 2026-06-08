from flask import Flask, render_template, request, jsonify
import sudoku_solver as solver

app = Flask(__name__)

@app.route("/") #run index when someone is at homepage
def index():
    return render_template("index.html")  # serves your HTML page

@app.route("/solve", methods=["POST"])
def solve():
    data = request.json
    board = data["board"]
    if not solver.is_solvable(board):
        return jsonify({"error": "Invalid board"}), 400
    result = solver.solve(board)
    if result == "stuck":
        return jsonify({"error": "Could not solve"}), 400
    solution, steps = result

    # compute initial candidates from the input board
    initial_candidates = {}
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                cands = {1,2,3,4,5,6,7,8,9}
                cands -= solver.get_row_candidates(board, i)
                cands -= solver.get_col_candidates(board, j)
                cands -= solver.get_box_candidates(board, i, j)
                initial_candidates[f"{i},{j}"] = sorted(list(cands))

    serialized_steps = []
    for step in steps:
        serialized_steps.append({
            "cells": step[0],
            "value": step[1],
            "strategy": step[2],
            "discarded": step[3]
        })

    return jsonify({
        "solution": solution,
        "steps": serialized_steps,
        "initial_candidates": initial_candidates
    })


if __name__ == "__main__":
    app.run(debug=True) #auto restart when I make changes