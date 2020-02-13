import os

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from datetime import datetime, timedelta

from helpers import apology

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_FILE_THRESHOLD'] = float("inf")

Session(app)

# Global variables
gameboard = {}
for i in range(256):
    gameboard['b' + str(i)] = 0

p1_id_in_use = False
p2_id_in_use = False

last_move = 0
turn_index = 1

p1_winc = 0
p2_winc = 0
p1_winlist = []
p2_winlist = []

total_marks = 0

p1_stalemate = False
p2_stalemate = False

p1_requests_newgame = False
p2_requests_newgame = False

p1_requests_reset = False
p2_requests_reset = False

p1_time_out = 0
p2_time_out = 0

p1_dc = False
p2_dc = False


@app.route("/update", methods=["GET"])
def update():
    """Handle game logic"""

    # Access global variables
    global gameboard

    global p1_winc
    global p2_winc
    global p1_winlist
    global p2_winlist

    global total_marks

    global p1_stalemate
    global p2_stalemate

    global last_move
    global turn_index

    global p1_requests_newgame
    global p2_requests_newgame

    global p1_requests_reset
    global p2_requests_reset

    global p1_time_out
    global p2_time_out

    global p1_dc
    global p2_dc

    global p1_id_in_use
    global p2_id_in_use

    # Handle disconnects
    try:
        if session["user_id"] == 1 and p2_id_in_use:
            if not p1_time_out:
                p1_time_out = datetime.now()
            else:
                if p2_time_out and datetime.now() - p2_time_out > timedelta(seconds=5):
                    p2_dc = True
                else:
                    p1_time_out = datetime.now()

        if session["user_id"] == 2 and p1_id_in_use:
            if not p2_time_out:
                p2_time_out = datetime.now()
            else:
                if p1_time_out and datetime.now() - p1_time_out > timedelta(seconds=5):
                    p1_dc = True
                else:
                    p2_time_out = datetime.now()
    except:
        pass

    # Handle stalemate
    if total_marks == 256:

        # Reset the gameboard
        for i in range(256):
            gameboard['b' + str(i)] = 0

        # Reset the global variables
        last_move = 0

        # In case of stalemate, swap the first move right
        if turn_index == 1:
            turn_index = 2
        else:
            turn_index = 1

        p1_winc = 0
        p2_winc = 0
        p1_winlist.clear()
        p2_winlist.clear()

        if p1_dc:
            p1_id_in_use = False

        if p2_dc:
            p2_id_in_use = False

        p1_dc = False
        p2_dc = False

        p1_requests_reset = True
        p2_requests_reset = True

        p1_stalemate = True
        p2_stalemate = True

        return jsonify(True)

    # Handle disconnects via adding a forced reset method
    force_reset = request.args.get("force_reset")

    if force_reset:
        if p1_dc or p2_dc:

            # Reset the gameboard
            for i in range(256):
                gameboard['b' + str(i)] = 0

            # Reset the global variables
            last_move = 0

            # Give loser the first move
            if p1_winc == 5:
                turn_index = 2

            if p2_winc == 5:
                turn_index = 1

            p1_winc = 0
            p2_winc = 0
            p1_winlist.clear()
            p2_winlist.clear()

            if p1_dc:
                p1_id_in_use = False

            if p2_dc:
                p2_id_in_use = False

            p1_dc = False
            p2_dc = False

            return jsonify(True)

    # Method for starting a new game in case both players wish to do so
    reset_needed = request.args.get("reset")

    if reset_needed == "1":
        p1_requests_newgame = True

    if reset_needed == "2":
        p2_requests_newgame = True

    if reset_needed:
        if p1_winc == 5 or p2_winc == 5:
            if p1_requests_newgame and p2_requests_newgame:

                # Reset the gameboard
                for i in range(256):
                    gameboard['b' + str(i)] = 0

                # Reset the global variables
                last_move = 0

                # Give loser the first move
                if p1_winc == 5:
                    turn_index = 2

                if p2_winc == 5:
                    turn_index = 1

                p1_winc = 0
                p2_winc = 0
                p1_winlist.clear()
                p2_winlist.clear()

                p1_requests_reset = True
                p2_requests_reset = True

                return jsonify(True)

            else:
                return jsonify(False)

    # Handle refresh logic in an unreadable and unmaintainable fashion
    refresh_needed = request.args.get("refresh")
    if refresh_needed:
        if p1_winc == 5:
            if p1_requests_newgame:
                return jsonify({'p1_dc': p1_dc, 'p2_dc': p2_dc, 'last_move': last_move, 'winner': 'P1', 'winlist': p1_winlist, 'turn_index': turn_index, 'p1_id_in_use': p1_id_in_use, 'p2_id_in_use': p2_id_in_use, 'p1_requests_newgame': True})
            elif p2_requests_newgame:
                return jsonify({'p1_dc': p1_dc, 'p2_dc': p2_dc, 'last_move': last_move, 'winner': 'P1', 'winlist': p1_winlist, 'turn_index': turn_index, 'p1_id_in_use': p1_id_in_use, 'p2_id_in_use': p2_id_in_use, 'p2_requests_newgame': True})
            else:
                return jsonify({'p1_dc': p1_dc, 'p2_dc': p2_dc, 'last_move': last_move, 'winner': 'P1', 'winlist': p1_winlist, 'turn_index': turn_index, 'p1_id_in_use': p1_id_in_use, 'p2_id_in_use': p2_id_in_use})
        elif p2_winc == 5:
            if p1_requests_newgame:
                return jsonify({'p1_dc': p1_dc, 'p2_dc': p2_dc, 'last_move': last_move, 'winner': 'P2', 'winlist': p2_winlist, 'turn_index': turn_index, 'p1_id_in_use': p1_id_in_use, 'p2_id_in_use': p2_id_in_use, 'p1_requests_newgame': True})
            elif p2_requests_newgame:
                return jsonify({'p1_dc': p1_dc, 'p2_dc': p2_dc, 'last_move': last_move, 'winner': 'P2', 'winlist': p2_winlist, 'turn_index': turn_index, 'p1_id_in_use': p1_id_in_use, 'p2_id_in_use': p2_id_in_use, 'p2_requests_newgame': True})
            else:
                return jsonify({'p1_dc': p1_dc, 'p2_dc': p2_dc, 'last_move': last_move, 'winner': 'P2', 'winlist': p2_winlist, 'turn_index': turn_index, 'p1_id_in_use': p1_id_in_use, 'p2_id_in_use': p2_id_in_use})

        elif p1_requests_reset and session["user_id"] == 1:
            p1_requests_reset = False
            p1_requests_newgame = False
            p1_stalemate = False
            return jsonify({'p1_stalemate': True, 'p2_stalemate': True, 'p1_dc': p1_dc, 'p2_dc': p2_dc, 'last_move': last_move, 'turn_index': turn_index, 'p1_id_in_use': p1_id_in_use, 'p2_id_in_use': p2_id_in_use, 'p1_requests_newgame': True, 'p2_requests_newgame': True})
        elif p2_requests_reset and session["user_id"] == 2:
            p2_requests_reset = False
            p2_requests_newgame = False
            p2_stalemate = False
            return jsonify({'p1_stalemate': True, 'p2_stalemate': True, 'p1_dc': p1_dc, 'p2_dc': p2_dc, 'last_move': last_move, 'turn_index': turn_index, 'p1_id_in_use': p1_id_in_use, 'p2_id_in_use': p2_id_in_use, 'p1_requests_newgame': True, 'p2_requests_newgame': True})
        else:
            return jsonify({'p1_dc': p1_dc, 'p2_dc': p2_dc, 'last_move': last_move, 'turn_index': turn_index, 'p1_id_in_use': p1_id_in_use, 'p2_id_in_use': p2_id_in_use})

    # Handle moves
    temptd = request.args.get("td")

    if temptd:
        if p1_winc < 5 and p2_winc < 5:
            if gameboard[temptd] == 0 and p1_id_in_use and p2_id_in_use:
                if session["user_id"] == 1 and turn_index == 1:
                    gameboard[temptd] = "X"
                    last_move = temptd

                if session["user_id"] == 2 and turn_index == 2:
                    gameboard[temptd] = "O"
                    last_move = temptd

                # Check rows for win condition
                total_marks = 0
                for i in range(16):
                    p1_winc = 0
                    p2_winc = 0
                    for j in range(i * 16, (i + 1) * 16):
                        if gameboard['b' + str(j)] == "X":
                            p1_winc += 1
                            p1_winlist.append('b' + str(j))
                            total_marks += 1
                        else:
                            p1_winc = 0
                            p1_winlist.clear()
                        if p1_winc == 5:
                            return jsonify(True)

                        if gameboard['b' + str(j)] == "O":
                            p2_winc += 1
                            p2_winlist.append('b' + str(j))
                            total_marks += 1
                        else:
                            p2_winc = 0
                            p2_winlist.clear()
                        if p2_winc == 5:
                            return jsonify(True)

                # Check columns for win condition
                for i in range(16):
                    p1_winc = 0
                    p2_winc = 0
                    for j in range(i, 241 + i, 16):
                        if checkwin(j):
                            return jsonify(True)

                # Check diagonals for win condition
                for i in range(12):
                    p1_winc = 0
                    p2_winc = 0
                    for j in range(4 + i, (5 + i) + (4 + i) * 15, 15):
                        if checkwin(j):
                            return jsonify(True)

                for i in range(12):
                    p1_winc = 0
                    p2_winc = 0
                    for j in range(15 + (i * 16), 241 + i, 15):
                        if checkwin(j):
                            return jsonify(True)

                for i in range(12):
                    p1_winc = 0
                    p2_winc = 0
                    for j in range(i, 256 - (i * 16), 17):
                        if checkwin(j):
                            return jsonify(True)

                for i in range(12):
                    p1_winc = 0
                    p2_winc = 0
                    for j in range(i * 16, 256 - i, 17):
                        if checkwin(j):
                            return jsonify(True)

                # If win condition isn't met, return a successful gamestate variable
                if session["user_id"] == turn_index:

                    if turn_index == 1:
                        turn_index = 2
                    else:
                        turn_index = 1

                    return jsonify(True)
                else:
                    return jsonify(False)

            else:
                return jsonify(False)

        else:
            return jsonify(False)


