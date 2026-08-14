document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-registro');
    const paso1 = document.getElementById('contenedor-paso1');
    const paso2 = document.getElementById('contenedor-paso2');
    const btnSiguiente = document.getElementById('btn-siguiente');
    const btnVolver = document.getElementById('btn-volver');
    const btnSubmit = document.getElementById('btn-submit');
    const stepInd1 = document.getElementById('step-ind-1');
    const stepInd2 = document.getElementById('step-ind-2');
    const stepDivider = document.getElementById('step-divider');
    const alertBox = document.getElementById('alert-box');
    const questionsContainer = document.getElementById('questions-container');

    let availableQuestions = [];

    function showAlert(message, type = 'danger') {
        alertBox.className = `alert alert-${type}`;
        alertBox.textContent = message;
        alertBox.style.display = 'flex';
        alertBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function hideAlert() {
        alertBox.style.display = 'none';
        alertBox.textContent = '';
    }

    // Cargar preguntas desde la API de Python
    async function loadSecurityQuestions() {
        try {
            const res = await fetch('/api/auth/questions');
            if (!res.ok) throw new Error('Error al obtener preguntas.');
            availableQuestions = await res.json();
            renderQuestionSelects();
        } catch (err) {
            questionsContainer.innerHTML = `<p style="color: var(--danger);">No se pudieron cargar las preguntas del servidor.</p>`;
        }
    }

    function renderQuestionSelects() {
        questionsContainer.innerHTML = '';
        for (let i = 1; i <= 3; i++) {
            const box = document.createElement('div');
            box.className = 'question-box';

            let optionsHtml = `<option value="" disabled selected>Selecciona la pregunta #${i}</option>`;
            availableQuestions.forEach(q => {
                optionsHtml += `<option value="${q.clave}">${q.texto}</option>`;
            });

            box.innerHTML = `
                <div class="question-box-title">
                    <span>Pregunta de Seguridad #${i}</span>
                </div>
                <div class="form-group">
                    <select id="pregunta_${i}" name="pregunta_${i}" required>
                        ${optionsHtml}
                    </select>
                </div>
                <div class="form-group" style="margin-bottom: 0;">
                    <label for="respuesta_${i}">Tu Respuesta <span class="required">*</span></label>
                    <input type="text" id="respuesta_${i}" name="respuesta_${i}" placeholder="Escribe tu respuesta aquí" required>
                </div>
            `;
            questionsContainer.appendChild(box);
        }
    }

    loadSecurityQuestions();

    btnSiguiente.addEventListener('click', () => {
        hideAlert();
        const camposPaso1 = paso1.querySelectorAll('input, select');
        let esValido = true;

        for (let campo of camposPaso1) {
            if (!campo.checkValidity()) {
                campo.reportValidity();
                esValido = false;
                break;
            }
        }

        if (!esValido) return;

        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('password_confirmation').value;
        
        if (password.length < 6) {
            showAlert('La contraseña debe tener al menos 6 caracteres.');
            document.getElementById('password').focus();
            return;
        }

        if (password !== confirmPassword) {
            showAlert('Las contraseñas no coinciden.');
            document.getElementById('password_confirmation').focus();
            return;
        }

        paso1.style.display = 'none';
        paso2.style.display = 'block';
        stepInd1.classList.remove('active');
        stepInd2.classList.add('active');
        stepDivider.classList.add('active');
    });

    btnVolver.addEventListener('click', () => {
        hideAlert();
        paso2.style.display = 'none';
        paso1.style.display = 'block';
        stepInd2.classList.remove('active');
        stepInd1.classList.add('active');
        stepDivider.classList.remove('active');
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideAlert();

        const p1 = document.getElementById('pregunta_1').value;
        const r1 = document.getElementById('respuesta_1').value;
        const p2 = document.getElementById('pregunta_2').value;
        const r2 = document.getElementById('respuesta_2').value;
        const p3 = document.getElementById('pregunta_3').value;
        const r3 = document.getElementById('respuesta_3').value;

        if (!p1 || !p2 || !p3 || !r1.trim() || !r2.trim() || !r3.trim()) {
            showAlert('Por favor completa las 3 preguntas de seguridad y sus respuestas.');
            return;
        }

        const selectedSet = new Set([p1, p2, p3]);
        if (selectedSet.size < 3) {
            showAlert('Debes seleccionar 3 preguntas diferentes.');
            return;
        }

        const payload = {
            nombre: document.getElementById('nombre').value.trim(),
            apellido: document.getElementById('apellido').value.trim(),
            ocupacion: document.getElementById('ocupacion').value,
            email: document.getElementById('email').value.trim(),
            password: document.getElementById('password').value,
            password_confirmation: document.getElementById('password_confirmation').value,
            genero: document.getElementById('genero').value,
            preguntas: [
                { clave: p1, respuesta: r1.trim() },
                { clave: p2, respuesta: r2.trim() },
                { clave: p3, respuesta: r3.trim() }
            ]
        };

        btnSubmit.disabled = true;
        btnSubmit.textContent = 'Registrando...';

        try {
            const res = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();

            if (!res.ok) {
                showAlert(data.detail || 'Ocurrió un error al registrar el usuario.');
                btnSubmit.disabled = false;
                btnSubmit.textContent = 'Finalizar Registro';
                return;
            }

            showAlert('¡Registro completado con éxito! Redirigiendo al inicio de sesión...', 'success');
            setTimeout(() => {
                window.location.href = '../login/login.html';
            }, 1800);

        } catch (err) {
            showAlert('Error de conexión con el servidor Python.');
            btnSubmit.disabled = false;
            btnSubmit.textContent = 'Finalizar Registro';
        }
    });
});