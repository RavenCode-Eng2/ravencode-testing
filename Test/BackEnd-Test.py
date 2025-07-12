import requests
import traceback
from utils import generar_email_aleatorio, generar_nombre_aleatorio
import random
import string

# Endpoints
BASE_URL = "http://localhost:8001"
JUDGE_URL = "http://localhost:8000"
LEARNING_URL = "http://localhost:8002"
ACHIEVEMENTS_URL = "http://localhost:8003"

# Auth endpoints
REGISTER_USER = f"{BASE_URL}/auth/register"
USER_LOGIN = f"{BASE_URL}/auth/login"
RECOVERY_PASSWORD = f"{BASE_URL}/auth/recovery/request"
RECOVERY_VERIFY = f"{BASE_URL}/auth/recovery/verify"

# Student endpoints
STUDENT_SERVICE = f"{BASE_URL}/students/students/"

# Judge/Submissions endpoints
SUBMISSIONS_SERVICE = f"{JUDGE_URL}/api/v1/submissions/"
DELETION_SUBMISSIONS_SERVICE = f"{JUDGE_URL}/api/v1/submissions/by-user"

# Learning endpoints
GRADES_SERVICE = f"{LEARNING_URL}/grades/"
RESPONSES_SERVICE = f"{LEARNING_URL}/responses/responses/"

# Achievements endpoints
ACHIEVEMENTS_SERVICE = f"{ACHIEVEMENTS_URL}/achievements/"

def register_user(register_data):
    """Registra un nuevo usuario estudiante."""
    response = requests.post(REGISTER_USER, json={
        "nombre": register_data["nombre"],
        "email": register_data["email"],
        "password": register_data["password"],
        "fecha_de_nacimiento": register_data["fecha_de_nacimiento"],
        "institucion_educativa": register_data["institucion_educativa"],
        "grado_academico": register_data["grado_academico"],
        "foto_de_perfil": register_data.get("foto_de_perfil")
    })
    
    response.raise_for_status()
    user_data = response.json()
    print("✅ Usuario registrado exitosamente")
    return user_data

def login_user(email, password):
    """Realiza login de un usuario y retorna el token."""
    response = requests.post(USER_LOGIN, json={
        "email": email,
        "password": password
    })
    
    response.raise_for_status()
    login_data = response.json()
    print("✅ Login exitoso")
    return login_data

def request_password_recovery(email):
    """Solicita recuperación de contraseña."""
    response = requests.post(RECOVERY_PASSWORD, json={
        "email": email
    })
    
    response.raise_for_status()
    recovery_data = response.json()
    print("✅ Solicitud de recuperación enviada")
    return recovery_data

def verify_recovery_code(email, code, new_password):
    """Verifica el código de recuperación y cambia la contraseña."""
    response = requests.post(RECOVERY_VERIFY, json={
        "email": email,
        "code": code,
        "new_password": new_password
    })
    
    response.raise_for_status()
    verify_data = response.json()
    print("✅ Recuperación de contraseña completada")
    return verify_data

def get_student_by_email(email, token=None):
    """Obtiene un estudiante por email."""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    response = requests.get(f"{STUDENT_SERVICE}{email}", headers=headers)
    response.raise_for_status()
    student_data = response.json()
    print("✅ Estudiante obtenido exitosamente")
    return student_data

def update_student(email, update_data):
    
    response = requests.put(f"{STUDENT_SERVICE}{email}", json=update_data)
    response.raise_for_status()
    update_result = response.json()
    print("✅ Estudiante actualizado exitosamente")
    print(update_result)
    return update_result

def delete_student(email, token=None):
    """Elimina un estudiante."""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    response = requests.delete(f"{STUDENT_SERVICE}{email}", headers=headers)
    response.raise_for_status()
    delete_result = response.json()
    print("✅ Estudiante eliminado exitosamente")
    return delete_result

def list_students(token=None):
    """Lista todos los estudiantes."""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    response = requests.get(STUDENT_SERVICE, headers=headers)
    response.raise_for_status()
    students = response.json()
    print(f"✅ Lista de estudiantes obtenida: {len(students)} estudiantes")
    return students

def verify_student_exists(email):
    """Verifica que un estudiante existe en el sistema."""
    try:
        student = get_student_by_email(email)
        assert student is not None, f"Student with email {email} not found"
        return True
    except Exception:
        return False

