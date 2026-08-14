<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Confirmar Identidad</title>
</head>
<body>
    <h1>Confirmación de Seguridad</h1>
    <p>Por favor, responde a la siguiente pregunta de seguridad para verificar tu identidad y acceder al sistema.</p>

    <form action="../index/index.php" method="POST">
        <!-- Campo oculto para mantener referencia al usuario/pregunta que envía el backend -->
        <input type="hidden" name="email" value="<?php echo isset($_POST['email']) ? htmlspecialchars($_POST['email']) : ''; ?>">
        <input type="hidden" name="pregunta_id" value="">

        <!-- Pregunta de seguridad que el backend cargará aleatoriamente -->
        <label for="respuesta_seguridad">Pregunta de Seguridad:</label>
        <br>
        <input type="text" id="respuesta_seguridad" name="respuesta_seguridad" required>
        <br><br>

        <input type="submit" value="Confirmar y Acceder">
    </form>

    <p><a href="login.php">Cancelar y volver al inicio de sesión</a></p>
</body>
</html>
