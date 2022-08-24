# *HyperMines*

Submitted by: **Peilin Chen**


## Introduction
In this lab you will implement a HyperMines Game

**Mines**

Mines is played on a rectangular r \times cr×c board (where rr indicates the number of rows and cc the number of columns), covered with 1\times 11×1 square tiles. Some of these tiles hide secretly buried mines; all the other squares are safe. On each turn, the player removes one tile, revealing either a mine or a safe square. The game is won when all safe squares have been revealed, without revealing a single mine, and it is lost if a mine is revealed.

The game wouldn't be very entertaining if it only involved random guessing, so the following twist is added: when a safe square is revealed, that square is additionally inscribed with a number between 0 and 8 (inclusive), indicating the number of surrounding mines (when rendering the board, 0 is replaced by a blank, or ' '). Additionally, any time a 0 is revealed (a square surrounded by no mines), all the surrounding squares are also automatically revealed (they are, by definition, safe).


## 2D Mines
The following methods are critical to the operation of the game:

- init(dimensions, bombs) - This starts a new Mines game with the correct internal values initialized. dimensions is a list representing the dimensions of the board, and bombs is a list of locations of bombs on the board.

- dig(coords) - This method digs up, or reveals, the square at the specified coordinates (coords) and then recursively digs up neighbors according to the rules of the game.

- render(xray=False) - This method returns a string representation of the current board. If xray is True (the default is False), all cells are shown regardless of whether they have already been dug.

- make_board(dimensions, elem) - This method creates a 2-D list representing a Mines board of the provided dimensions, initializing each element in the 2-D list to elem.

- is_in_bounds(coords) - This method checks a specific coordinate (coords) to see whether it is a valid location on the current board.

- neighbors(coords) - This method returns a list of all of the valid coordinates which neighbor the provided coordinate (coords).

- is_victory() - This method checks the board to see whether it satisfies the victory condition.

- dump() - This method prints a human-readable representation of the current game. Useful for debugging code

## nD HyperMines
Use recursive functions

Now that you've mastered 2-D mines, it's time to participate in the International Mines tournament! But wait! This year's tournament comes with a small twist. The tournament will be taking place on planet Htrae, and not on Earth! :) The Planet Htrae is not very different from Earth, except that space in the Yklim way, Htrae's star cluster, doesn't have three dimensions — at least, not always: it fluctuates between 2 and, on the worst days, 60. In fact, it's not uncommon for an Htraean to wake up flat, for example, and finish the day in 7 dimensions — only to find themselves living in 3 or 4 dimensions on the next morning. It takes a bit of time to get used to, of course.

## Game State

```
dimensions = [4, 3, 2]
board = [[[1, 1], ['.', 2], [2, 2]], 
         [[1, 1], [2, 2], ['.', 2]], 
         [[1, 1], [2, 2], [1, 1]], 
         [[1, '.'], [1, 1], [0, 0]]]
mask = [[[True, False], [False, False], [False, False]], 
        [[False, False], [True, False], [False, False]], 
        [[False, False], [True, True], [True, True]], 
        [[False, False], [True, True], [True, True]]]
state = "ongoing"
```
