const nav = document.querySelector('nav');
const items = Array.from(document.querySelectorAll('nav ul li'));

let indicator = document.querySelector('.nav-indicator');
if (!indicator) {
    indicator = document.createElement('div');
    indicator.className = 'nav-indicator';
    nav.appendChild(indicator);
}

indicator.style.position = 'absolute';
indicator.style.borderRadius = '10px';
indicator.style.zIndex = '0';
indicator.style.transition = 'left 0.28s cubic-bezier(.2,.9,.3,1), top 0.28s cubic-bezier(.2,.9,.3,1), width 0.28s cubic-bezier(.2,.9,.3,1), height 0.28s cubic-bezier(.2,.9,.3,1)';
indicator.style.pointerEvents = 'none';
indicator.style.backgroundColor = window.matchMedia('(prefers-color-scheme: dark)').matches ? '#1C1C1E' : '#FBFBFB';

function moveIndicatorToElement(el) {
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
}

function initIndicator() {
    const active = document.querySelector('nav ul li.active') || items[0];
    moveIndicatorToElement(active);
}

items.forEach(item => {
    item.addEventListener('click', () => {
        const current = document.querySelector('nav ul li.active');
        if (current) current.classList.remove('active');
        item.classList.add('active');
        moveIndicatorToElement(item);
    });
});

window.addEventListener('resize', () => {
    const active = document.querySelector('nav ul li.active') || items[0];
    moveIndicatorToElement(active);
});

document.addEventListener('DOMContentLoaded', initIndicator);