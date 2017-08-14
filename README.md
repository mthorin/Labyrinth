# Labyrinth Board Game Simulation
<img src="http://www.mindgames.ca/content/images/thumbs/0000268_labyrinth-board-game.jpeg" style="width: 350px;"/>

## How to run
`python labyrinth.py` : Runs a simulated game once with a verbose output

`python interactive_labyrinth.py` : Runs a game with human players

`python find_best_board.py` : Tries multiple simulations to find a "fair" board
(use SIGINT to print the best starting board found)

## Project Inspiration
To setup a game of Labyrinth, a bunch of maze tiles need to be randomly placed
on the gameboard. Each player starts in a different corner of the board and
traverses the maze to collect tokens. Since the tiles were placed randomly, it
seems like some players have a lot more freedom to move about the maze than others.

The primary aim of this project is to try and find the "fairest" starting board
with a secondary aim of looking into whether different rules could improve the game.

## Current Progress
- [x] Create a gameboard with the tiles placed randomly
- [x] Slide tiles horizontally and vertically when the floating tile is pushed
- [x] Add tokens that players need to pickup
- [x] Add "ai" to play the game
- [x] Add an interactive mode to allow humans to play against ai

## TODO
- [ ] Implement some of the game rule changes
- [ ] Cleanup file structure
