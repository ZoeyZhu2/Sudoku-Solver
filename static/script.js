//Global
let selectedCell = null
let steps = []
let givenCells = new Set()
let initialCandidates = null
let originalBoard = null
let solvedBoard = null
let currentStep = -1  // -1 = showing original
let boardLocked = false

//Mode 2
// the puzzle board as generated (0 = empty), never changes after generation
let mode2Given = null
// the current state of the board as the player fills it in
let mode2Board = null
// the complete solution for this puzzle
let mode2Solution = null
// steps and initial candidates — same structure as Mode 1, used for hint and solve
let mode2Steps = []
let mode2InitialCandidates = null
// which step we're on when walking through solve in Mode 2
let mode2CurrentStep = -1
// which number the player has selected in the number pad (null = none)
let selectedNumber = null
// 'value' = placing actual digits, 'candidate' = placing pencil marks
let inputMode = 'value'
// player's pencil mark candidates per cell — only used in Notes mode
// structure: { "r-c": Set of numbers }
let mode2UserCandidates = {}
// which difficulty is currently selected
let mode2Difficulty = 'easy'
let selectedMode2Cell = null  // [row, col] of currently selected cell

// timer state
let timerSeconds = 0        // total seconds elapsed
let timerInterval = null    // the setInterval handle so we can clear it
let timerPaused = false     // whether the timer is currently paused

// hint state — tracks how many times hint has been clicked for the current hint
// 0 = no hint shown, 1 = cell highlighted, 2 = strategy shown, resets after step done
let hintLevel = 0
let hintStepIndex = -1  // which step in mode2Steps the current hint is pointing at


function showScreen(screenId) {
    document.querySelectorAll('#app > div').forEach(div => {
        div.classList.add('hidden')
    })
    document.getElementById(screenId).classList.remove('hidden')
    if (screenId === 'mode1-screen') buildBoard()
    if (screenId === 'mode2-screen' && mode2Board === null) newPuzzle()
}

//Mode 1 board building and input
function buildBoard() {
    boardLocked = false
    const table = document.getElementById('sudoku-board')
    table.innerHTML = ''
    givenCells.clear()
    for (let i = 0; i < 9; i++) {
        const row = document.createElement('tr')
        for (let j = 0; j < 9; j++) {
            const cell = document.createElement('td')
            cell.id = `cell-${i}-${j}`
            cell.tabIndex = 0  // makes cell focusable
            console.log('built cell', i, j, 'tabIndex:', cell.tabIndex)
            cell.addEventListener('click', () => selectCell(i, j))
            cell.addEventListener('keydown', (e) => handleKey(e, i, j))
            row.appendChild(cell)
        }
        table.appendChild(row)
    }
}

function selectCell(row, col) {
    // remove highlight from old cell
    if (selectedCell) {
        const old = document.getElementById(`cell-${selectedCell[0]}-${selectedCell[1]}`)
        old.classList.remove('selected')
        old.blur()  // remove focus from old cell
    }
    selectedCell = [row, col]
    const cell = document.getElementById(`cell-${row}-${col}`)
    cell.classList.add('selected')
    cell.focus()  // focus new cell so it receives keyboard events
}

function handleKey(e, row, col) {
    if (boardLocked) { e.preventDefault(); return }
    if (e.key >= '1' && e.key <= '9') {
        e.preventDefault()
        const cell = document.getElementById(`cell-${row}-${col}`)
        cell.textContent = e.key
        cell.dataset.value = e.key
        cell.classList.add('given')
        givenCells.add(`${row}-${col}`)
    }
    else if (e.key === 'Backspace' || e.key === 'Delete') {
        e.preventDefault()
        const cell = document.getElementById(`cell-${row}-${col}`)
        cell.textContent = ''
        cell.dataset.value = ''
        cell.classList.remove('given')
        givenCells.delete(`${row}-${col}`)
    }
    else if (e.key === 'ArrowRight') { e.preventDefault(); selectCell(row, Math.min(col+1, 8)) }
    else if (e.key === 'ArrowLeft')  { e.preventDefault(); selectCell(row, Math.max(col-1, 0)) }
    else if (e.key === 'ArrowDown')  { e.preventDefault(); selectCell(Math.min(row+1, 8), col) }
    else if (e.key === 'ArrowUp')    { e.preventDefault(); selectCell(Math.max(row-1, 0), col) }
    else e.preventDefault()
}

