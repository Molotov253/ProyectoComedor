document.addEventListener('DOMContentLoaded', () => {
    const pasoCorreo = document.getElementById('contenedor-correo');
    const pasoPregunta = document.getElementById('contenedor-pregunta');
    const pasoPassword = document.getElementById('contenedor-password');

    const btnBuscarCorreo = document.getElementById('btn-buscar-correo');
    const btnVolverCorreo = document.getElementById('btn-volver-correo');
    const btnValidarRespuesta = document.getElementById('btn-validar-respuesta');
    const formRecuperar = document.getElementById('form-recuperar');

    btnBuscarCorreo.addEventListener('click', () => {
        const emailInput = document.getElementById('email');
        if (!emailInput.checkValidity()) {
            emailInput.reportValidity();
            return;
        }
        pasoCorreo.style.display = 'none';
        pasoPregunta.style.display = 'block';
    });

    btnVolverCorreo.addEventListener('click', () => {
        pasoPregunta.style.display = 'none';
        pasoCorreo.style.display = 'block';
    });

    btnValidarRespuesta.addEventListener('click', () => {
        const respuestaInput = document.getElementById('respuesta_seguridad');
        if (!respuestaInput.checkValidity()) {
            respuestaInput.reportValidity();
            return;
        }

        pasoPregunta.style.display = 'none';
        pasoPassword.style.display = 'block';
    });

    formRecuperar.addEventListener('submit', (e) => {
        const newPass = document.getElementById('new_password').value;
        const confirmPass = document.getElementById('new_password_confirmation').value;

        if (newPass !== confirmPass) {
            e.preventDefault();
            alert('Las contraseñas no coinciden.');
            document.getElementById('new_password_confirmation').focus();
        }
    });
});