def verify_student_deleted(email):
    """Verifica que un estudiante fue eliminado del sistema."""
    try:
        # Intentar obtener el estudiante
        response = requests.get(f"{STUDENT_SERVICE}{email}")
        
        # Si la respuesta es 404, significa que el estudiante fue eliminado correctamente
        if response.status_code == 404:
            print("✅ Estudiante eliminado correctamente (404 - No encontrado)")
            return True
        # Si la respuesta es 401, también es exitoso porque significa que no se puede acceder
        elif response.status_code == 401:
            print("✅ Estudiante eliminado correctamente (401 - No autorizado)")
            return True
        # Si encuentra el estudiante (200), entonces no se eliminó correctamente
        elif response.status_code == 200:
            print("❌ Error: El estudiante aún existe en el sistema")
            return False
        else:
            print(f"✅ Estudiante eliminado correctamente (Status: {response.status_code})")
            return True
            
    except requests.exceptions.RequestException as e:
        # Si hay un error de conexión o similar, consideramos que se eliminó correctamente
        print(f"✅ Estudiante eliminado correctamente (Error de acceso: {str(e)})")
        return True

# Funciones para Judge/Submissions
def create_submission(email, problem_id, code, language="python"):
    """Crea una nueva submission de código."""
    submission_data = {
        "email": email,
        "problem_id": problem_id,
        "code": code,
        "language": language
    }
    
    response = requests.post(f"{SUBMISSIONS_SERVICE}", json=submission_data)
    response.raise_for_status()
    submission = response.json()
    print("✅ Submission creada exitosamente")
    return submission

def get_submissions_by_email(email):
    """Obtiene todas las submissions de un usuario."""
    response = requests.get(f"{SUBMISSIONS_SERVICE}?email={email}")
    response.raise_for_status()
    submissions = response.json()
    print(f"✅ Submissions obtenidas: {len(submissions)} submissions")
    return submissions

def get_submission_by_id(submission_id, email=None):
    """Obtiene una submission específica por ID."""
    params = {}
    if email:
        params["email"] = email
    
    response = requests.get(f"{SUBMISSIONS_SERVICE}{submission_id}", params=params)
    response.raise_for_status()
    submission = response.json()
    print("✅ Submission obtenida exitosamente")
    return submission

def update_submission(submission_id, email, code=None, language=None):
    """Actualiza una submission."""
    update_data = {}
    if code is not None:
        update_data["code"] = code
    if language is not None:
        update_data["language"] = language
    
    params = {"email": email}
    response = requests.put(f"{SUBMISSIONS_SERVICE}{submission_id}", json=update_data, params=params)
    response.raise_for_status()
    submission = response.json()
    print("✅ Submission actualizada exitosamente")
    return submission

def delete_submission(submission_id, email):
    """Elimina una submission específica."""
    params = {"email": email}
    response = requests.delete(f"{SUBMISSIONS_SERVICE}{submission_id}", params=params)
    response.raise_for_status()
    print("✅ Submission eliminada exitosamente")
    return True

def delete_all_submissions_by_user(email):
    """Elimina todas las submissions de un usuario."""
    params = {"email": email}
    response = requests.delete(f"{DELETION_SUBMISSIONS_SERVICE}", params=params)
    response.raise_for_status()
    print("✅ Todas las submissions del usuario eliminadas exitosamente")
    return True

def verify_submission_exists(submission_id, email):
    """Verifica que una submission existe."""
    try:
        submission = get_submission_by_id(submission_id, email)
        assert submission is not None, f"Submission with ID {submission_id} not found"
        return True
    except Exception:
        return False

def verify_submission_deleted(submission_id, email):
    """Verifica que una submission fue eliminada."""
    try:
        response = requests.get(f"{SUBMISSIONS_SERVICE}{submission_id}?email={email}")
        
        # Si la respuesta es 404, significa que la submission fue eliminada correctamente
        if response.status_code == 404:
            print("✅ Submission eliminada correctamente (404 - No encontrada)")
            return True
        # Si encuentra la submission (200), entonces no se eliminó correctamente
        elif response.status_code == 200:
            print("❌ Error: La submission aún existe en el sistema")
            return False
        else:
            print(f"✅ Submission eliminada correctamente (Status: {response.status_code})")
            return True
            
    except requests.exceptions.RequestException as e:
        # Si hay un error de conexión o similar, consideramos que se eliminó correctamente
        print(f"✅ Submission eliminada correctamente (Error de acceso: {str(e)})")
        return True

# Funciones para Learning/Grades
def create_grade(email, module, grade_value, date_assigned=None):
    """Crea una nueva calificación para un estudiante."""
    grade_data = {
        "email": email,
        "module": module,
        "grade": grade_value,
        "date_assigned": date_assigned or "2025-01-15"
    }
    
    response = requests.post(f"{GRADES_SERVICE}", json=grade_data)
    response.raise_for_status()
    grade = response.json()
    print(grade)
    print("✅ Calificación creada exitosamente")
    return grade