//Mode 1 solving and steps
async function loadBoard() {
    // read current board state from the UI
    const board = []
    for (let i = 0; i < 9; i++) {
        const row = []
        for (let j = 0; j < 9; j++) {
            const cell = document.getElementById(`cell-${i}-${j}`)
            const val = parseInt(cell.dataset.value) || 0
            row.push(val)
        }
        board.push(row)
    }

    // clear any previous error
    const errEl = document.getElementById('error-msg')
    errEl.classList.add('hidden')

    let response
    try {
        response = await fetch('/solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ board })
        })
    } catch (e) {
        errEl.textContent = 'Network error.'
        errEl.classList.remove('hidden')
        return
    }

    const data = await response.json()
    if (!response.ok) {
        errEl.textContent = data.error || 'Invalid board!'
        errEl.classList.remove('hidden')
        return
    }

    // store state
    originalBoard = board.map(row => [...row])
    solvedBoard = data.solution
    steps = data.steps
    initCandidates(data.initial_candidates)
    currentStep = -1

    // lock all cells so user can't edit mid-walkthrough
    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            const cell = document.getElementById(`cell-${i}-${j}`)
            cell.removeEventListener('keydown', cell._keyHandler)
        }
    }
    boardLocked = true
    renderBoard(originalBoard, -1)
    updateStepButtons()
    document.getElementById('strategy-display').textContent =
        `Solved in ${steps.length} steps. Use the buttons to walk through.`
}

function renderBoard(board, stepIndex) {
    // first render the board values
    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            const cell = document.getElementById(`cell-${i}-${j}`)
            const val = board[i][j]
            cell.innerHTML = ''
            if (val !== 0) {
                cell.textContent = val
            }
            // reset classes, keep 'given' for original clues
            cell.classList.remove('selected', 'solved', 'highlight-cell', 'highlight-discard')
            if (originalBoard[i][j] !== 0) {
                cell.classList.add('given')
            } else if (val !== 0) {
                cell.classList.add('solved')
            }
        }
    }

    // if we're at a real step, highlight the relevant cells
    if (stepIndex >= 0 && stepIndex < steps.length) {
        const step = steps[stepIndex]
        // highlight key cells (the ones that triggered the strategy)
        for (const [r, c] of step.cells) {
            document.getElementById(`cell-${r}-${c}`).classList.add('highlight-cell')
        }
        // highlight cells that lost candidates (or got a value placed)
        for (const [r, c, v] of step.discarded) {
            const cell = document.getElementById(`cell-${r}-${c}`)
            // only mark discard-red if the cell wasn't already marked as a key cell
            if (!cell.classList.contains('highlight-cell')) {
                cell.classList.add('highlight-discard')
            }
        }
    }
    const cands = stepIndex >= 0 ? candidatesAtStep(stepIndex) : initialCandidates
    if (cands) renderCandidates(cands)
    // discarded digit highlighting stays inside the stepIndex >= 0 block
    if (stepIndex >= 0 && stepIndex < steps.length) {
        for (const [r, c, v] of steps[stepIndex].discarded) {
            const cell = document.getElementById(`cell-${r}-${c}`)
            if (cell.classList.contains('given') || cell.classList.contains('solved')) continue
            const spans = cell.querySelectorAll('.candidate')
            if (spans.length >= v) spans[v - 1].classList.add('discarded-cand')
        }
    }
}

// build the board state at a given step index by replaying from scratch
function boardAtStep(stepIndex) {
    const board = originalBoard.map(row => [...row])
    for (let s = 0; s <= stepIndex; s++) {
        const step = steps[s]
        if (step.value !== 0) {
            const [r, c] = step.cells[0]
            board[r][c] = step.value
        }
    }
    return board
}

function showOriginal() {
    currentStep = -1
    renderBoard(originalBoard, -1)
    document.getElementById('strategy-display').textContent = 'Original puzzle.'
    updateStepButtons()
}

