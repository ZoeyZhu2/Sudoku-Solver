from itertools import combinations
import random

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
    for box in range(9):
        nums = set()
        for row in range(box // 3 * 3, box // 3 * 3 + 3):
            for col in range(box % 3 * 3, box % 3 * 3 + 3):
                if board[row][col] == 0:
                    return False
                else:
                    nums.add(board[row][col])
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
    new_board, candidates = updateBoard(new_board, candidates)
    if check(new_board) == False:
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

    updated = True

    while (updated):
        old_candidates = {key: set(value) for key, value in new_candidates.items()}
        #solving in a chiastic order of complexity from simple -> complex -> simple
        #naked singles: only one candidate
        new_board, new_candidates = naked_singles(new_board, new_candidates)
        old_candidates = {key: set(value) for key, value in new_candidates.items()}
        #hidden singles: a number can only go in one cell in a row/column/box, even if that cell has multiple candidates
        new_board, new_candidates = hidden_singles(new_board, new_candidates)
        old_candidates = {key: set(value) for key, value in new_candidates.items()}
        #naked pairs: remove candidates if there's two cells with the same 2 candidates
        new_board, new_candidates = naked_pairs(new_board, new_candidates)
        if old_candidates != new_candidates:
            continue
        old_candidates = {key: set(value) for key, value in new_candidates.items()}
        #hidden pairs: two numbers only appear in two cells within a unit, so all other candidates in those cells can be eliminated
        new_board, new_candidates = hidden_pairs(new_board, new_candidates)
        if old_candidates != new_candidates:
            continue
        old_candidates = {key: set(value) for key, value in new_candidates.items()}        
        #pointing pairs: if a candidate IN A BOX only appears in ONE row or col IN THAT BOX, it can be eliminated from that row/col outside of the box
        new_board, new_candidates = pointing_pairs(new_board, new_candidates)
        if old_candidates != new_candidates:
            continue
        old_candidates = {key: set(value) for key, value in new_candidates.items()}      
        #naked triples: three cells in a unit share the same 3 candidates
        new_board, new_candidates = naked_triples(new_board, new_candidates)
        if old_candidates != new_candidates:
            continue
        old_candidates = {key: set(value) for key, value in new_candidates.items()}
        #box line reduction: if a candidate IN A ROW/COL only appears in ONE box IN THE ROW/COL, it can be eliminated from that box outside of the ROW/COL
        new_board, new_candidates = box_line_reduction(new_board, new_candidates)
        if old_candidates != new_candidates:
            continue
        old_candidates = {key: set(value) for key, value in new_candidates.items()}
        #X-wing: only two cells for a candidate in two diff rows/cols, and they appear in the same cols/rows, then the candidate can be eliminated from the rest of the cols outside the rows or rows outside of the cols
        new_board, new_candidates = x_wing(new_board, new_candidates)
        if old_candidates != new_candidates:
            continue
        old_candidates = {key: set(value) for key, value in new_candidates.items()}   
        #Swordfish: only two cells for a candidate in 3 diff rows/cols, and they appear in the same 3 cols/rows, then the candidate can be eliminated from the rest of the cols outside of the rows or the rows outside of the cols
        new_board, new_candidates = swordfish(new_board, new_candidates)
        if old_candidates != new_candidates:
            continue
        old_candidates = {key: set(value) for key, value in new_candidates.items()}
        #XY-wing: a cell containing two values intersects two other cells each containing a value from the middle cell and a shared third value (each cell has 2 values). Then everything else in the units of the two wing cells cannot contain the value shared by the wing cells. 
        new_board, new_candidates = xy_wing(new_board, new_candidates)
        if old_candidates == new_candidates:
            updated = False
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
                candidates = update_candidates_around_two_in_a_box(board, candidates, cell_one[0], cell_two[0], cell_one[1], cell_two[1], p, q)       
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

#pointing pairs: if a candidate IN A BOX only appears in ONE row or col IN THAT BOX, it can be eliminated from that row/col outside of the box
def pointing_pairs(board, candidates):
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
        for candidate in candidate_cells:
            cells = candidate_cells[candidate]
            if len(cells) <= 3:  # only 2 or 3 cells can form a pointing pair
                rows = list()
                cols = list()
                for i in range(len(cells)):
                    rows.append(cells[i][0])
                    cols.append(cells[i][1])
                r = rows[0]
                c = cols[0]
                same_row = True
                same_col = True
                for rs in rows:
                    if rs != r:
                        same_row = False
                for cs in cols:
                    if cs != c:
                        same_col = False
                if same_row == True:
                    for j in range(9):
                        if j < box % 3 * 3 or j >= box % 3 * 3 + 3:  # outside the box
                            if (r, j) in candidates:
                                candidates[(r, j)].discard(candidate)

                if same_col == True:
                    for i in range(9):
                        if i < box // 3 * 3 or i >= box // 3 * 3 + 3:  # outside the box
                            if (i, c) in candidates:
                                candidates[(i, c)].discard(candidate)
    return board, candidates

def naked_triples(board, candidates):
    #rows
    for row in range(9):
        potential_cells = [(row, col) for col in range(9) if (row, col) in candidates and len(candidates[(row,col)]) <= 3]
        for (c1, c2, c3) in combinations(potential_cells, 3):
            union = candidates[c1] | candidates[c2] | candidates[c3]
            if len(union) == 3:
                val_one, val_two, val_three = union
                candidates = update_candidates_around_three_in_a_row(board, candidates, row, c1[1], c2[1], c3[1], val_one, val_two, val_three)
    #columns
    for col in range(9):
        potential_cells = [(row, col) for row in range(9) if (row, col) in candidates and len(candidates[(row,col)]) <= 3]
        for (c1, c2, c3) in combinations(potential_cells, 3):
            union = candidates[c1] | candidates[c2] | candidates[c3]
            if len(union) == 3:
                val_one, val_two, val_three = union       
                candidates = update_candidates_around_three_in_a_col(board, candidates, c1[0], c2[0], c3[0], col, val_one, val_two, val_three)
    #boxes
    for box in range(9):
        potential_cells = [(row, col) for row in range(box // 3 * 3, box // 3 * 3 + 3) for col in range (box % 3 * 3, box % 3 * 3 + 3) if (row, col) in candidates and len(candidates[(row,col)]) <= 3]
        for (c1, c2, c3) in combinations(potential_cells, 3):
            union = candidates[c1] | candidates[c2] | candidates[c3]
            if len(union) == 3:
                val_one, val_two, val_three = union       
                candidates = update_candidates_around_three_in_a_box(board, candidates, c1[0], c2[0], c3[0], c1[1], c2[1], c3[1], val_one, val_two, val_three)
    return board, candidates

    #box line reduction: if a candidate IN A ROW/COL only appears in ONE box IN THE ROW/COL, it can be eliminated from that BOX outside of the ROW/COL
def box_line_reduction(board, candidates):
    #check row
    for row in range(9):
        candidate_cells = {} #candidates -> cells
        for col in range(9):
            if (row, col) in candidates:
                for candidate in candidates[(row, col)]:
                    if candidate in candidate_cells:
                        candidate_cells[candidate].append((row, col))
                    else:
                        candidate_cells[candidate] = [(row,col)]
        potential = {candidate: cells for candidate, cells in candidate_cells.items() if len(cells) <= 3}
        #if cells are all in the same box
        for candidate, cells in potential.items():
            boxes = set(cell[1] // 3 for cell in cells) 
            same_box = len(boxes) == 1
            if same_box:
                (i, j) = cells[0]
                for r in range(i // 3 * 3, i // 3 * 3 + 3):
                    for c in range(j // 3 * 3, j // 3 * 3 + 3):
                        if (r,c) in candidates and r != i:
                            candidates[(r,c)].discard(candidate)

    #check col
    for col in range(9):
        candidate_cells = {} #candidates -> cells
        for row in range(9):
            if (row, col) in candidates:
                for candidate in candidates[(row, col)]:
                    if candidate in candidate_cells:
                        candidate_cells[candidate].append((row, col))
                    else:
                        candidate_cells[candidate] = [(row,col)]
        potential = {candidate: cells for candidate, cells in candidate_cells.items() if len(cells) <= 2}
        #if cells are all in the same box
        for candidate, cells in potential.items():
            boxes = set(cell[0] // 3 for cell in cells) 
            same_box = len(boxes) == 1
            if same_box:
                (i, j) = cells[0]
                for r in range(i // 3 * 3, i // 3 * 3 + 3):
                    for c in range(j // 3 * 3, j // 3 * 3 + 3):
                        if (r, c) in candidates and c != j:
                            candidates[(r, c)].discard(candidate)
    return board, candidates

#X-wing: only two cells for a candidate in two diff rows/cols, and they appear in the same cols/rows, then the candidate can be eliminated from the rest of the cols outside the rows or rows outside of the cols
def x_wing(board, candidates):
    #see if a candidate appears in (i1, j1), (i1, j2), (i2,j1), (i2,j2)
    #then eliminate from rows i1, i2, and cols j1, j2
    potential_total = {} #candidate -> cells
    for row in range(9):
        potential_row = {} #candidate -> cells
        for col in range(9):
            if (row, col) in candidates:
                for candidate in candidates[(row,col)]:
                    if candidate in potential_row:
                        potential_row[candidate].append((row,col))
                    else:
                        potential_row[candidate] = [(row,col)]
        twice = {candidate: cells for candidate, cells in potential_row.items() if len(cells) == 2}
        for key in twice:
            if key in potential_total:
                potential_total[key].extend(twice[key])
            else:
                potential_total[key] = twice[key]
    four_times = {candidate: cells for candidate, cells in potential_total.items() if len(cells) == 4}
    for key in four_times:
        cols = set(cell[1] for cell in four_times[key])
        rows = set(cell[0] for cell in four_times[key])
        if len(cols) == 2 and len(rows) == 2:  # exactly 2 rows and 2 cols = X-wing!
            j_one, j_two = cols
            i_one, i_two = rows
            for row in [i_one, i_two]:
                for col in range(9):
                    if col != j_one and col != j_two:
                        if (row, col) in candidates:
                            candidates[(row, col)].discard(key)
            for col in [j_one, j_two]:
                for row in range(9):
                    if row != i_one and row != i_two:
                        if (row, col) in candidates:
                            candidates[(row, col)].discard(key)
    return board, candidates

#Swordfish: only two cells for a candidate in 3 diff rows/cols, and they appear in the same 3 cols/rows, then the candidate can be eliminated from the rest of the cols outside of the rows or the rows outside of the cols
def swordfish(board, candidates):
    #the same candidate needs to cover 3 rows and 3 columns
    potential_total = {} #candidate -> cells
    for row in range(9):
        potential_row = {} #candidate -> cells
        for col in range(9):
            if (row, col) in candidates:
                for candidate in candidates[(row,col)]:
                    if candidate in potential_row:
                        potential_row[candidate].append((row,col))
                    else:
                        potential_row[candidate] = [(row,col)]
        maybe = {candidate: cells for candidate, cells in potential_row.items() if len(cells) >= 2 and len(cells) <= 3}
        for key in maybe:
            if key in potential_total:
                potential_total[key].extend(maybe[key])
            else:
                potential_total[key] = maybe[key]
    maybe_total = {candidate: cells for candidate, cells in potential_total.items() if len(cells) >= 6 and len(cells) <= 9}
    for key in maybe_total:
        rows = set()
        cols = set()
        for (i, j) in maybe_total[key]:
            rows.add(i)
            cols.add(j)
        if len(rows) == 3 and len(cols) == 3:
            j_one, j_two, j_three = cols
            i_one, i_two, i_three = rows
            for row in [i_one, i_two, i_three]:
                for col in range(9):
                    if col != j_one and col != j_two and col != j_three:
                        if (row, col) in candidates:
                            candidates[(row, col)].discard(key)
            for col in [j_one, j_two, j_three]:
                for row in range(9):
                    if row != i_one and row != i_two and row != i_three:
                        if (row, col) in candidates:
                            candidates[(row, col)].discard(key)
    return board, candidates

#XY-wing: only works for cells with two candidates. Take "pivot" cell that sees cells 1 and 2. Cells 1 and 2 each contain two candidates, B and C, and A and C. They must have candidates in common with pivot (which has, say A, B). Then any cells that see with cells 1 and 2 cannot have C.
#see: share row/col/box with a cell
def xy_wing(board, candidates):
    #finding all cells with two candidates
    two_candidates = {} #location -> the two candidates
    for (row,col) in candidates:
        if len(candidates[(row, col)]) == 2:
            two_candidates[(row, col)] = candidates[(row, col)]
    #finding all pivots
    for (row, col) in two_candidates:
        sees = {} #location -> two candidates
        for (i, j) in two_candidates:
            if row != i or col != j:
            #same row?
                if row == i:
                    sees[(i,j)] = two_candidates[(i,j)]
            #same col?
                if col == j:
                    sees[(i, j)] = two_candidates[(i, j)]
            #same box?
                elif row // 3 == i // 3 and col // 3 == j // 3:
                    sees[(i, j)] = two_candidates[(i, j)]
        #seeing if (row, col) is actually a pivot
        pivot_cands = two_candidates[(row, col)]
        #deleting all nonviable wings
        new_sees = {}
        if len(sees) >= 2:
            for (i, j) in sees:
                shared = sees[(i,j)] & pivot_cands #set intersection
                if len(shared) == 1:
                    new_sees[(i,j)] = sees[(i,j)]
        if len(new_sees) >= 2:
            for (i_one, j_one) in new_sees:
                for (i_two, j_two) in new_sees:
                    if i_one != i_two or j_one != j_two:
                        #check for valid wings:
                        wing_set = new_sees[(i_one, j_one)] & new_sees[(i_two, j_two)]
                        if len(wing_set) == 1 and not (wing_set & pivot_cands):                            #remove cand_one1 from all cells that see i_one, j_one AND i_two, j_two
                            val = next(iter(wing_set))
                            #make list of all valid cells
                            valid = {} #location -> candidates
                            for i in range(9):
                                for j in range(9):
                                    sees_one = False
                                    sees_two = False
                                    if (i, j) in candidates:
                                        if (i != i_one or j != j_one) and (i != i_two or j != j_two):
                                            #same row?
                                            if i == i_one:
                                                sees_one = True
                                            #same col?
                                            elif j == j_one:
                                                sees_one = True
                                            #same box?
                                            elif i // 3 == i_one // 3 and j // 3 == j_one // 3:
                                                sees_one = True
                                            #same row?
                                            if i == i_two:
                                                sees_two = True
                                            #same col?
                                            elif j == j_two:
                                                sees_two = True
                                            #same box?
                                            elif i // 3 == i_two // 3 and j // 3 == j_two // 3:
                                                sees_two = True
                                        if sees_one == True and sees_two == True:
                                            valid[(i,j)] = candidates[(i, j)]
                            for (i, j) in valid:
                                candidates[(i, j)].discard(val)
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

#updates candidates in a cell's row/box given a triple in a row
def update_candidates_around_three_in_a_row(board, candidates, i, j_one, j_two, j_three, val_one, val_two, val_three):
    #update row
    for col in range(9):
        if (i, col) in candidates:
            if col != j_one and col != j_two and col != j_three:
                candidates[(i,col)].discard(val_one)
                candidates[(i,col)].discard(val_two)
                candidates[(i,col)].discard(val_three)
    return candidates

#updates candidates in a cell's col/box given a triple in a col
def update_candidates_around_three_in_a_col(board, candidates, i_one, i_two, i_three, j, val_one, val_two, val_three):
    #update col
    for row in range(9):
        if (row, j) in candidates:
            if row != i_one and row != i_two and row != i_three:
                candidates[(row, j)].discard(val_one)
                candidates[(row, j)].discard(val_two)
                candidates[(row, j)].discard(val_three)
    return candidates

#updates candidates in a cell's box given a pair in a box
def update_candidates_around_three_in_a_box(board, candidates, i_one, i_two, i_three, j_one, j_two, j_three, val_one, val_two, val_three):
    #update box
    for row in range(i_one // 3 * 3, i_one // 3 * 3 + 3):
        for col in range(j_one // 3 * 3, j_one // 3 * 3 + 3):
            if (row, col) in candidates:
                if (row, col) != (i_one, j_one) and (row, col) != (i_two, j_two) and (row,col) != (i_three, j_three):
                    candidates[(row,col)].discard(val_one)
                    candidates[(row,col)].discard(val_two)
                    candidates[(row,col)].discard(val_three)
    return candidates

def is_solvable(board):
    #check for duplicate values
    #check rows
    for row in range(9):
        non_zero = [board[row][col] for col in range(9) if board[row][col] != 0]
        if len(non_zero) != len(set(non_zero)):  # duplicate detected!
            return False
    #check cols
    for col in range(9):
        non_zero = [board[row][col] for row in range(9) if board[row][col] != 0]
        if len(non_zero) != len(set(non_zero)):  # duplicate detected!
            return False
    #check boxes
    for box in range(9):
        non_zero = [board[row][col] for row in range(box // 3 * 3, box // 3 * 3 + 3) for col in range (box % 3 * 3, box % 3 * 3 + 3) if board[row][col] != 0]
        if len(non_zero) != len(set(non_zero)):  # duplicate detected!
            return False
            
    #see if there are multiple solutions or no solution
    copy_board = [row[:] for row in board]
    num_solutions = count_solutions(copy_board, 0)
    if (num_solutions != 1):
        return False
    return True

#just checking up to 2
def count_solutions(board, count):
    if count >= 2: #stopping at 2
        return count
    i, j = 0, 0 #this will be the first empty cell
    empty = True
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                empty = False
                i, j = row, col
                break
        if not empty:
            break
    if empty == True:
        return count + 1
    for test in range(1, 10):
        if is_valid(board, i, j, test):
            board[i][j] = test
            count = count_solutions(board, count)
            board[i][j] = 0  #resetting board[i][j]
    return count

def generate_solved_board():
    board = [[0] * 9 for i in range(9)]
    fill_board(board)
    return board

def fill_board(board):
    empty = True
    i, j = 0, 0
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                empty = False
                i, j = row, col
                break
        if not empty:
            break
    if empty == True:
        return True
    nums = list(range(1, 10))
    random.shuffle(nums)
    for test in nums:
        if is_valid(board, i, j, test):
            board[i][j] = test
            if fill_board(board):  # did it work?
                return True
            board[i][j] = 0
    return False

def generate_board(difficulty):
    board = generate_solved_board()
    num_to_delete = 0
    if difficulty == "easy":
        num_to_delete = 9
    elif difficulty == "medium":
        num_to_delete = 19
    elif difficulty == "hard":
        num_to_delete = 24
    elif difficulty == "super hard":
        num_to_delete = 29
    deleted = 0
    while deleted < num_to_delete:
        row = random.randint(0, 8)
        col = random.randint(0, 8)
        if board[row][col] == 0:
            continue
        new_board = [r[:] for r in board]
        new_board[row][col] = 0
        if is_solvable(new_board):
            board[row][col] = 0
            deleted += 1
    return board

print(solve(sudoku_board))

#Next Steps:
#add a method that takes in a sudoku board
#create a GUI to input a sudoku board
#create a GUI to solve sudoku boards
#make a solve method that shows each step as it is solved
#make this solve method pausable so I can go step by step for hints with arrows walking through steps. Think Chess.com strategy walk throughs
#add another gamemode where it creates sudoku boards of varying difficulty for you to solve
#so will have two modes: 1 to get the solution to an external sudoku board, another to solve the sudoku on the website and i can get hints and check with the solve method
#hints will highlight the square, show next number will fill in a number

