document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('auth_token');

    if (!token) {
        window.location.href = '../login/login.html';
        return;
    }

    try {
        const res = await fetch('/api/auth/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!res.ok) {
            localStorage.removeItem('auth_token');
            localStorage.removeItem('auth_user');
            window.location.href = '../login/login.html';
            return;
        }

        const data = await res.json();
        const user = data.user;

        // Mostrar datos en interfaz
        document.getElementById('user-display-name').textContent = `${user.nombre} ${user.apellido}`;
        document.getElementById('welcome-name').textContent = `${user.nombre}`;

        const roleElem = document.getElementById('user-display-role');
        roleElem.textContent = user.ocupacion.toUpperCase();
        roleElem.className = `role-pill role-${user.ocupacion.toLowerCase()}`;

        renderRoleSpecificPanel(user);

    } catch (err) {
        console.error('Error al validar sesión:', err);
    }

    // Botón de cerrar sesión
    const btnLogout = document.getElementById('btn-logout');
    btnLogout.addEventListener('click', async () => {
        try {
            await fetch('/api/auth/logout', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
        } catch (e) {
            // Continuar cierre local
        }
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
        window.location.href = '../login/login.html';
    });

    function renderRoleSpecificPanel(user) {
        const panelTitle = document.getElementById('panel-title');
        const content = document.getElementById('role-panel-content');

        if (user.ocupacion.toLowerCase() === 'cocina') {
            panelTitle.textContent = 'Módulo de Cocina y Producción';
            content.innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px;">
                    <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border-color); padding: 18px; border-radius: var(--radius-sm);">
                        <h4 style="color: var(--accent-orange); margin-bottom: 8px;">Menú del Día Preparado</h4>
                        <ul style="list-style-type: none; font-size: 0.9rem; color: var(--text-secondary); line-height: 1.8;">
                            <li>🍲 <strong>Plato Principal:</strong> Arroz con Pollo a la Jardinera</li>
                            <li>🥗 <strong>Ensalada:</strong> Mixta con aderezo de limón</li>
                            <li>🥤 <strong>Bebida:</strong> Jugo natural de Maracuyá</li>
                            <li>🍎 <strong>Postre:</strong> Manzana fresca</li>
                        </ul>
                    </div>

                    <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border-color); padding: 18px; border-radius: var(--radius-sm);">
                        <h4 style="color: var(--primary); margin-bottom: 8px;">Acciones Rápidas</h4>
                        <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 12px;">Gestiona el despacho de bandejas e inventario.</p>
                        <button class="btn btn-secondary" style="font-size: 0.85rem; padding: 8px 12px; margin-bottom: 8px;" onclick="alert('Lote de 50 raciones listo para despacho.')">
                            ✓ Notificar Lote Listo
                        </button>
                        <button class="btn btn-secondary" style="font-size: 0.85rem; padding: 8px 12px;" onclick="alert('Inventario actualizado.')">
                            📦 Reportar Stock de Insumos
                        </button>
                    </div>
                </div>
            `;
        } else {
            panelTitle.textContent = 'Módulo de Operación y Registro de Comensales';
            content.innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px;">
                    <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border-color); padding: 18px; border-radius: var(--radius-sm);">
                        <h4 style="color: var(--accent); margin-bottom: 8px;">Control de Acceso al Comedor</h4>
                        <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 14px;">Ingresa la cédula o código del estudiante/comensal para registrar consumo.</p>
                        <div style="display: flex; gap: 8px;">
                            <input type="text" id="codigo-comensal" placeholder="Código o Cédula" style="font-size: 0.9rem;">
                            <button class="btn btn-primary" style="width: auto; padding: 10px 16px; font-size: 0.85rem;" onclick="
                                const cod = document.getElementById('codigo-comensal').value;
                                if(cod) { alert('Comensal ' + cod + ' verificado. Ración registrada con éxito.'); document.getElementById('codigo-comensal').value = ''; }
                                else { alert('Por favor ingresa un código.'); }
                            ">Validar</button>
                        </div>
                    </div>

                    <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border-color); padding: 18px; border-radius: var(--radius-sm);">
                        <h4 style="color: var(--primary); margin-bottom: 8px;">Detalles de la Cuenta</h4>
                        <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 4px;"><strong>Email:</strong> ${user.email}</p>
                        <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 4px;"><strong>Género:</strong> ${user.genero}</p>
                        <p style="font-size: 0.85rem; color: var(--text-secondary);"><strong>Rol:</strong> Operador de Línea</p>
                    </div>
                </div>
            `;
        }
    }
});
