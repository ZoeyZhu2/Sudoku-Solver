console.log('script loaded')

let selectedCell = null
let steps = []
let givenCells = new Set()
let initialCandidates = null
let originalBoard = null
let solvedBoard = null
let currentStep = -1  // -1 = showing original
let boardLocked = false

function showScreen(screenId) {
    document.querySelectorAll('#app > div').forEach(div => {
        div.classList.add('hidden')
    })
    document.getElementById(screenId).classList.remove('hidden')
    if (screenId === 'mode1-screen') buildBoard()
}

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
    console.log('initial_candidates:', data.initial_candidates)
    console.log('initialCandidates after init:', initialCandidates)

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
            if (i === 0 && j === 2) console.log('cell 0,2 cands:', cellCands, 'cands[0]:', cands[0], 'cands[0][2]:', cands[0]?.[2])            
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