@app.route("/")
def index():
    """ Index """

    # Access global variables
    global gameboard

    global p1_winc
    global p2_winc
    global p1_winlist
    global p2_winlist

    global total_marks

    global p1_stalemate
    global p2_stalemate

    global last_move
    global turn_index

    global p1_requests_newgame
    global p2_requests_newgame

    global p1_requests_reset
    global p2_requests_reset

    global p1_time_out
    global p2_time_out

    global p1_dc
    global p2_dc

    global p1_id_in_use
    global p2_id_in_use

    # Handle the case of both players disconnecting simultaneously
    if p1_id_in_use and p2_id_in_use:
        if p1_time_out and datetime.now() - p1_time_out > timedelta(seconds=5) and p2_time_out and datetime.now() - p2_time_out > timedelta(seconds=5):
            p1_id_in_use = False
            p2_id_in_use = False

            # Reset the gameboard
            for i in range(256):
                gameboard['b' + str(i)] = 0

            # Reset the global variables
            last_move = 0

            # Give loser the first move
            if p1_winc == 5:
                turn_index = 2

            if p2_winc == 5:
                turn_index = 1

            p1_winc = 0
            p2_winc = 0
            p1_winlist.clear()
            p2_winlist.clear()

    # Kickstart the time-out timers in case of a disconnect
    if not p1_id_in_use:
        session["user_id"] = 1
        p1_id_in_use = True
        p1_time_out = datetime.now()
        p2_time_out = datetime.now()

    elif not p2_id_in_use:
        session["user_id"] = 2
        p2_id_in_use = True
        p1_time_out = datetime.now()
        p2_time_out = datetime.now()

    # If 2 players already playing:
    else:
        return apology("Game already in session")

    return render_template("index.html", playerid=session["user_id"])


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


# Check win condition
def checkwin(j):

    # Access global variables
    global gameboard

    global p1_winc
    global p2_winc
    global p1_winlist
    global p2_winlist

    if gameboard['b' + str(j)] == "X":
        p1_winc += 1
        p1_winlist.append('b' + str(j))
    else:
        p1_winc = 0
        p1_winlist.clear()
    if p1_winc == 5:
        return True

    if gameboard['b' + str(j)] == "O":
        p2_winc += 1
        p2_winlist.append('b' + str(j))
    else:
        p2_winc = 0
        p2_winlist.clear()
    if p2_winc == 5:
        return True

    return False
