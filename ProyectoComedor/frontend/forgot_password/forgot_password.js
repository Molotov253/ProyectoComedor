document.addEventListener('DOMContentLoaded', () => {
    const pasoCorreo = document.getElementById('contenedor-correo');
    const pasoPregunta = document.getElementById('contenedor-pregunta');
    const pasoPassword = document.getElementById('contenedor-password');

    const btnBuscarCorreo = document.getElementById('btn-buscar-correo');
    const btnVolverCorreo = document.getElementById('btn-volver-correo');
    const btnValidarRespuesta = document.getElementById('btn-validar-respuesta');
    const btnActualizarPass = document.getElementById('btn-actualizar-pass');
    const formRecuperar = document.getElementById('form-recuperar');
    const alertBox = document.getElementById('alert-box');

    const stepInd1 = document.getElementById('step-ind-1');
    const stepInd2 = document.getElementById('step-ind-2');
    const stepInd3 = document.getElementById('step-ind-3');
    const stepDiv1 = document.getElementById('step-divider-1');
    const stepDiv2 = document.getElementById('step-divider-2');

    let currentEmail = '';
    let currentTempToken = '';
    let currentQuestionKey = '';
    let currentResetToken = '';

    function showAlert(message, type = 'danger') {
        alertBox.className = `alert alert-${type}`;
        alertBox.textContent = message;
        alertBox.style.display = 'flex';
    }

    function hideAlert() {
        alertBox.style.display = 'none';
        alertBox.textContent = '';
    }

    // Paso 1: Buscar correo y obtener pregunta de seguridad
    btnBuscarCorreo.addEventListener('click', async () => {
        hideAlert();
        const emailInput = document.getElementById('email');
        const email = emailInput.value.trim();

        if (!email || !emailInput.checkValidity()) {
            showAlert('Por favor ingresa un correo electrónico válido.');
            emailInput.focus();
            return;
        }

        btnBuscarCorreo.disabled = true;
        btnBuscarCorreo.textContent = 'Buscando cuenta...';

        try {
            const res = await fetch('/api/auth/forgot-password/init', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });

            const data = await res.json();

            if (!res.ok) {
                showAlert(data.detail || 'No se encontró una cuenta con ese correo.');
                btnBuscarCorreo.disabled = false;
                btnBuscarCorreo.textContent = 'Buscar Cuenta →';
                return;
            }

            currentEmail = data.email;
            currentTempToken = data.temp_token;
            currentQuestionKey = data.pregunta_clave;

            document.getElementById('label-pregunta').textContent = data.pregunta_texto;

            pasoCorreo.style.display = 'none';
            pasoPregunta.style.display = 'block';

            stepInd1.classList.remove('active');
            stepInd2.classList.add('active');
            stepDiv1.classList.add('active');

            btnBuscarCorreo.disabled = false;
            btnBuscarCorreo.textContent = 'Buscar Cuenta →';
        } catch (err) {
            showAlert('Error de conexión con el servidor Python.');
            btnBuscarCorreo.disabled = false;
            btnBuscarCorreo.textContent = 'Buscar Cuenta →';
        }
    });

    // Volver de paso 2 a paso 1
    btnVolverCorreo.addEventListener('click', () => {
        hideAlert();
        pasoPregunta.style.display = 'none';
        pasoCorreo.style.display = 'block';

        stepInd2.classList.remove('active');
        stepInd1.classList.add('active');
        stepDiv1.classList.remove('active');
    });

    // Paso 2: Validar respuesta de seguridad
    btnValidarRespuesta.addEventListener('click', async () => {
        hideAlert();
        const respuestaInput = document.getElementById('respuesta_seguridad');
        const respuesta = respuestaInput.value.trim();

        if (!respuesta) {
            showAlert('Por favor ingresa tu respuesta.');
            respuestaInput.focus();
            return;
        }

        btnValidarRespuesta.disabled = true;
        btnValidarRespuesta.textContent = 'Validando...';

        try {
            const res = await fetch('/api/auth/forgot-password/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: currentEmail,
                    temp_token: currentTempToken,
                    clave_pregunta: currentQuestionKey,
                    respuesta: respuesta
                })
            });

            const data = await res.json();

            if (!res.ok) {
                showAlert(data.detail || 'Respuesta de seguridad incorrecta.');
                btnValidarRespuesta.disabled = false;
                btnValidarRespuesta.textContent = 'Validar Respuesta →';
                return;
            }

            currentResetToken = data.reset_token;

            pasoPregunta.style.display = 'none';
            pasoPassword.style.display = 'block';

            stepInd2.classList.remove('active');
            stepInd3.classList.add('active');
            stepDiv2.classList.add('active');

            btnValidarRespuesta.disabled = false;
            btnValidarRespuesta.textContent = 'Validar Respuesta →';
        } catch (err) {
            showAlert('Error de conexión con el servidor Python.');
            btnValidarRespuesta.disabled = false;
            btnValidarRespuesta.textContent = 'Validar Respuesta →';
        }
    });

    // Paso 3: Actualizar contraseña
    formRecuperar.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideAlert();

        const newPass = document.getElementById('new_password').value;
        const confirmPass = document.getElementById('new_password_confirmation').value;

        if (newPass.length < 6) {
            showAlert('La nueva contraseña debe tener al menos 6 caracteres.');
            document.getElementById('new_password').focus();
            return;
        }

        if (newPass !== confirmPass) {
            showAlert('Las contraseñas no coinciden.');
            document.getElementById('new_password_confirmation').focus();
            return;
        }

        btnActualizarPass.disabled = true;
        btnActualizarPass.textContent = 'Actualizando contraseña...';

        try {
            const res = await fetch('/api/auth/forgot-password/reset', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: currentEmail,
                    reset_token: currentResetToken,
                    new_password: newPass,
                    new_password_confirmation: confirmPass
                })
            });

            const data = await res.json();

            if (!res.ok) {
                showAlert(data.detail || 'Error al restablecer la contraseña.');
                btnActualizarPass.disabled = false;
                btnActualizarPass.textContent = 'Actualizar Contraseña';
                return;
            }

            showAlert('¡Contraseña actualizada con éxito! Redirigiendo al login...', 'success');
            setTimeout(() => {
                window.location.href = '../login/login.html';
            }, 1800);

        } catch (err) {
            showAlert('Error de conexión con el servidor.');
            btnActualizarPass.disabled = false;
            btnActualizarPass.textContent = 'Actualizar Contraseña';
        }
    });
});
