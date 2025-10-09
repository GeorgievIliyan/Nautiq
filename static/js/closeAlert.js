document.addEventListener('DOMContentLoaded', function() {
    const closeButtons = document.querySelectorAll('.alert-close');

    closeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const alert = this.parentElement;
            
            alert.style.transition = 'opacity 0.3s ease';
            alert.style.opacity = '0';
            alert.style.height = '0';
            
            setTimeout(() => alert.remove(), 300);
        });
    });
});