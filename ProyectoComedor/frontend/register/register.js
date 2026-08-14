const paso1 = document.getElementById('contenedor-paso1');
const paso2 = document.getElementById('contenedor-paso2');
const btnSiguiente = document.getElementById('btn-siguiente');
const btnVolver = document.getElementById('btn-volver');

btnSiguiente.addEventListener('click', () => {
    const camposPaso1 = paso1.querySelectorAll('input, select');
    let esValido = true;

    for (let campo of camposPaso1) {
        if (!campo.checkValidity()) {
            campo.reportValidity();
            esValido = false;
            break;
        }
    }

    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('password_confirmation').value;
    if (esValido && password !== confirmPassword) {
        alert('Las contraseñas no coinciden.');
        document.getElementById('password_confirmation').focus();
        esValido = false;
    }

    if (esValido) {
        paso1.style.display = 'none';
        paso2.style.display = 'block';
    }
});

btnVolver.addEventListener('click', () => {
    paso2.style.display = 'none';
    paso1.style.display = 'block';
});