function prevStep() {
    if (currentStep <= 0) {
        showOriginal()
        return
    }
    currentStep--
    const board = boardAtStep(currentStep)
    renderBoard(board, currentStep)
    document.getElementById('strategy-display').textContent =
        `Step ${currentStep + 1} of ${steps.length}: ${steps[currentStep].strategy}`
    updateStepButtons()
}

function nextStep() {
    if (currentStep >= steps.length - 1) return
    currentStep++
    const board = boardAtStep(currentStep)
    renderBoard(board, currentStep)
    document.getElementById('strategy-display').textContent =
        `Step ${currentStep + 1} of ${steps.length}: ${steps[currentStep].strategy}`
    updateStepButtons()
}

function showFinal() {
    currentStep = steps.length - 1
    renderBoard(solvedBoard, -1)
    document.getElementById('strategy-display').textContent = 'Final solution.'
    updateStepButtons()
}

function updateStepButtons() {
    document.getElementById('btn-original').disabled = currentStep === -1
    document.getElementById('btn-prev').disabled = currentStep === -1
    document.getElementById('btn-next').disabled = currentStep >= steps.length - 1
    document.getElementById('btn-final').disabled = currentStep >= steps.length - 1
}

//Mode 1 candidates
// called once after loadBoard() gets the response
function initCandidates(raw) {
    // raw is {"0,2": [1,4], "1,1": [2,7], ...}
    initialCandidates = {}
    for (const key in raw) {
        const [r, c] = key.split(',').map(Number)
        if (!initialCandidates[r]) initialCandidates[r] = {}
        initialCandidates[r][c] = new Set(raw[key])
    }
}

function candidatesAtStep(stepIndex) {
    // deep copy initial state
    const cands = {}
    for (const r in initialCandidates) {
        cands[r] = {}
        for (const c in initialCandidates[r]) {
            cands[r][c] = new Set(initialCandidates[r][c])
        }
    }
    // replay steps 0 through stepIndex
    for (let s = 0; s <= stepIndex; s++) {
        const step = steps[s]
        // if a value was placed, remove that cell from candidates entirely
        if (step.value !== 0) {
            const [r, c] = step.cells[0]
            if (cands[r]) delete cands[r][c]
        }
        // apply discards
        for (const [r, c, v] of step.discarded) {
            if (cands[r] && cands[r][c]) {
                cands[r][c].delete(v)
            }
        }
    }
    return cands
}

function renderCandidates(cands) {
    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            const cell = document.getElementById(`cell-${i}-${j}`)
            if (cell.classList.contains('given') || cell.classList.contains('solved')) continue
            const cellCands = cands[i] && cands[i][j] ? cands[i][j] : new Set()
            cell.innerHTML = buildCandidateGrid(cellCands)
        }
    }
}

function buildCandidateGrid(candSet) {
    let html = '<div class="candidate-grid">'
    for (let n = 1; n <= 9; n++) {
        const visible = candSet.has(n)
        html += `<span class="candidate${visible ? '' : ' hidden-cand'}">${n}</span>`
    }
    html += '</div>'
    return html
}


//Mode 2 board building and input
function selectDifficulty(difficulty, btn) {
    // store the selected difficulty
    mode2Difficulty = difficulty
    // remove 'active' class from all difficulty buttons
    document.querySelectorAll('.diff-btn').forEach(b => b.classList.remove('active'))
    // add 'active' to the clicked button
    btn.classList.add('active')
    // immediately start a new puzzle with this difficulty
    newPuzzle()
}

