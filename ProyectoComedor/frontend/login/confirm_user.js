document.addEventListener('DOMContentLoaded', () => {
    const rawData = sessionStorage.getItem('temp_auth');
    if (!rawData) {
        window.location.href = 'login.html';
        return;
    }

    const authData = JSON.parse(rawData);
    const preguntaTextoElem = document.getElementById('pregunta-texto');
    const formConfirm = document.getElementById('form-confirm');
    const btnConfirmar = document.getElementById('btn-confirmar');
    const btnCancelar = document.getElementById('btn-cancelar');
    const alertBox = document.getElementById('alert-box');

    preguntaTextoElem.textContent = authData.pregunta_texto || '¿Pregunta de seguridad?';

    function showAlert(message, type = 'danger') {
        alertBox.className = `alert alert-${type}`;
        alertBox.textContent = message;
        alertBox.style.display = 'flex';
    }

    function hideAlert() {
        alertBox.style.display = 'none';
        alertBox.textContent = '';
    }

    btnCancelar.addEventListener('click', () => {
        sessionStorage.removeItem('temp_auth');
        window.location.href = 'login.html';
    });

    formConfirm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideAlert();

        const respuesta = document.getElementById('respuesta_seguridad').value.trim();
        if (!respuesta) {
            showAlert('Por favor escribe tu respuesta.');
            return;
        }

        btnConfirmar.disabled = true;
        btnConfirmar.textContent = 'Verificando...';

        try {
            const res = await fetch('/api/auth/login-security-check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: authData.email,
                    temp_token: authData.temp_token,
                    clave_pregunta: authData.pregunta_clave,
                    respuesta: respuesta
                })
            });

            const data = await res.json();

            if (!res.ok) {
                showAlert(data.detail || 'Respuesta de seguridad incorrecta.');
                btnConfirmar.disabled = false;
                btnConfirmar.textContent = 'Confirmar y Acceder';
                return;
            }

            // Guardar token y usuario
            localStorage.setItem('auth_token', data.token);
            localStorage.setItem('auth_user', JSON.stringify(data.user));
            sessionStorage.removeItem('temp_auth');

            showAlert('¡Autenticación exitosa! Accediendo al sistema...', 'success');
            setTimeout(() => {
                window.location.href = '../index/index.html';
            }, 1000);

        } catch (err) {
            showAlert('Error de conexión con el servidor Python.');
            btnConfirmar.disabled = false;
            btnConfirmar.textContent = 'Confirmar y Acceder';
        }
    });
});
