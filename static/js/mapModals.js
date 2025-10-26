const add_modal = document.getElementById('add-beach-modal');

window.openAddModal = () => {
    closeAllModals();
    console.log('Add modal opened!')
    add_modal.style.display = 'flex';
}

window.closeAddModal = () => {
    add_modal.style.display = 'none';
}
const all_modals = document.getElementsByClassName('modal')
const logs_modal = document.getElementById('log-beach-modal')

const closeAllModals = () => {
    for (let m of all_modals) {
        m.style.display = 'none'
    }
}

window.openLogsModal = () => {
    closeAllModals()
    logs_modal.style.display = 'flex'
}

window.closeLogsModal = () => {
    logs_modal.style.display = 'none'
}