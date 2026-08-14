document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-login');
    const btnLogin = document.getElementById('btn-login');
    const alertBox = document.getElementById('alert-box');

    function showAlert(message, type = 'danger') {
        alertBox.className = `alert alert-${type}`;
        alertBox.textContent = message;
        alertBox.style.display = 'flex';
    }

    function hideAlert() {
        alertBox.style.display = 'none';
        alertBox.textContent = '';
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideAlert();

        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;

        if (!email || !password) {
            showAlert('Por favor ingresa tu correo y contraseña.');
            return;
        }

        btnLogin.disabled = true;
        btnLogin.textContent = 'Verificando...';

        try {
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await res.json();

            if (!res.ok) {
                showAlert(data.detail || 'Credenciales incorrectas.');
                btnLogin.disabled = false;
                btnLogin.textContent = 'Continuar al Paso 2 →';
                return;
            }

            if (data.status === 'requires_security_check') {
                // Guardar datos temporales para el desafío de seguridad
                sessionStorage.setItem('temp_auth', JSON.stringify({
                    email: data.email,
                    temp_token: data.temp_token,
                    pregunta_clave: data.pregunta_clave,
                    pregunta_texto: data.pregunta_texto
                }));

                window.location.href = 'confirm_user.html';
            } else {
                showAlert('Respuesta inesperada del servidor.');
                btnLogin.disabled = false;
                btnLogin.textContent = 'Continuar al Paso 2 →';
            }

        } catch (err) {
            showAlert('Error de conexión con el servidor Python.');
            btnLogin.disabled = false;
            btnLogin.textContent = 'Continuar al Paso 2 →';
        }
    });
});
