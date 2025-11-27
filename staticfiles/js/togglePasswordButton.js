const inputElements = document.querySelectorAll('input[type="password"]');
const inputElement = inputElements.length > 0 ? inputElements[0] : null;
const toggleBtn = document.getElementById('toggle');

const forms = document.getElementsByTagName('form');
const form = forms.length > 0 ? forms[0] : null;

const hidePassword = () => {
    if (inputElement) {
        inputElement.type = "password";
        toggleBtn.className = "bi bi-eye-fill toggle-btn";
    }
};

if (inputElement && toggleBtn) {

    toggleBtn.addEventListener('mousedown', () => {
        inputElement.type = 'text';
        toggleBtn.className = 'bi bi-eye-slash-fill toggle-btn';
    });
    toggleBtn.addEventListener('mouseup', hidePassword);
    toggleBtn.addEventListener('mouseleave', hidePassword);

    toggleBtn.addEventListener('touchstart', (e) => {
        e.preventDefault();
        inputElement.type = 'text';
        toggleBtn.className = 'bi bi-eye-slash-fill toggle-btn';
    });

    toggleBtn.addEventListener('touchend', hidePassword);
    toggleBtn.addEventListener('touchcancel', hidePassword);
}

if (form) {
    form.addEventListener('submit', hidePassword);
}