async function newPuzzle() {
    // show a loading state on the board while we wait
    document.getElementById('mode2-status').textContent = 'Generating puzzle...'

    // POST to /generate with the selected difficulty
    let response
    try {
        response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ difficulty: mode2Difficulty })
        })
    } catch (e) {
        document.getElementById('mode2-status').textContent = 'Network error.'
        return
    }

    const data = await response.json()
    if (!response.ok) {
        document.getElementById('mode2-status').textContent = 'Error generating puzzle.'
        return
    }

    // store all the puzzle data
    mode2Given = data.board.map(row => [...row])       // the puzzle with 0s
    mode2Board = data.board.map(row => [...row])       // player's working copy
    mode2Solution = data.solution                       // the full solution
    mode2Steps = data.steps                             // steps for hint/solve
    mode2UserCandidates = {}                            // clear any pencil marks
    mode2CurrentStep = -1                               // reset solve walkthrough
    hintLevel = 0                                       // reset hint state
    hintStepIndex = -1

    // parse initial candidates same way as Mode 1
    mode2InitialCandidates = {}
    for (const key in data.initial_candidates) {
        const [r, c] = key.split(',').map(Number)
        if (!mode2InitialCandidates[r]) mode2InitialCandidates[r] = {}
        mode2InitialCandidates[r][c] = new Set(data.initial_candidates[key])
    }

    // clear status message
    document.getElementById('mode2-status').textContent = ''

    // reset and start timer
    resetTimer()
    startTimer()

    // build the board UI
    buildMode2Board()
    renderMode2Board()
}


// ── Build the board DOM ───────────────────────────────────────

function buildMode2Board() {
    const table = document.getElementById('sudoku-board-2')
    table.innerHTML = ''  // clear any previous board

    for (let i = 0; i < 9; i++) {
        const row = document.createElement('tr')
        for (let j = 0; j < 9; j++) {
            const cell = document.createElement('td')
            cell.id = `cell2-${i}-${j}`

            // clicking a cell places the selected number (if any)
            cell.addEventListener('mousedown', () => handleMode2CellClick(i, j))

            // keyboard input works too — same arrow key navigation
            cell.tabIndex = 0

            row.appendChild(cell)
        }
        table.appendChild(row)
    }
}


function renderMode2Board() {
    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            const cell = document.getElementById(`cell2-${i}-${j}`)
            const given = mode2Given[i][j]      // original puzzle value (0 if empty)
            const current = mode2Board[i][j]    // what's currently in this cell

            // clear previous content and all highlight classes
            cell.innerHTML = ''
            cell.classList.remove('given-2', 'player-value', 'incorrect', 'hint-highlight', 'selected-2')

            if (given !== 0) {
                // this is a clue cell — show the given number, bold black, not editable
                cell.textContent = given
                cell.classList.add('given-2')
            } else if (current !== 0) {
                // player placed a value here
                cell.textContent = current
                cell.classList.add('player-value')
            } else {
                // empty cell — show pencil marks if any, otherwise show solver candidates
                const key = `${i}-${j}`
                if (mode2UserCandidates[key] && mode2UserCandidates[key].size > 0) {
                    // player has pencil marks for this cell
                    cell.innerHTML = buildCandidateGrid(mode2UserCandidates[key])
                } 
            }
        }
    }
    if (selectedMode2Cell) {
        const [r, c] = selectedMode2Cell
        const cell = document.getElementById(`cell2-${r}-${c}`)
        if (cell) cell.classList.add('selected-2')
    }
}


function handleMode2CellClick(row, col) {
    selectMode2Cell(row, col)
}

function selectMode2Cell(row, col) {
    selectedMode2Cell = [row, col]
    // remove highlight from previously selected cell
    document.querySelectorAll('#sudoku-board-2 td').forEach(td => td.classList.remove('selected-2'))
    // highlight the clicked cell
    document.getElementById(`cell2-${row}-${col}`).classList.add('selected-2')
}

function handleMode2Key(e, row, col) {
    if (e.key >= '1' && e.key <= '9') {
        e.preventDefault()
        if (mode2Given[row][col] !== 0) return
        const num = parseInt(e.key)
        if (inputMode === 'value') {
            mode2Board[row][col] = num
            delete mode2UserCandidates[`${row}-${col}`]
        } else {
            const key = `${row}-${col}`
            if (!mode2UserCandidates[key]) mode2UserCandidates[key] = new Set()
            if (mode2UserCandidates[key].has(num)) {
                mode2UserCandidates[key].delete(num)
            } else {
                mode2UserCandidates[key].add(num)
            }
        }
        renderMode2Board()
        checkComplete()
    } else if (e.key === 'Backspace' || e.key === 'Delete') {
        e.preventDefault()
        if (mode2Given[row][col] !== 0) return
        mode2Board[row][col] = 0
        delete mode2UserCandidates[`${row}-${col}`]
        renderMode2Board()
    } else if (e.key === 'ArrowRight') { e.preventDefault(); selectMode2Cell(row, Math.min(col+1, 8)) }
    else if (e.key === 'ArrowLeft')  { e.preventDefault(); selectMode2Cell(row, Math.max(col-1, 0)) }
    else if (e.key === 'ArrowDown')  { e.preventDefault(); selectMode2Cell(Math.min(row+1, 8), col) }
    else if (e.key === 'ArrowUp')    { e.preventDefault(); selectMode2Cell(Math.max(row-1, 0), col) }
}

