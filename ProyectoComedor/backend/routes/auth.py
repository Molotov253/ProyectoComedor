import random
from fastapi import APIRouter, HTTPException, Depends, Header, status
from typing import Optional, List

from backend.database import get_db, SECURITY_QUESTIONS_CATALOG
from backend.models import (
    RegisterRequest,
    LoginRequest,
    LoginSecurityCheckRequest,
    ForgotPasswordInitRequest,
    ForgotPasswordVerifyRequest,
    ForgotPasswordResetRequest,
    UserProfileResponse
)
from backend.security import (
    hash_password,
    verify_password,
    hash_security_answer,
    verify_security_answer,
    generate_session_token,
    create_signed_token,
    verify_signed_token
)

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])

@router.get("/questions", summary="Obtener catálogo de preguntas de seguridad disponibles")
def get_security_questions():
    return [{"clave": k, "texto": v} for k, v in SECURITY_QUESTIONS_CATALOG.items()]

@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Registro de nuevo usuario")
def register_user(data: RegisterRequest):
    if data.password != data.password_confirmation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las contraseñas no coinciden."
        )

    # Validar que se hayan provisto al menos 3 preguntas distintas y respuestas válidas
    unique_keys = set()
    for item in data.preguntas:
        if not item.clave or not item.respuesta or not item.respuesta.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Todas las preguntas de seguridad deben tener una respuesta válida."
            )
        if item.clave not in SECURITY_QUESTIONS_CATALOG:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Pregunta de seguridad desconocida: {item.clave}"
            )
        unique_keys.add(item.clave)

    if len(unique_keys) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes seleccionar 3 preguntas de seguridad diferentes."
        )

    password_hashed = hash_password(data.password)

    with get_db() as conn:
        cursor = conn.cursor()
        
        # Verificar si el correo ya existe
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (data.email.lower(),))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya se encuentra registrado."
            )

        # Insertar usuario
        cursor.execute("""
            INSERT INTO usuarios (nombre, apellido, ocupacion, email, password_hash, genero)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data.nombre.strip(),
            data.apellido.strip(),
            data.ocupacion.strip().lower(),
            data.email.lower().strip(),
            password_hashed,
            data.genero.strip().lower()
        ))
        user_id = cursor.lastrowid

        # Insertar preguntas de seguridad
        for item in data.preguntas:
            answer_hash = hash_security_answer(item.respuesta)
            cursor.execute("""
                INSERT INTO preguntas_seguridad_usuario (usuario_id, clave_pregunta, respuesta_hash)
                VALUES (?, ?, ?)
            """, (user_id, item.clave, answer_hash))

    return {"status": "success", "message": "Usuario registrado exitosamente."}

@router.post("/login", summary="Paso 1: Validación de credenciales y desafío de pregunta de seguridad")
def login_step_one(data: LoginRequest):
    email_clean = data.email.lower().strip()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, email, password_hash FROM usuarios WHERE email = ?
        """, (email_clean,))
        user = cursor.fetchone()

        if not user or not verify_password(user["password_hash"], data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos."
            )

        # Obtener preguntas asociadas al usuario
        cursor.execute("""
            SELECT clave_pregunta FROM preguntas_seguridad_usuario WHERE usuario_id = ?
        """, (user["id"],))
        rows = cursor.fetchall()
        
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="El usuario no tiene preguntas de seguridad configuradas."
            )

        # Elegir una pregunta aleatoria
        selected = random.choice(rows)
        clave_pregunta = selected["clave_pregunta"]
        pregunta_texto = SECURITY_QUESTIONS_CATALOG.get(clave_pregunta, "¿Pregunta de seguridad?")

        # Crear token firmado temporal para el paso 2 (expira en 10 minutos)
        temp_token = create_signed_token({
            "action": "login_2fa",
            "user_id": user["id"],
            "email": email_clean,
            "clave_pregunta": clave_pregunta
        }, expires_in_seconds=600)

        return {
            "status": "requires_security_check",
            "email": email_clean,
            "temp_token": temp_token,
            "pregunta_clave": clave_pregunta,
            "pregunta_texto": pregunta_texto
        }

@router.post("/login-security-check", summary="Paso 2: Confirmar pregunta de seguridad e iniciar sesión")
def login_step_two(data: LoginSecurityCheckRequest):
    payload = verify_signed_token(data.temp_token)
    if not payload or payload.get("action") != "login_2fa" or payload.get("email") != data.email.lower().strip() or payload.get("clave_pregunta") != data.clave_pregunta:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión de verificación ha expirado o es inválida. Por favor inicia sesión nuevamente."
        )

    user_id = payload["user_id"]

    with get_db() as conn:
        cursor = conn.cursor()
        
        # Buscar respuesta almacenada
        cursor.execute("""
            SELECT respuesta_hash FROM preguntas_seguridad_usuario 
            WHERE usuario_id = ? AND clave_pregunta = ?
        """, (user_id, data.clave_pregunta))
        row = cursor.fetchone()

        if not row or not verify_security_answer(row["respuesta_hash"], data.respuesta):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Respuesta de seguridad incorrecta."
            )

        # Obtener datos de usuario
        cursor.execute("""
            SELECT id, nombre, apellido, ocupacion, email, genero FROM usuarios WHERE id = ?
        """, (user_id,))
        user = cursor.fetchone()

        # Crear sesión
        session_token = generate_session_token()
        cursor.execute("""
            INSERT INTO sesiones (token, usuario_id) VALUES (?, ?)
        """, (session_token, user_id))

        return {
            "status": "success",
            "message": "Inicio de sesión exitoso.",
            "token": session_token,
            "user": {
                "id": user["id"],
                "nombre": user["nombre"],
                "apellido": user["apellido"],
                "ocupacion": user["ocupacion"],
                "email": user["email"],
                "genero": user["genero"]
            }
        }

