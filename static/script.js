let selectedCell = null
let steps = []
let currentStep = 0
let givenCells = new Set()

function showScreen(screenId) {
    document.querySelectorAll('#app > div').forEach(div => {
        div.classList.add('hidden')
    })
    document.getElementById(screenId).classList.remove('hidden')
    if (screenId === 'mode1-screen') buildBoard()
}

function buildBoard() {
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
    if (e.key >= '1' && e.key <= '9') {
        e.preventDefault()
        const cell = document.getElementById(`cell-${row}-${col}`)
        cell.textContent = e.key
        cell.classList.add('given')
        givenCells.add(`${row}-${col}`)
    }
    else if (e.key === 'Backspace' || e.key === 'Delete') {
        e.preventDefault()
        const cell = document.getElementById(`cell-${row}-${col}`)
        cell.textContent = ''
        cell.classList.remove('given')
        givenCells.delete(`${row}-${col}`)
    }
    else if (e.key === 'ArrowRight') { e.preventDefault(); selectCell(row, Math.min(col+1, 8)) }
    else if (e.key === 'ArrowLeft')  { e.preventDefault(); selectCell(row, Math.max(col-1, 0)) }
    else if (e.key === 'ArrowDown')  { e.preventDefault(); selectCell(Math.min(row+1, 8), col) }
    else if (e.key === 'ArrowUp')    { e.preventDefault(); selectCell(Math.max(row-1, 0), col) }
    else e.preventDefault()
}