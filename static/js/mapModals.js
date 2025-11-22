const overlay = document.querySelector('.modal-overlay');
const addModal = document.getElementById('add-beach-modal');
const logModal = document.getElementById('log-beach-modal');
const reportModal = document.getElementById('report-beach-modal');

function hideAllModals() {
    document.querySelectorAll('.modal').forEach(m => m.style.display = 'none');
    if (overlay) overlay.style.display = 'none';
}

function openAddModal() {
    hideAllModals();
    addModal.style.display = 'flex';
    overlay.style.display = 'flex';
}

function openLogsModal(beachId = null) {
    hideAllModals();
    if (beachId && logModal) {
        const beachInput = logModal.querySelector('input[name="beach"]');
        if (beachInput) beachInput.value = beachId;
    }
    logModal.style.display = 'flex';
    overlay.style.display = 'flex';
}

function openReportModal() {
    hideAllModals();
    reportModal.style.display = 'flex';
    overlay.style.display = 'flex';
}

function closeAddModal() {
    addModal.style.display = 'none';
    overlay.style.display = 'none';
}

function closeLogsModal() {
    logModal.style.display = 'none';
    overlay.style.display = 'none';
}

function closeReportModal() {
    reportModal.style.display = 'none';
    overlay.style.display = 'none';
}

if (overlay) {
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) hideAllModals();
    });
}

window.openAddModal = openAddModal;
window.openLogsModal = openLogsModal;
window.openReportModal = openReportModal;
window.closeAddModal = closeAddModal;
window.closeLogsModal = closeLogsModal;
window.closeReportModal = closeReportModal;