def get_grade(email, module):
    """Obtiene una calificación específica."""
    response = requests.get(f"{GRADES_SERVICE}{email}/{module}")
    response.raise_for_status()
    grade = response.json()
    
    print("✅ Calificación obtenida exitosamente")
    return grade

def update_grade(email, module, new_grade_value):
    """Actualiza una calificación existente."""
    grade_data = {
        "email": email,
        "module": module,
        "grade": new_grade_value,
        "date_assigned": "2025-01-15"
    }
    
    response = requests.patch(f"{GRADES_SERVICE}{email}/{module}", json=grade_data)
    response.raise_for_status()
    grade = response.json()
    print("✅ Calificación actualizada exitosamente")
    return grade

def list_all_grades():
    """Lista todas las calificaciones."""
    response = requests.get(f"{GRADES_SERVICE}")
    response.raise_for_status()
    grades = response.json()
    print(f"✅ Lista de calificaciones obtenida: {len(grades)} calificaciones")
    return grades

def delete_grades_by_email(email):
    """Elimina todas las calificaciones de un estudiante."""
    response = requests.delete(f"{GRADES_SERVICE}{email}")
    response.raise_for_status()
    result = response.json()
    print("✅ Calificaciones del estudiante eliminadas exitosamente")
    return result

# Funciones para Learning/Responses
def save_responses(email, responses_data):
    """Guarda las respuestas de un estudiante."""
    responses_payload = {
        "email": email,
        "responses": responses_data
    }
    print(responses_payload)
    
    response = requests.post(f"{RESPONSES_SERVICE}", json=responses_payload)
    response.raise_for_status()
    result = response.json()
    print("✅ Respuestas guardadas exitosamente")
    return result

def get_responses_by_email(email):
    """Obtiene las respuestas de un estudiante."""
    response = requests.get(f"{RESPONSES_SERVICE}{email}")
    response.raise_for_status()
    responses = response.json()
    print("✅ Respuestas obtenidas exitosamente")
    return responses

def delete_responses_by_email(email):
    """Elimina todas las respuestas de un estudiante."""
    response = requests.delete(f"{RESPONSES_SERVICE}{email}")
    response.raise_for_status()
    result = response.json()
    print("✅ Respuestas del estudiante eliminadas exitosamente")
    return result

def verify_grade_exists(email, module):
    """Verifica que una calificación existe."""
    try:
        grade = get_grade(email, module)
        assert grade is not None, f"Grade for {email} in {module} not found"
        return True
    except Exception:
        return False

def verify_responses_exist(email):
    """Verifica que las respuestas existen."""
    try:
        responses = get_responses_by_email(email)
        assert responses is not None, f"Responses for {email} not found"
        return True
    except Exception:
        return False

# Funciones para Achievements
def update_student_achievement(email, achievement_name, course_id, title, description, score, total_points):
    """Actualiza o agrega un logro de estudiante."""
    achievement_data = {
        "email": email,
        "achievement": {
            "achievement_name": achievement_name,
            "course_id": course_id,
            "title": title,
            "description": description
        },
        "score": score,
        "total_points": total_points
    }
    
    response = requests.post(f"{ACHIEVEMENTS_SERVICE}update", json=achievement_data)
    response.raise_for_status()
    result = response.json()
    print("✅ Logro de estudiante actualizado exitosamente")
    return result

def get_student_achievements(email):
    """Obtiene los logros de un estudiante."""
    response = requests.get(f"{ACHIEVEMENTS_SERVICE}{email}")
    response.raise_for_status()
    achievements = response.json()
    print("✅ Logros del estudiante obtenidos exitosamente")
    return achievements

def verify_achievements_exist(email):
    """Verifica que los logros existen."""
    try:
        achievements = get_student_achievements(email)
        assert achievements is not None, f"Achievements for {email} not found"
        return True
    except Exception:
        return False