function selectNumber(n) {
    if (!selectedMode2Cell) return
    const [row, col] = selectedMode2Cell
    if (mode2Given[row][col] !== 0) return
    if (inputMode === 'value') {
        mode2Board[row][col] = n
        delete mode2UserCandidates[`${row}-${col}`]
    } else {
        const key = `${row}-${col}`
        if (!mode2UserCandidates[key]) mode2UserCandidates[key] = new Set()
        if (mode2UserCandidates[key].has(n)) {
            mode2UserCandidates[key].delete(n)
        } else {
            mode2UserCandidates[key].add(n)
        }
    }
    renderMode2Board()
    checkComplete()
}

function setInputMode(mode) {
    inputMode = mode

    // update the toggle button styles
    document.getElementById('toggle-value').classList.toggle('active', mode === 'value')
    document.getElementById('toggle-candidate').classList.toggle('active', mode === 'candidate')
}

//Mode 2 timer
function startTimer() {
    // clear any existing interval first
    clearInterval(timerInterval)
    timerPaused = false

    // tick every 1000ms (1 second)
    timerInterval = setInterval(() => {
        if (!timerPaused) {
            timerSeconds++
            updateTimerDisplay()
        }
    }, 1000)
}

function resetTimer() {
    clearInterval(timerInterval)
    timerSeconds = 0
    timerPaused = false
    updateTimerDisplay()
}

function updateTimerDisplay() {
    const el = document.getElementById('timer-display')
    if (!el) return
    // format as M:SS
    const mins = Math.floor(timerSeconds / 60)
    const secs = timerSeconds % 60
    // padStart(2, '0') adds a leading zero if secs < 10, so 5 becomes "05"
    document.getElementById('timer-display').textContent = `${mins}:${secs.toString().padStart(2, '0')}`
}

// auto-pause when user leaves the tab
document.addEventListener('visibilitychange', () => {
    const mode2Screen = document.getElementById('mode2-screen')
    const mode2Visible = mode2Screen && !mode2Screen.classList.contains('hidden')
    if (document.hidden && !timerPaused && mode2Board !== null && timerSeconds > 0 && mode2Visible) {
        // tab is hidden and game is active — pause
        pauseGame()
    }
})

document.addEventListener('focusing', (e) => {
    console.log('focus moved to:', e.target.id)
})

document.addEventListener('keydown', (e) => {
    const mode2Screen = document.getElementById('mode2-screen')
    if (mode2Screen.classList.contains('hidden')) return
    if (!selectedMode2Cell) return
    console.log('keydown:', e.key, 'selectedMode2Cell:', selectedMode2Cell)
    const [row, col] = selectedMode2Cell
    handleMode2Key(e, row, col)
})

function pauseGame() {
    console.log('pauseGame called, timerPaused:', timerPaused, 'timerSeconds:', timerSeconds, 'stack:', new Error().stack)
    if (timerPaused) {
        resumeGame()
    } else {
        timerPaused = true
        document.getElementById('pause-overlay').classList.add('visible')
        document.getElementById('btn-pause').textContent = '▶ Resume'
    }
}

function resumeGame() {
    timerPaused = false
    // hide the pause overlay
    document.getElementById('pause-overlay').classList.remove('visible')
    document.getElementById('btn-pause').textContent = '⏸ Pause'
}

