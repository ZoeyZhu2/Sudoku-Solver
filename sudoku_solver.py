# sudoku_board = [
#     [0,0,0,0,0,0,0,0,0], 
#     [0,0,0,0,0,0,0,0,0], 
#     [0,0,0,0,0,0,0,0,0], 
#     [0,0,0,0,0,0,0,0,0], 
#     [0,0,0,0,0,0,0,0,0], 
#     [0,0,0,0,0,0,0,0,0], 
#     [0,0,0,0,0,0,0,0,0], 
#     [0,0,0,0,0,0,0,0,0], 
#     [0,0,0,0,0,0,0,0,0]
# ]

sudoku_board = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]

# check if a number is valid
def is_valid(board, rowNum, colNum, value):
    #check if value in row
    if value in board[rowNum]:
        return False
    #check if value in column
    for i in range(9):
        if board[i][colNum] == value:
            return False
    #check if value in row
    for i in range(rowNum // 3 * 3, rowNum // 3 * 3+ 3):
        for j in range(colNum // 3 * 3, colNum // 3 * 3+ 3):
            if board[i][j] == value:
                return False
    return True


def check(board):
    #check if sudoku_board is correct, so all cells have one value, and every value is valid
    if check_rows(board) == False:
        return False
    if check_cols(board) == False:
        return False
    if check_boxes(board) == False:
        return False
    return True
    #eventually locate the errors

def check_rows(board):
    for i in range(9):
        nums = set()
        for j in range(9):
            if board[i][j] == 0:
                return False
            else:
                nums.add(board[i][j])
        if len(nums) != 9:
            return False
    return True;       
    

def check_cols(board):
    for j in range(9):
        nums = set()
        for i in range(9):
            if board[i][j] == 0:
                return False
            else:
                nums.add(board[i][j])
        if len(nums) != 9:
            return False
    return True


def check_boxes(board):
    for x in range(3):
        for i in range(x * 3, x * 3 + 3):
            nums = set()
            for y in range (3):
                for j in range(y * 3, y * 3 + 3):
                    if board[i][j] == 0:
                        return False
                    else:
                        nums.add(board[i][j])
        if len(nums) != 9:
            return False
    return True


def solve(board):
    candidates = {} #python dictionaries are like a Java HashMap
    #candidates[(0,0)] = {1, 3 , 7} #key is (0,0), a cell location. Set its value equal to a HashSet (just Set in python) of candidate values

    #populate candidates with starting values
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                candidates[(i,j)] = {1,2,3,4,5,6,7,8,9}
                #remove originally present candidates
                candidates = update_candidates_cell(board, candidates, i, j)

    new_board = [row[:] for row in board]
    while check(new_board) == False:
        old_board = [row[:] for row in new_board]
        new_board, candidates = updateBoard(new_board, candidates)
        if old_board == new_board:
            return "stuck"
    return new_board
    

def updateBoard(board, candidates):
    #copying board and candidates so I don't change the parameters and can compare new with old in solve(board)
    new_board = [row[:] for row in board]
    new_candidates = {key: set(value) for key, value in candidates.items()}

    #solve in order of complexity
    #naked singles: only one candidate
    new_board, new_candidates = naked_singles(new_board, new_candidates)

    #hidden singles: a number can only go in one cell in a row/column/box, even if that cell has multiple candidates
    #will have to check separately for rows, cols, and boxes
    #check rows
    for i in range(9):
        #keep track of count of each candidate 1-9 in the row. 
        for j in range(9):
            #idk pick up here
    #check cols

    #check boxes


    #naked pairs: remove candidates if there's two cells with the same 2 candidates
    #hidden pairs: two numbers only appear in two cells within a unit, so all other candidates in those cells can be eliminated
    #pointing pairs: if a candidate IN A BOX only appears in ONE row or col IN THAT BOX, it can be eliminated from that row/col outside of the box
    #naked triples: three cells in a unit share the same 3 candidates
    #box line reduction: if a candidate IN A ROW/COL only appears in ONE box IN THE ROW/COL, it can be eliminated from that box outside of the ROW/COL
    #X-wing: only two cells for a candidate in two diff rows/cols, and they appear in the same cols/rows, then the candidate can be eliminated from the rest of the cols outside the rows or rows outside of the cols
    #Swordfish: only two cells for a candidate in 3 diff rows/cols, and they appear in the same 3 cols/rows, then the candidate can be eliminated from the rest of the cols outside of the rows or the rows outside of the cols
    #XY-wing: a cell containing two values intersects two other cells each containing a value from the middle cell and a shared third value (each cell has 2 values). Then everything else in the units of the two wing cells cannot contain the value shared by the wing cells. 

    return new_board, new_candidates
        
#solves for naked singles in place, which is okay becuase I put new_board and new_candidates in as parameters
def naked_singles(board, candidates):
    for i in range(9):
        for j in range(9):
            #identify candidate sets with only 1 value
            if board[i][j] == 0:
                if len(candidates[(i,j)]) == 1:
                    #remove value and set as board value
                    board[i][j] = next(iter(candidates[(i,j)]))
                    del candidates[(i,j)]
                    #now update candidates around
                    candidates = update_candidates_around(board, candidates, i, j, board[i][j])
    return board, candidates

#updates candidates for a particular cell.
def update_candidates_cell(board, candidates, i, j):
    if (i, j) in candidates:
        candidates[(i,j)] = candidates[(i,j)] - get_row_candidates(board, i)
        candidates[(i,j)] = candidates[(i,j)] - get_col_candidates(board, j)
        candidates[(i,j)] = candidates[(i,j)] - get_box_candidates(board, i, j)
    return candidates

#updates candidates in a cell's row/col/box after that cell has been changed
def update_candidates_around(board, candidates, i, j, val):
    #update row
    for col in range(9):
        if (i, col) in candidates:
            candidates[(i,col)] = candidates[(i,col)].discard(val)
    #update col
    for row in range(9):
        if (row, j) in candidates:
            candidates[(row,j)] = candidates[(row,j)].discard(val)
    #update box
    for row in range(i // 3 * 3, i // 3 * 3 + 3):
        for col in range(j // 3 * 3, j // 3 * 3 + 3):
            candidates[(row,col)] = candidates[(row,col)].discard(val)
    return candidates


def get_row_candidates(board, i):
    row_candidates = set()
    for j in range(9):
        if board[i][j] != 0:
            row_candidates.add(board[i][j])
    return row_candidates

def get_col_candidates(board, j):
    col_candidates = set()
    for i in range(9):
        if board[i][j] != 0:
            col_candidates.add(board[i][j])
    return col_candidates

def get_box_candidates(board, i, j):
    box_candidates = set()
    for row in range(i // 3 * 3, i // 3 * 3 + 3):
        for col in range(j // 3 * 3, j // 3 * 3 + 3):
            if board[row][col] != 0:
                box_candidates.add(board[row][col])
    return box_candidates

print(solve(sudoku_board))

#Next Steps:
#add all sudoku solving strategies
#add a method checking if a sudoku board is solvable
#add a method that takes in a sudoku board
#create a GUI to input a sudoku board
#make a solve method that shows each step as it is solved
#make this solve method pausable so I can go step by step for hints with arrows walking through steps. Think Chess.com strategy walk throughs
#add another gamemode where it creates sudoku boards of varying difficulty for you to solve
