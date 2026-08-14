<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recuperar Contraseña</title>
    <script src="forgot_password.js" defer></script>
</head>
<body>
    <h1>Recuperar Contraseña</h1>
    
    <form id="form-recuperar" action="" method="POST">
        <!-- Identificación por Correo -->
        <div id="contenedor-correo">
            <h3>Paso 1: Identificación</h3>
            <label for="email">Correo Electrónico:</label>
            <input type="email" id="email" name="email" required>
            <br><br>
            <button type="button" id="btn-buscar-correo">Continuar</button>
        </div>

        <!-- Pregunta de Seguridad Aleatoria -->
        <div id="contenedor-pregunta" style="display: none;">
            <h3>Paso 2: Pregunta de Seguridad</h3>
            <label id="label-pregunta" for="respuesta_seguridad">Pregunta de Seguridad:</label>
            <br>
            <!-- Campo oculto para identificar la pregunta enviada por el backend -->
            <input type="hidden" id="pregunta_id" name="pregunta_id" value="">
            <input type="text" id="respuesta_seguridad" name="respuesta_seguridad" required>
            <br><br>
            <button type="button" id="btn-volver-correo">Atrás</button>
            <button type="button" id="btn-validar-respuesta">Continuar</button>
        </div>

        <!-- Cambio de Contraseña -->
        <div id="contenedor-password" style="display: none;">
            <h3>Paso 3: Nueva Contraseña</h3>
            <label for="new_password">Nueva Contraseña:</label>
            <input type="password" id="new_password" name="new_password" required>
            <br>
            <label for="new_password_confirmation">Confirmar Nueva Contraseña:</label>
            <input type="password" id="new_password_confirmation" name="new_password_confirmation" required>
            <br><br>
            <input type="submit" value="Actualizar Contraseña">
        </div>
    </form>

    <p><a href="../login/login.php">Volver al Inicio de Sesión</a></p>
</body>
</html>
