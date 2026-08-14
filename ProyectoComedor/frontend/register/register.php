<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registro</title>
    <script src="register.js" defer></script>
</head>
<body>
    <h1>Registro</h1>
    <form id="form-registro" action="" method="POST">
        <!-- Datos Personales y de Cuenta -->
        <div id="contenedor-paso1">
            <h3>Datos de la Cuenta</h3>
            <label for="nombre">Nombre:</label>
            <input type="text" id="nombre" name="nombre" required>
            <br>
            <label for="apellido">Apellido:</label>
            <input type="text" id="apellido" name="apellido" required>
            <br>
            <label for="ocupacion">Ocupación:</label>
            <select name="ocupacion" id="ocupacion" required>
                <option value="operador">Operador</option>
                <option value="cocina">Cocina</option>
            </select>
            <br>
            <label for="email">Correo Electrónico:</label>
            <input type="email" id="email" name="email" required>
            <br>
            <label for="password">Contraseña:</label>
            <input type="password" id="password" name="password" required>
            <br>
            <label for="password_confirmation">Confirmar Contraseña:</label>
            <input type="password" id="password_confirmation" name="password_confirmation" required>
            <br>
            <label for="genero">Genero:</label>
            <select name="genero" id="genero" required>
                <option value="masculino">Masculino</option>
                <option value="femenino">Femenino</option>
                <option value="otro">Otro</option>
            </select>
            <br><br>
            <button type="button" id="btn-siguiente">Siguiente</button>
        </div>

        <!-- Preguntas de Seguridad -->
        <div id="contenedor-paso2" style="display: none;">
            <h3>Preguntas de Seguridad</h3>
            <?php 
            include 'questions.php';
            ?>
            <br>
            <button type="button" id="btn-volver">Atrás</button>
            <input type="submit" value="Registrarse">
        </div>
    </form>

    <p>¿Ya tienes una cuenta? <a href="../login/login.php">Inicia Sesión aquí</a></p>
</body>
</html>