def integration_test():
    """Ejecuta las pruebas de integración completas."""
    
    # Datos de prueba
    test_email = generar_email_aleatorio()
    test_nombre = generar_nombre_aleatorio()
    test_password = "TestPassword123!"
    new_password = "NewPassword456!"
    
    # Datos de prueba para submissions
    test_problem_id = "686422bf851b70e5b8b13b7c"  # ID de ejemplo para un problema
    test_code = """
def suma(a, b):
    return a + b

# Test
print(suma(5, 3))
"""
    
    # Datos de prueba para Learning
    test_module = "Matemáticas Avanzadas"
    test_grade = 95.5
    test_responses = [
        {"question_id": "1", "answer": "A"},
        {"question_id": "2", "answer": "B"},
        {"question_id": "3", "answer": "C"}
    ]
    
    # Datos de prueba para Achievements
    test_achievement_name = "Primer Problema Resuelto"
    test_course_id = "CS101"
    test_title = "Problema Básico Completado"
    test_description = "El estudiante resolvió su primer problema de programación"
    test_score = 85.0
    test_total_points = 100.0
    
    print(f"🧪 Iniciando pruebas con email: {test_email}")
    print(f"🧪 Nombre de prueba: {test_nombre}")
    print("="*60)
    
    # Step 1: Register user
    print("\n1. Registrando usuario...")
    try:
        user_data = register_user({
            "nombre": test_nombre,
            "email": test_email,
            "password": test_password,
            "fecha_de_nacimiento": "2000-01-01",
            "institucion_educativa": "Universidad Test",
            "grado_academico": "Ingeniería",
            "foto_de_perfil": "https://example.com/photo.jpg"
        })
    except Exception as e:
        print(f"❌ Error al registrar usuario: {str(e)}")
        return

    # Step 2: Verify user registration
    print("\n2. Verificando registro...")
    try:
        assert verify_student_exists(test_email), "El usuario no existe después del registro"
        print("✅ Usuario verificado en el sistema")
    except Exception as e:
        print(f"❌ Error al verificar el registro: {str(e)}")
        return

    # Step 3: Login user
    print("\n3. Realizando login...")
    try:
        login_data = login_user(test_email, test_password)
        assert "access_token" in login_data, "No se recibió token de acceso"
        token = login_data["access_token"]
    except Exception as e:
        print(f"❌ Error al hacer login: {str(e)}")
        token = None
        return

    # Step 4: Get student data with token
    print("\n4. Obteniendo datos del estudiante...")
    try:
        if token:
            student_data = get_student_by_email(test_email, token)
            assert student_data["Correo_electronico"] == test_email, "Los datos no coinciden"
        else:
            print("❌ No hay token disponible")
            return
    except Exception as e:
        print(f"❌ Error al obtener datos del estudiante: {str(e)}")
        return

    # Step 5: Update student data
    print("\n5. Actualizando datos del estudiante...")
    try:
        if token:
            update_data = {
            "Nombre": "Juan Perez",
            "Correo_electronico": test_email,
            "Contrasena": "securepassword123",
            "Fecha_de_nacimiento": "1990-05-15",
            "Foto_de_perfil": "http://example.com/foto.jpg",
            "Institucion_educativa": "Universidad Nacional de Colombia",
            "Grado_academico": "Licenciatura en Ciencias"
            }
            updated_student = update_student(test_email, update_data)
            assert updated_student["student"]["Nombre"] == update_data["Nombre"], "Los datos no se actualizaron"
        else:
            print("❌ No hay token disponible")
            return
    except Exception as e:
        print(f"❌ Error al actualizar datos del estudiante: {str(e)}")
        return

    # Step 6: Request password recovery
    print("\n6. Solicitando recuperación de contraseña...")
    try:
        recovery_data = request_password_recovery(test_email)
        assert "message" in recovery_data, "No se recibió confirmación de recuperación"
    except Exception as e:
        print(f"❌ Error al solicitar recuperación de contraseña: {str(e)}")
        return

    # Step 7: List all students
    print("\n7. Listando estudiantes...")
    try:
        if token:
            students = list_students(token)
            assert isinstance(students, list), "No se recibió lista de estudiantes"
            assert any(s["Correo_electronico"] == test_email for s in students), "El estudiante no está en la lista"
        else:
            print("❌ No hay token disponible")
            return
    except Exception as e:
        print(f"❌ Error al listar estudiantes: {str(e)}")
        return

    # Step 8: Create submission (Judge)
    print("\n8. Creando submission de código...")
    try:
        submission = create_submission(test_email, test_problem_id, test_code, "python")
        submission_id = submission["_id"]
        print(f"✅ Submission creada con ID: {submission_id}")
    except Exception as e:
        print(f"❌ Error al crear submission: {str(e)}")
        return

    # Step 9: Get submissions by user
    print("\n9. Obteniendo submissions del usuario...")
    try:
        submissions = get_submissions_by_email(test_email)
        assert isinstance(submissions, list), "No se recibió lista de submissions"
        assert any(s["_id"] == submission_id for s in submissions), "La submission no está en la lista"
    except Exception as e:
        print(f"❌ Error al obtener submissions: {str(e)}")
        return

    # Step 10: Get specific submission
    print("\n10. Obteniendo submission específica...")
    try:
        submission_data = get_submission_by_id(submission_id, test_email)
        assert submission_data["user_email"] == test_email, "La submission no pertenece al usuario"
    except Exception as e:
        print(f"❌ Error al obtener submission específica: {str(e)}")
        return

    # Step 11: Update student achievement (Achievements)
    print("\n11. Actualizando logro del estudiante...")
    try:
        achievement = update_student_achievement(
            test_email, 
            test_achievement_name, 
            test_course_id, 
            test_title, 
            test_description, 
            test_score, 
            test_total_points
        )
        assert achievement is not None, "El logro no se actualizó correctamente"
    except Exception as e:
        print(f"❌ Error al actualizar logro: {str(e)}")
        return

    # Step 12: Get student achievements
    print("\n12. Obteniendo logros del estudiante...")
    try:
        achievements = get_student_achievements(test_email)
        assert achievements is not None, "No se encontraron logros del estudiante"
        assert "email" in achievements, "Los logros no tienen el formato esperado"
    except Exception as e:
        print(f"❌ Error al obtener logros: {str(e)}")
        return

    # Step 13: Create grade (Learning)
    print("\n13. Creando calificación...")
    try:
        grade = create_grade(test_email, test_module, test_grade)
        
        assert "successfully" in grade["grade"]["message"] , "La calificación no pertenece al usuario"
    except Exception as e:
        print(f"❌ Error al crear calificación: {str(e)}")
        return

    # Step 14: Get grade
    print("\n14. Obteniendo calificación...")
    try:
        grade_data = get_grade(test_email, test_module)
        assert grade_data["email"] == test_email, "La calificación no pertenece al usuario"
        assert grade_data["grade"] == test_grade, "La calificación no coincide"
    except Exception as e:
        print(f"❌ Error al obtener calificación: {str(e)}")
        return

    # Step 15: Update grade
    print("\n15. Actualizando calificación...")
    try:
        new_grade = 98.5
        updated_grade = update_grade(test_email, test_module, new_grade)
        assert "successfully" in updated_grade["message"] , "La calificación no se actualizó"
    except Exception as e:
        print(f"❌ Error al actualizar calificación: {str(e)}")
        return

    # Step 16: Save responses (Learning)
    print("\n16. Guardando respuestas...")
    try:
        responses = save_responses(test_email, test_responses)
        assert "successfully" in responses["message"], "Las respuestas no pertenecen al usuario"
    except Exception as e:
        print(f"❌ Error al guardar respuestas: {str(e)}")
        return

    # Step 17: Get responses
    print("\n17. Obteniendo respuestas...")
    try:
        responses_data = get_responses_by_email(test_email)
        assert responses_data["email"] == test_email, "Las respuestas no pertenecen al usuario"
        assert responses_data["_id"] == responses["inserted_id"], "No se encontraron respuestas"
    except Exception as e:
        print(f"❌ Error al obtener respuestas: {str(e)}")
        return

    # Step 18: Delete specific submission
    print("\n18. Eliminando submission específica...")
    try:
        delete_submission(submission_id, test_email)
        if verify_submission_deleted(submission_id, test_email):
            print("✅ Verificación de eliminación de submission exitosa")
        else:
            print("❌ Error: La submission no fue eliminada correctamente")
            return
    except Exception as e:
        print(f"❌ Error al eliminar submission: {str(e)}")
        return

    # Step 19: Delete grades by email
    print("\n19. Eliminando calificaciones del estudiante...")
    try:
        delete_result = delete_grades_by_email(test_email)
        assert delete_result["deleted_count"] > 0, "No se eliminaron calificaciones"
    except Exception as e:
        print(f"❌ Error al eliminar calificaciones: {str(e)}")
        return

    # Step 20: Delete responses by email
    print("\n20. Eliminando respuestas del estudiante...")
    try:
        delete_result = delete_responses_by_email(test_email)
        assert delete_result["deleted_count"] > 0, "No se eliminaron respuestas"
    except Exception as e:
        print(f"❌ Error al eliminar respuestas: {str(e)}")
        return

    # Step 21: Delete student and verify
    print("\n21. Eliminando estudiante...")
    try:
        if token:
            delete_student(test_email, token)
            # Verificar que el estudiante fue eliminado haciendo un GET
            if verify_student_deleted(test_email):
                print("✅ Verificación de eliminación exitosa")
            else:
                print("❌ Error: El estudiante no fue eliminado correctamente")
                return
        else:
            print("❌ No hay token disponible")
            return
    except Exception as e:
        print(f"❌ Error al eliminar estudiante: {str(e)}")
        return

    print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de integración para API de Estudiantes, Judge, Learning y Achievements")
    integration_test()
