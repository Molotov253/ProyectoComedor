<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inicia Sesión</title>
</head>
<body>
    <h1>Inicio de Sesión</h1>
    <form action="confirm_user.php" method="POST">
        <label for="email">Correo Electrónico:</label>
        <input type="email" id="email" name="email" required>
        <br>
        <label for="password">Contraseña:</label>
        <input type="password" id="password" name="password" required>
        <br>
        <input type="submit" value="Iniciar Sesión">
    </form>
    <p>¿No tienes una cuenta? <a href="../register/register.php">Regístrate aquí</a></p>
    <p>¿Olvidaste tu contraseña? <a href="../forgot_password/forgot_password.php">Recuperar contraseña aquí</a></p>
</body>
</html>