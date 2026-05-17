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

#updates candidates for a particular cell.
def update_candidates_cell(board, candidates, i, j):
    if (i, j) in candidates:
        candidates[(i,j)] = candidates[(i,j)] - get_row_candidates(board, i)
        candidates[(i,j)] = candidates[(i,j)] - get_col_candidates(board, j)
        candidates[(i,j)] = candidates[(i,j)] - get_box_candidates(board, i, j)
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

#helper method for solve(board)
def updateBoard(board, candidates):
    #copying board and candidates so I don't change the parameters and can compare new with old in solve(board)
    new_board = [row[:] for row in board]
    new_candidates = {key: set(value) for key, value in candidates.items()}

    #solving in a chiastic order of complexity from simple -> complex -> simple
    #naked singles: only one candidate
    new_board, new_candidates = naked_singles(new_board, new_candidates)

    #hidden singles: a number can only go in one cell in a row/column/box, even if that cell has multiple candidates
    new_board, new_candidates = hidden_singles(new_board, new_candidates)

    #naked pairs: remove candidates if there's two cells with the same 2 candidates
    new_board, new_candidates = naked_pairs(new_board, new_candidates)
    #Question: should I be checking for naked and hidden signles after each new strategy?

    #hidden pairs: two numbers only appear in two cells within a unit, so all other candidates in those cells can be eliminated
    new_board, new_candidates = hidden_pairs(new_board, new_candidates)

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
                    candidates = update_candidates_around_one(board, candidates, i, j, board[i][j])
    return board, candidates

