import os
import sys
import unittest
from fastapi.testclient import TestClient

# Asegurar que el directorio raíz esté en sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.main import app
from backend.database import get_db, init_db

class TestAuthFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        
        # Limpiar usuario de prueba si existiese
        with get_db() as conn:
            conn.execute("DELETE FROM usuarios WHERE email = ?", ("testuser@comedor.edu",))

    def test_01_get_questions(self):
        response = self.client.get("/api/auth/questions")
        self.assertEqual(response.status_code, 200)
        questions = response.json()
        self.assertIsInstance(questions, list)
        self.assertGreaterEqual(len(questions), 5)
        self.assertTrue(any(q["clave"] == "primer_amor" for q in questions))

    def test_02_register_user_success(self):
        payload = {
            "nombre": "Carlos",
            "apellido": "Gomez",
            "ocupacion": "operador",
            "email": "testuser@comedor.edu",
            "password": "Password123!",
            "password_confirmation": "Password123!",
            "genero": "masculino",
            "preguntas": [
                {"clave": "primer_amor", "respuesta": "Laura"},
                {"clave": "maestro_favorito", "respuesta": "Profesor Mendez"},
                {"clave": "comida_favorita", "respuesta": "Pizza napolitana"}
            ]
        }
        response = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json().get("status"), "success")

    def test_03_register_duplicate_email(self):
        payload = {
            "nombre": "Carlos",
            "apellido": "Gomez",
            "ocupacion": "operador",
            "email": "testuser@comedor.edu",
            "password": "Password123!",
            "password_confirmation": "Password123!",
            "genero": "masculino",
            "preguntas": [
                {"clave": "primer_amor", "respuesta": "Laura"},
                {"clave": "maestro_favorito", "respuesta": "Profesor Mendez"},
                {"clave": "comida_favorita", "respuesta": "Pizza"}
            ]
        }
        response = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("registrado", response.json()["detail"].lower())

    def test_04_login_step_one_success(self):
        response = self.client.post("/api/auth/login", json={
            "email": "testuser@comedor.edu",
            "password": "Password123!"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "requires_security_check")
        self.assertTrue("temp_token" in data)
        self.assertTrue("pregunta_clave" in data)
        self.assertTrue("pregunta_texto" in data)
        
        # Guardar para paso 2
        TestAuthFlow.login_temp_token = data["temp_token"]
        TestAuthFlow.login_pregunta_clave = data["pregunta_clave"]

    def test_05_login_step_two_wrong_answer(self):
        response = self.client.post("/api/auth/login-security-check", json={
            "email": "testuser@comedor.edu",
            "temp_token": TestAuthFlow.login_temp_token,
            "clave_pregunta": TestAuthFlow.login_pregunta_clave,
            "respuesta": "RespuestaTotalmenteEquivocada"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("incorrecta", response.json()["detail"].lower())

    def test_06_login_step_two_correct_answer(self):
        # Mapeo de respuestas configuradas
        answers_map = {
            "primer_amor": "laura",
            "maestro_favorito": "profesor mendez",
            "comida_favorita": "pizza napolitana"
        }
        correct_answer = answers_map[TestAuthFlow.login_pregunta_clave]

        response = self.client.post("/api/auth/login-security-check", json={
            "email": "testuser@comedor.edu",
            "temp_token": TestAuthFlow.login_temp_token,
            "clave_pregunta": TestAuthFlow.login_pregunta_clave,
            "respuesta": correct_answer.upper()  # Debe ser insensible a mayúsculas
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "success")
        self.assertTrue("token" in data)
        self.assertEqual(data["user"]["email"], "testuser@comedor.edu")
        self.assertEqual(data["user"]["ocupacion"], "operador")

        TestAuthFlow.session_token = data["token"]

    def test_07_get_me_authenticated(self):
        headers = {"Authorization": f"Bearer {TestAuthFlow.session_token}"}
        response = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["user"]["nombre"], "Carlos")

    def test_08_forgot_password_flow(self):
        # Paso 1: Solicitar recuperación
        init_res = self.client.post("/api/auth/forgot-password/init", json={
            "email": "testuser@comedor.edu"
        })
        self.assertEqual(init_res.status_code, 200)
        init_data = init_res.json()
        self.assertEqual(init_data.get("status"), "success")

        # Paso 2: Responder pregunta de seguridad
        answers_map = {
            "primer_amor": "Laura",
            "maestro_favorito": "Profesor Mendez",
            "comida_favorita": "Pizza Napolitana"
        }
        verify_res = self.client.post("/api/auth/forgot-password/verify", json={
            "email": "testuser@comedor.edu",
            "temp_token": init_data["temp_token"],
            "clave_pregunta": init_data["pregunta_clave"],
            "respuesta": answers_map[init_data["pregunta_clave"]]
        })
        self.assertEqual(verify_res.status_code, 200)
        reset_token = verify_res.json().get("reset_token")
        self.assertIsNotNone(reset_token)

        # Paso 3: Restablecer contraseña
        reset_res = self.client.post("/api/auth/forgot-password/reset", json={
            "email": "testuser@comedor.edu",
            "reset_token": reset_token,
            "new_password": "NewSecretPassword2026!",
            "new_password_confirmation": "NewSecretPassword2026!"
        })
        self.assertEqual(reset_res.status_code, 200)

        # Verificar que la nueva contraseña funciona en login
        login_new = self.client.post("/api/auth/login", json={
            "email": "testuser@comedor.edu",
            "password": "NewSecretPassword2026!"
        })
        self.assertEqual(login_new.status_code, 200)

    def test_09_logout(self):
        headers = {"Authorization": f"Bearer {TestAuthFlow.session_token}"}
        logout_res = self.client.post("/api/auth/logout", headers=headers)
        self.assertEqual(logout_res.status_code, 200)

        # La sesión ya no debe ser válida
        me_res = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(me_res.status_code, 401)

if __name__ == "__main__":
    unittest.main()
