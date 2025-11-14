document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.alert-close').forEach(btn => {
        btn.addEventListener('click', function() {
            const alert = this.closest('.alert-danger, .alert-success');

            alert.classList.add('fade-out');

            void alert.offsetWidth; 

            alert.addEventListener('transitionend', () => alert.remove(), { once: true });
        });
    });
});