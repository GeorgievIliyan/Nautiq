let popupAlertContainer = document.getElementById('popup-alert-container');
if (!popupAlertContainer) {
    popupAlertContainer = document.createElement('div');
    popupAlertContainer.id = 'popup-alert-container';
    document.body.appendChild(popupAlertContainer);
}

/**
 * @param {string} message - Text of the alert
 * @param {'danger'|'success'} type - Type of alert
 * @param {number} timeout - Time in ms before disappearing
 */
function showPopupAlert(message, type = 'danger', timeout = 10000) {
    const alertDiv = document.createElement('div');
    alertDiv.classList.add(`popup-alert-${type}`);

    const icon = document.createElement('i');
    icon.classList.add('bi', type === 'danger' ? 'bi-exclamation-octagon' : 'bi-check-lg');
    alertDiv.appendChild(icon);

    const textSpan = document.createElement('div');
    textSpan.textContent = message;
    alertDiv.appendChild(textSpan);

    // Close button
    const closeBtn = document.createElement('i');
    closeBtn.classList.add('bi', 'bi-x-lg', 'alert-close');
    closeBtn.addEventListener('click', () => alertDiv.remove());
    alertDiv.appendChild(closeBtn);

    popupAlertContainer.appendChild(alertDiv);

    requestAnimationFrame(() => alertDiv.classList.add('show'));

    if (timeout > 0) {
        setTimeout(() => {
            alertDiv.classList.remove('show');
            alertDiv.addEventListener(
                'transitionend',
                () => alertDiv.remove(),
                { once: true }
            );
        }, timeout);
    }
}