//Mode 2 actions
function resetGame() {
    if (!mode2Given) return

    // restore board to the original puzzle — copy given so board is independent
    mode2Board = mode2Given.map(row => [...row])

    // clear all pencil marks
    mode2UserCandidates = {}

    // clear any status messages and highlights
    document.getElementById('mode2-status').textContent = ''

    // reset hint state
    hintLevel = 0
    hintStepIndex = -1

    // reset timer
    resetTimer()
    startTimer()

    renderMode2Board()
}

function checkGame() {
    if (!mode2Board || !mode2Solution) return

    let errors = 0

    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            const cell = document.getElementById(`cell2-${i}-${j}`)
            // only check cells the player filled in (not givens, not empty)
            if (mode2Given[i][j] === 0 && mode2Board[i][j] !== 0) {
                if (mode2Board[i][j] !== mode2Solution[i][j]) {
                    // wrong value — highlight red
                    cell.classList.add('incorrect')
                    errors++
                } else {
                    // correct — remove any incorrect highlight
                    cell.classList.remove('incorrect')
                }
            }
        }
    }

    if (errors === 0) {
        document.getElementById('mode2-status').textContent = 'No errors found!'
    } else {
        document.getElementById('mode2-status').textContent = `${errors} error${errors > 1 ? 's' : ''} found.`
    }
}


function checkComplete() {
    // check if every cell is filled
    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            if (mode2Board[i][j] === 0) return  // still empty cells
        }
    }

    // check if solution matches
    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            if (mode2Board[i][j] !== mode2Solution[i][j]) {
                document.getElementById('mode2-status').textContent = 'Not quite — there are errors.'
                return
            }
        }
    }

    // all correct!
    clearInterval(timerInterval)  // stop the timer
    document.getElementById('mode2-status').textContent = '🎉 Solved!'
}


function hintGame() {
    if (!mode2Steps || mode2Steps.length === 0) return

    // find the next unsolved step — a step whose cell hasn't been filled yet by the player
    if (hintStepIndex === -1) {
        // find the first step that's still relevant
        for (let s = 0; s < mode2Steps.length; s++) {
            const step = mode2Steps[s]
            if (step.value !== 0) {
                // this step places a value — check if it's already placed
                const [r, c] = step.cells[0]
                if (mode2Board[r][c] === 0) {
                    hintStepIndex = s
                    break
                }
            } else {
                // elimination step — always relevant as a hint
                hintStepIndex = s
                break
            }
        }
    }

    if (hintStepIndex === -1) return  // no hint available

    const step = mode2Steps[hintStepIndex]

    if (hintLevel === 0) {
        // first click — highlight the key cells yellow
        clearMode2Highlights()
        for (const [r, c] of step.cells) {
            document.getElementById(`cell2-${r}-${c}`).classList.add('hint-highlight')
        }
        document.getElementById('mode2-status').textContent = 'Hint: look at the highlighted cell(s).'
        hintLevel = 1

    } else if (hintLevel === 1) {
        // second click — show the strategy name
        document.getElementById('mode2-status').textContent = `Hint: try using ${step.strategy}.`
        hintLevel = 2

    } else {
        // third click — do the step for the player
        clearMode2Highlights()
        if (step.value !== 0) {
            // place the value
            const [r, c] = step.cells[0]
            mode2Board[r][c] = step.value
        } else {
            // apply candidate eliminations to user candidates
            for (const [r, c, v] of step.discarded) {
                const key = `${r}-${c}`
                if (mode2UserCandidates[key]) {
                    mode2UserCandidates[key].delete(v)
                }
            }
        }
        renderMode2Board()
        document.getElementById('mode2-status').textContent = `Applied: ${step.strategy}.`
        // reset hint state so next hint finds the next step
        hintLevel = 0
        hintStepIndex = -1
        checkComplete()
    }
}

function clearMode2Highlights() {
    // removes hint and incorrect highlights from all cells
    document.querySelectorAll('#sudoku-board-2 td').forEach(td => {
        td.classList.remove('hint-highlight', 'incorrect')
    })
}

function solveGame() {
    if (!mode2Solution) return
    
    // fill the board with the solution
    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            mode2Board[i][j] = mode2Solution[i][j]
        }
    }
    
    clearInterval(timerInterval)
    clearMode2Highlights()
    renderMode2Board()
    document.getElementById('mode2-status').textContent = 'Solved!'
}