5-in-a-row

An advanced version of tic-tac-toe with a 16x16 grid and 5 times "X" or "O" in a row as a win condition (columns and diagonals work too).
The application provides an online gameboard for 2 players at a time.

In case of a win condition, both opponents are provided with an opportunity to start another game, with gameboard being reset both on server and user side.
Should a stalemate happen (all cells filled without a victor emerging), the gameboard will be reset.

When 2 players are already online, any third visitor will be notified of an on-going game session and rejected a place at the gameboard.

Disconnects (timeouts) are handled by update requests to the server from the users,
with first player's update requests keeping alive second player's timeout condition and vice versa.
If player 2 disconnects, player 1 will have the chance to reset the gameboard and wait for a new opponent, same goes the other way around.

If both players disconnect at the same time, the next "/" request to the server will reset the gameboard and free both player spots.

Credits:
Johannes Sarapuu
Tallinn, Estonia