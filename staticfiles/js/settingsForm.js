const form = document.getElementById('settings-form')
const closeBtn = document.getElementById('close-settings-form')

const openSettingsForm = () => {
    form.style.display = 'flex'
}

const closeSettingsForm = () => {
    form.style.display = 'none'
}