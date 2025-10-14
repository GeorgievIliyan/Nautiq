class SeaSightSidebar extends HTMLElement {
    constructor() {
        super();
        const shadow = this.attachShadow({ mode: 'open' });

        const username = this.getAttribute('data-username') || 'Guest';
        const level = this.getAttribute('data-level') || 'Level 1';
        const pfp = this.getAttribute('data-pfp') || 
            'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQwAAAC8CAMAAAC672BgAAAAA1BMVEWxrq37BefPAAAARklEQVR4nO3BAQEAAACAkP6v7ggKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoAbFjAAB3KzK6gAAAABJRU5ErkJggg==';

        const dashboardURL = this.getAttribute('dashboard-url') || '#';
        const mapURL = this.getAttribute('map-url') || '#';
        const logsURL = this.getAttribute('logs-url') || '#';
        const accountURL = this.getAttribute('account-url') || '#';
        const logoutURL = this.getAttribute('logout-url') || '#';
        const settingsURL = this.getAttribute('settings-url') || '#';
        const termsURL = this.getAttribute('terms-url') || '#';


        const wrapper = document.createElement('aside');
        wrapper.innerHTML = `
            <nav>
                <div class="account-wrapper">
                    <img src="${pfp}" class="user-pfp" alt="User profile picture">
                    <div class="account-info">
                        <span class="user-username">${username}</span>
                        <span class="user-level">${level}</span>
                    </div>
                </div>

                <section>
                    <div>
                        <div class="navbar-seperator"></div>
                        <h6>Приложение</h6>
                    </div>
                    <ul>
                        <li><a href="${dashboardURL}"><i class="bi bi-grid-1x2"></i> Табло</a></li>
                        <li><a href="${mapURL}"><i class="bi bi-compass"></i> Карта</a></li>
                        <li><a href="${logsURL}"><i class="bi bi-journal"></i> Доклади</a></li>
                    </ul>
                </section>

                <section>
                    <div>
                        <div class="navbar-seperator"></div>
                        <h6>Акаунт</h6>
                    </div>
                    <ul>
                        <li><a href="${accountURL}"><i class="bi bi-person"></i> Акаунт</a></li>
                        <li><a href="${logoutURL}"><i class="bi bi-box-arrow-right"></i> Излез</a></li>
                    </ul>
                </section>

                <section>
                    <div>
                        <div class="navbar-seperator"></div>
                        <h6>Други</h6>
                    </div>
                    <ul>
                        <li><a href="${settingsURL}"><i class="bi bi-gear"></i> Настройки</a></li>
                        <li><a href="${termsURL}"><i class="bi bi-text-left"></i> Условия</a></li>
                    </ul>
                </section>
            </nav>
        `;

        const icons = document.createElement('link');
        icons.rel = 'stylesheet';
        icons.href = 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.min.css';

        const style = document.createElement('style');
        style.textContent = `
            @import url('https://fonts.googleapis.com/css?family=Onest:100,200,300,regular,500,600,700,800,900');

            * {
                padding: 0;
                margin: 0;
                box-sizing: border-box;
                font-family: "Onest", sans-serif;
            }

            aside {
                padding: 36px;
                width: fit-content;
                min-width: 20vw;
                height: 100vh;
                background-color: #F8F8F8;
                border-right: 1px solid #d7d7d7;
            }

            .account-wrapper {
                margin-bottom: 32px;
                display: flex;
                flex-direction: row;
                align-items: center;
                gap: 12px;
            }

            .user-pfp {
                aspect-ratio: 1/1;
                width: 56px;
                border-radius: 10px;
                object-fit: cover;
            }

            .account-info {
                display: flex;
                flex-direction: column;
                gap: 0px;
            }

            .user-username {
                font-weight: 600;
                font-size: 24px;
                color: #222222;
            }

            .user-level {
                font-size: 14px;
                font-weight: 200;
            }

            nav section {
                display: flex;
                flex-direction: column;
                gap: 16px;
                margin-bottom: 32px;
            }

            nav h6 {
                color: #939393;
                font-size: 12px;
                font-weight: 400;
                letter-spacing: 0.25px;
            }

            .navbar-seperator {
                background-color: #D9D9D9;
                height: 1px;
                width: 100%;
                margin-bottom: 8px;
            }

            nav ul {
                display: flex;
                flex-direction: column;
                list-style: none;
                gap: 16px;
                transform: translateX(3px);
            }

            nav ul li a {
                color: #222222;
                text-decoration: none;
                font-size: 20px;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            nav ul li a i {
                font-size: 20px;
                color: #048FE6;
            }

            .bi-person {
                font-size: 22px;
            }

            .bi-box-arrow-right {
                color: #E63946;
            }
        `;

        shadow.appendChild(icons);
        shadow.appendChild(style);
        shadow.appendChild(wrapper);
    }
}

customElements.define('sea-sight-sidebar', SeaSightSidebar);