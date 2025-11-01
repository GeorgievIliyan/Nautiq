const nav = document.querySelector('nav');
const items = Array.from(document.querySelectorAll('nav ul li'));

let indicator = document.querySelector('.nav-indicator');
if (!indicator) {
    indicator = document.createElement('div');
    indicator.className = 'nav-indicator';
    nav.appendChild(indicator);
}

function setIndicatorRect(x, y, w, h) {
    indicator.style.left = x + 'px';
    indicator.style.top  = y + 'px';
    indicator.style.width = w + 'px';
    indicator.style.height = h + 'px';
}

function moveIndicatorToElement(el) {
    const elRect = el.getBoundingClientRect();
    const navRect = nav.getBoundingClientRect();

    const left = (elRect.left - navRect.left) + nav.scrollLeft;
    const top  = (elRect.top  - navRect.top)  + nav.scrollTop;

    const x = Math.round(left);
    const y = Math.round(top);
    const w = Math.round(elRect.width);
    const h = Math.round(elRect.height);

    setIndicatorRect(x, y, w, h);
}

function initIndicator() {
    const initial = document.querySelector('nav ul li.active') || items[0];
    moveIndicatorToElement(initial);
}

items.forEach(item => {
    item.addEventListener('click', (e) => {
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

window.addEventListener('load', () => {
    setTimeout(initIndicator, 10);
});

document.addEventListener('DOMContentLoaded', initIndicator);