def hidden_singles(board, candidates):
    #will have to check separately for rows, cols, and boxes
    #making a new dict where the candidate values are the keys
    nums = {} #candidate -> frequency

    #check rows
    for row in range(9):
        #adding keys 1-9
        for num in range(1,10):
            nums[num] = set()
        for col in range(9):
            if (row, col) in candidates:
                for i in candidates[(row, col)]:
                    nums[i].add((row, col))
        for num in range(1, 10):
            if len(nums[num]) == 1:
                (i, j) = next(iter(nums[num]))
                board[i][j] = num
                del candidates[(i,j)]
                candidates = update_candidates_around_one(board, candidates, i, j, num)
    #check cols
    for col in range(9):
        #adding keys 1-9
        for num in range(1,10):
            nums[num] = set()
        for row in range(9):
            if (row, col) in candidates:
                for i in candidates[(row,col)]:
                    nums[i].add((row, col))
        for num in range(1, 10):
            if len(nums[num]) == 1:
                (i, j) = next(iter(nums[num]))
                board[i][j] = num
                del candidates[(i,j)]
                candidates = update_candidates_around_one(board, candidates, i, j, num)
        
    #check boxes
    # 0 1 2
    # 3 4 5
    # 6 7 8
    for box in range(9):
        #adding keys 1-9
        for num in range(1,10):
            nums[num] = set()
        for row in range(box // 3 * 3, box // 3 * 3 + 3):
            for col in range((box % 3) * 3, (box % 3) * 3 + 3):
                if (row, col) in candidates:
                    for i in candidates[(row, col)]:
                        nums[i].add((row, col))
        for num in range(1, 10):
            if len(nums[num]) == 1:
                (i, j) = next(iter(nums[num]))
                board[i][j] = num
                del candidates[(i,j)]
                candidates = update_candidates_around_one(board, candidates, i, j, num)
    return board, candidates

def naked_pairs(board, candidates):
    #create a set called keys with tuples of candidates
    #only add boxes with two candidates
    #see if any keys in keys have exactly 2 boxes
    #must check every row, column, and box
    #check rows
    for row in range(9):
        keys = {} #candidate -> location
        for col in range(9):
            #adding all cells with two candidates into dict keys
            if (row, col) in candidates:
                if len(candidates[(row,col)]) == 2:
                    key = frozenset(candidates[(row, col)])
                    if key in keys:
                            keys[key].append((row, col))
                    else:
                        keys[key] = [(row, col)]
        for key, cells in keys.items():
            #seeing if there are two cells with the same two candidates
            if len(cells) == 2:
                cell_one, cell_two = cells
                p, q = key
                candidates = update_candidates_around_two_in_a_row(board, candidates, row, cell_one[1], cell_two[1], p, q)       
    #check columns
    for col in range(9):
        keys = {} #candidate -> location
        for row in range(9):
            #adding all cells with two candidates into dict keys
            if (row, col) in candidates:
                if len(candidates[(row, col)]) == 2:
                    key = frozenset(candidates[(row, col)])
                    if key in keys:
                            keys[key].append((row, col))
                    else:
                        keys[key] = [(row, col)]
        for key, cells in keys.items():
            #seeing if there are two cells with the same two candidates
            if len(cells) == 2:
                cell_one, cell_two = cells
                p, q = key
                candidates = update_candidates_around_two_in_a_col(board, candidates, cell_one[0], cell_two[0], col, p, q)       
    #check boxes
    for box in range (9):
        keys = {}
        for row in range(box // 3 * 3, box // 3 * 3+ 3):
            for col in range(box % 3 * 3, box % 3 * 3+ 3):
            #adding all cells with two candidates into dict keys
                if (row, col) in candidates:
                    if len(candidates[(row, col)]) == 2:
                        key = frozenset(candidates[(row, col)])
                        if key in keys:
                            keys[key].append((row, col))
                        else:
                            keys[key] = [(row, col)]
        for key, cells in keys.items():
            #seeing if there are two cells with the same two candidates
            if len(cells) == 2:
                cell_one, cell_two = cells
                p, q = key
                candidates = update_candidates_around_two_in_a_row(board, candidates, row, cell_one[1], cell_two[1], p, q)       
    return board, candidates

def hidden_pairs(board, candidates):
    #if nothing else can be two candidates except in two cells
    #add all potential candidates to a dict and count times they appear so candidate:frequency
    #then locate the two cells with the two candidates if possible
    #rows
    for row in range(9):
        candidate_cells = {}  # candidate -> list of cells it appears in
        for col in range(9):
            if (row, col) in candidates:
                for candidate in candidates[(row,col)]:
                    if candidate in candidate_cells:
                        candidate_cells[candidate].append((row, col))
                    else:
                        candidate_cells[candidate] = [(row,col)]
        twice = {candidate: cells for candidate, cells in candidate_cells.items() if len(cells) == 2}
        #make a dictionary candidate -> cells if the length of the candidate locations is 2
        #candidate_cells.items() returns a tuple (candidate, list of cells)
        for cand_1 in twice:
            for cand_2 in twice:
                if cand_1 < cand_2: #avoid duplicates
                    if twice[cand_1] == twice[cand_2]: #since the order of the location tuples will be the same
                    #update candidates
                        cell_one, cell_two = twice[cand_1]
                        candidates[cell_one] = {cand_1, cand_2}
                        candidates[cell_two] = {cand_1, cand_2}
                        candidates = update_candidates_around_two_in_a_row(board, candidates, row, cell_one[1], cell_two[1], cand_1, cand_2)

    #columns
    for col in range(9):
        candidate_cells = {}  # candidate -> list of cells it appears in
        for row in range(9):
            if (row, col) in candidates:
                for candidate in candidates[(row,col)]:
                    if candidate in candidate_cells:
                        candidate_cells[candidate].append((row, col))
                    else:
                        candidate_cells[candidate] = [(row,col)]
        twice = {candidate: cells for candidate, cells in candidate_cells.items() if len(cells) == 2}
        #make a dictionary candidate -> cells if the length of the candidate locations is 2
        #candidate_cells.items() returns a tuple (candidate, list of cells)
        for cand_1 in twice:
            for cand_2 in twice:
                if cand_1 < cand_2: #avoid duplicates
                    if twice[cand_1] == twice[cand_2]: #since the order of the location tuples will be the same
                    #update candidates
                        cell_one, cell_two = twice[cand_1]
                        candidates[cell_one] = {cand_1, cand_2}
                        candidates[cell_two] = {cand_1, cand_2}
                        candidates = update_candidates_around_two_in_a_col(board, candidates, cell_one[0], cell_two[0], col, cand_1, cand_2)
    #boxes
    for box in range(9):
        candidate_cells = {}  # candidate -> list of cells it appears in
        for row in range(box // 3 * 3, box // 3 * 3 + 3):
            for col in range(box % 3 * 3, box % 3 * 3 + 3):
                if (row, col) in candidates:
                    for candidate in candidates[(row,col)]:
                        if candidate in candidate_cells:
                            candidate_cells[candidate].append((row, col))
                        else:
                            candidate_cells[candidate] = [(row,col)]
        twice = {candidate: cells for candidate, cells in candidate_cells.items() if len(cells) == 2}
        #make a dictionary candidate -> cells if the length of the candidate locations is 2
        #candidate_cells.items() returns a tuple (candidate, list of cells)
        for cand_1 in twice:
            for cand_2 in twice:
                if cand_1 < cand_2: #avoid duplicates
                    if twice[cand_1] == twice[cand_2]: #since the order of the location tuples will be the same
                    #update candidates
                        cell_one, cell_two = twice[cand_1]
                        candidates[cell_one] = {cand_1, cand_2}
                        candidates[cell_two] = {cand_1, cand_2}
                        candidates = update_candidates_around_two_in_a_box(board, candidates, cell_one[0], cell_two[0], cell_one[1], cell_two[1], cand_1, cand_2)
    return board, candidates

#updates candidates in a cell's row/col/box after that cell has been changed
def update_candidates_around_one(board, candidates, i, j, val):
    #update row
    for col in range(9):
        if (i, col) in candidates:
            candidates[(i,col)].discard(val)
    #update col
    for row in range(9):
        if (row, j) in candidates:
            candidates[(row,j)].discard(val)
    #update box
    for row in range(i // 3 * 3, i // 3 * 3 + 3):
        for col in range(j // 3 * 3, j // 3 * 3 + 3):
            if (row, col) in candidates:
                candidates[(row,col)].discard(val)
    return candidates

#updates candidates in a cell's row/box given a pair in a row
def update_candidates_around_two_in_a_row(board, candidates, i, j_one, j_two, val_one, val_two):
    #update row
    for col in range(9):
        if (i, col) in candidates:
            if col != j_one and col != j_two:
                candidates[(i,col)].discard(val_one)
                candidates[(i,col)].discard(val_two)
    return candidates

#updates candidates in a cell's col/box given a pair in a col
def update_candidates_around_two_in_a_col(board, candidates, i_one, i_two, j, val_one, val_two):
    #update col
    for row in range(9):
        if (row, j) in candidates:
            if row != i_one and row != i_two:
                candidates[(row, j)].discard(val_one)
                candidates[(row, j)].discard(val_two)
    return candidates

#updates candidates in a cell's box given a pair in a box
def update_candidates_around_two_in_a_box(board, candidates, i_one, i_two, j_one, j_two, val_one, val_two):
    #update box
    for row in range(i_one // 3 * 3, i_one // 3 * 3 + 3):
        for col in range(j_one // 3 * 3, j_one // 3 * 3 + 3):
            if (row, col) in candidates:
                if (row, col) != (i_one, j_one) and (row, col) != (i_two, j_two):
                    candidates[(row,col)].discard(val_one)
                    candidates[(row,col)].discard(val_two)
    return candidates

print(solve(sudoku_board))

#Next Steps:
#add all sudoku solving strategies
#add a method checking if a sudoku board is solvable
#add a method creating a solvable sudoku board
#make methods creating solvable sudoku boards of diff difficultires
#add a method that takes in a sudoku board
#create a GUI to input a sudoku board
#create a GUI to solve sudoku boards
#make a solve method that shows each step as it is solved
#make this solve method pausable so I can go step by step for hints with arrows walking through steps. Think Chess.com strategy walk throughs
#add another gamemode where it creates sudoku boards of varying difficulty for you to solve
#so will have two modes: 1 to get the solution to an external sudoku board, another to solve the sudoku on the website and i can get hints and check with the solve method
#hints will highlight the square, show next number will fill in a number

