from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class SecurityQuestionItem(BaseModel):
    clave: str
    respuesta: str

class RegisterRequest(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    ocupacion: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    password_confirmation: str = Field(..., min_length=6)
    genero: str = Field(..., min_length=2, max_length=20)
    preguntas: List[SecurityQuestionItem]

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginSecurityCheckRequest(BaseModel):
    email: EmailStr
    temp_token: str
    clave_pregunta: str
    respuesta: str

class ForgotPasswordInitRequest(BaseModel):
    email: EmailStr

class ForgotPasswordVerifyRequest(BaseModel):
    email: EmailStr
    temp_token: str
    clave_pregunta: str
    respuesta: str

class ForgotPasswordResetRequest(BaseModel):
    email: EmailStr
    reset_token: str
    new_password: str = Field(..., min_length=6)
    new_password_confirmation: str = Field(..., min_length=6)

class UserProfileResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    ocupacion: str
    email: str
    genero: str
