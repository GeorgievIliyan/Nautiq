const nav = document.querySelector('nav');
const items = Array.from(document.querySelectorAll('nav ul li'));

let indicator = document.querySelector('.nav-indicator');
if (!indicator) {
    indicator = document.createElement('div');
    indicator.className = 'nav-indicator';
    nav.appendChild(indicator);
}

function moveIndicatorToElement(el) {
    if (window.matchMedia('(min-width: 601px)').matches) {
        indicator.style.display = 'block';
        const elRect = el.getBoundingClientRect();
        const navRect = nav.getBoundingClientRect();
        const left = elRect.left - navRect.left + nav.scrollLeft;
        const top  = elRect.top - navRect.top + nav.scrollTop;
        const width = elRect.width;
        const height = elRect.height;
        indicator.style.left = left + 'px';
        indicator.style.top = top + 'px';
        indicator.style.width = width + 'px';
        indicator.style.height = height + 'px';
    } else {
        indicator.style.display = 'none';
    }
}

function initIndicator() {
    const active = document.querySelector('nav ul li.active') || items[0];
    moveIndicatorToElement(active);
}

// Click event for desktop
items.forEach(item => {
    item.addEventListener('click', (e) => {
        if (window.matchMedia('(min-width: 601px)').matches) {
            e.preventDefault(); 
        }
        const current = document.querySelector('nav ul li.active');
        if (current) current.classList.remove('active');
        item.classList.add('active');
        moveIndicatorToElement(item);

        if (window.matchMedia('(min-width: 601px)').matches) {
            setTimeout(() => {
                const link = item.querySelector('a');
                if (link) window.location.href = link.href;
            }, 300);
        }
    });
});

window.addEventListener('resize', initIndicator);
document.addEventListener('DOMContentLoaded', initIndicator);