@router.post("/forgot-password/init", summary="Recuperar contraseña - Paso 1: Obtener pregunta de seguridad")
def forgot_password_init(data: ForgotPasswordInitRequest):
    email_clean = data.email.lower().strip()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email_clean,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe una cuenta registrada con este correo electrónico."
            )

        cursor.execute("""
            SELECT clave_pregunta FROM preguntas_seguridad_usuario WHERE usuario_id = ?
        """, (user["id"],))
        rows = cursor.fetchall()

        if not rows:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se encontraron preguntas de seguridad para esta cuenta."
            )

        selected = random.choice(rows)
        clave_pregunta = selected["clave_pregunta"]
        pregunta_texto = SECURITY_QUESTIONS_CATALOG.get(clave_pregunta, "¿Pregunta de seguridad?")

        temp_token = create_signed_token({
            "action": "forgot_password_verify",
            "user_id": user["id"],
            "email": email_clean,
            "clave_pregunta": clave_pregunta
        }, expires_in_seconds=600)

        return {
            "status": "success",
            "email": email_clean,
            "temp_token": temp_token,
            "pregunta_clave": clave_pregunta,
            "pregunta_texto": pregunta_texto
        }

@router.post("/forgot-password/verify", summary="Recuperar contraseña - Paso 2: Validar respuesta de seguridad")
def forgot_password_verify(data: ForgotPasswordVerifyRequest):
    payload = verify_signed_token(data.temp_token)
    if not payload or payload.get("action") != "forgot_password_verify" or payload.get("email") != data.email.lower().strip() or payload.get("clave_pregunta") != data.clave_pregunta:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La solicitud ha expirado. Por favor inicia el proceso nuevamente."
        )

    user_id = payload["user_id"]

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT respuesta_hash FROM preguntas_seguridad_usuario 
            WHERE usuario_id = ? AND clave_pregunta = ?
        """, (user_id, data.clave_pregunta))
        row = cursor.fetchone()

        if not row or not verify_security_answer(row["respuesta_hash"], data.respuesta):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Respuesta de seguridad incorrecta."
            )

        reset_token = create_signed_token({
            "action": "forgot_password_reset",
            "user_id": user_id,
            "email": data.email.lower().strip()
        }, expires_in_seconds=900)

        return {
            "status": "verified",
            "message": "Identidad confirmada con éxito.",
            "reset_token": reset_token
        }

@router.post("/forgot-password/reset", summary="Recuperar contraseña - Paso 3: Actualizar contraseña")
def forgot_password_reset(data: ForgotPasswordResetRequest):
    if data.new_password != data.new_password_confirmation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las contraseñas no coinciden."
        )

    payload = verify_signed_token(data.reset_token)
    if not payload or payload.get("action") != "forgot_password_reset" or payload.get("email") != data.email.lower().strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token de restablecimiento ha expirado o es inválido."
        )

    user_id = payload["user_id"]
    new_password_hash = hash_password(data.new_password)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE usuarios SET password_hash = ? WHERE id = ?
        """, (new_password_hash, user_id))
        
        # Cerrar sesiones previas por seguridad
        cursor.execute("DELETE FROM sesiones WHERE usuario_id = ?", (user_id,))

    return {
        "status": "success",
        "message": "Contraseña actualizada exitosamente. Ahora puedes iniciar sesión con tu nueva contraseña."
    }

def get_current_user_from_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado.")
    
    token = authorization.replace("Bearer ", "").strip()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.nombre, u.apellido, u.ocupacion, u.email, u.genero
            FROM usuarios u
            INNER JOIN sesiones s ON u.id = s.usuario_id
            WHERE s.token = ?
        """, (token,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión inválida o expirada.")
        
        return dict(user)

@router.get("/me", summary="Obtener perfil del usuario actual autenticado")
def get_current_user(user: dict = Depends(get_current_user_from_token)):
    return {"status": "success", "user": user}

@router.post("/logout", summary="Cerrar sesión actual")
def logout_user(authorization: Optional[str] = Header(None)):
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sesiones WHERE token = ?", (token,))
    return {"status": "success", "message": "Sesión cerrada correctamente."}
