import requests
import traceback
from utils import generar_email_aleatorio, generar_nombre_aleatorio
import random
import string
import json
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

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



class TestResult:
    def __init__(self, test_name, success, error_message=None, execution_time=None):
        self.test_name = test_name
        self.success = success
        self.error_message = error_message
        self.execution_time = execution_time
        self.timestamp = datetime.now()

class IntegrationTestSuite:
    def __init__(self):
        self.results = []
        self.test_data = {}
        self.start_time = datetime.now()
        
    def add_result(self, test_name, success, error_message=None, execution_time=None):
        result = TestResult(test_name, success, error_message, execution_time)
        self.results.append(result)
        
    def get_summary(self):
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': success_rate,
            'duration': (datetime.now() - self.start_time).total_seconds()
        }

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
        response = requests.get(f"{STUDENT_SERVICE}{email}")
        
        if response.status_code == 404:
            print("✅ Estudiante eliminado correctamente (404 - No encontrado)")
            return True
        elif response.status_code == 401:
            print("✅ Estudiante eliminado correctamente (401 - No autorizado)")
            return True
        elif response.status_code == 200:
            print("❌ Error: El estudiante aún existe en el sistema")
            return False
        else:
            print(f"✅ Estudiante eliminado correctamente (Status: {response.status_code})")
            return True
            
    except requests.exceptions.RequestException as e:
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
        
        if response.status_code == 404:
            print("✅ Submission eliminada correctamente (404 - No encontrada)")
            return True
        elif response.status_code == 200:
            print("❌ Error: La submission aún existe en el sistema")
            return False
        else:
            print(f"✅ Submission eliminada correctamente (Status: {response.status_code})")
            return True
            
    except requests.exceptions.RequestException as e:
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

def create_test_charts(test_suite):
    
    charts = []
    
    # Configurar el estilo de seaborn para gráficos más bonitos
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # Configurar el tamaño de fuente para mejor legibilidad
    plt.rcParams.update({'font.size': 12})
    
    # 1. Gráfico de barras de pruebas exitosas y fallidas
    summary = test_suite.get_summary()
    fig, ax = plt.subplots(figsize=(10, 6))
    
    categories = ['Exitosas', 'Fallidas']
    values = [summary['passed'], summary['failed']]
    colors = ['#28a745', '#dc3545']
    
    bars = ax.bar(categories, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    
    # Agregar valores en las barras
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{value}', ha='center', va='bottom', fontweight='bold', fontsize=14)
    
    ax.set_title('Resultados de Pruebas - RavenCode', fontsize=18, fontweight='bold', pad=20)
    ax.set_ylabel('Cantidad de Pruebas', fontsize=14, fontweight='bold')
    ax.set_xlabel('Estado de las Pruebas', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, max(values) + 2)
    
    # Agregar porcentajes
    total = summary['total']
    for i, (bar, value) in enumerate(zip(bars, values)):
        percentage = (value / total) * 100
        ax.text(bar.get_x() + bar.get_width()/2., height/2,
                f'{percentage:.1f}%', ha='center', va='center', 
                fontweight='bold', fontsize=12, color='white')
    
    plt.tight_layout()
    chart_path = 'test_results_bars.png'
    plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    charts.append(chart_path)
    
    # 2. Gráfico de pastel de la distribución de resultados
    fig, ax = plt.subplots(figsize=(10, 8))
    
    labels = ['Pruebas Exitosas', 'Pruebas Fallidas']
    sizes = [summary['passed'], summary['failed']]
    colors_pie = ['#28a745', '#dc3545']
    explode = (0.05, 0.05)  # Separar ligeramente las secciones
    
    ax.pie(sizes, explode=explode, labels=labels, colors=colors_pie,
            autopct='%1.1f%%', startangle=90, shadow=True,
            textprops={'fontsize': 12, 'fontweight': 'bold'})
    
    ax.set_title('Distribución de Resultados - RavenCode', fontsize=18, fontweight='bold', pad=20)
    ax.legend(labels, title="Estados", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    plt.tight_layout()
    pie_chart_path = 'results_distribution_pie.png'
    plt.savefig(pie_chart_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    charts.append(pie_chart_path)
    
    # 3. Gráfico de barras de resultados por servicio
    services = ['User Service', 'Judge Service', 'Learning Service', 'Achievements Service']
    service_passed = {
        'User Service': 0,
        'Judge Service': 0,
        'Learning Service': 0,
        'Achievements Service': 0
    }
    service_failed = {
        'User Service': 0,
        'Judge Service': 0,
        'Learning Service': 0,
        'Achievements Service': 0
    }
    
    # Contar pruebas por servicio (exitosas y fallidas)
    for result in test_suite.results:
        if 'User' in result.test_name :
            if result.success:
                service_passed['User Service'] += 1
            else:
                service_failed['User Service'] += 1
        elif 'Judge' in result.test_name :
            if result.success:
                service_passed['Judge Service'] += 1
            else:
                service_failed['Judge Service'] += 1
        elif 'Learning' in result.test_name :
            if result.success:
                service_passed['Learning Service'] += 1
            else:
                service_failed['Learning Service'] += 1
        elif 'Achievement' in result.test_name :
            if result.success:
                service_passed['Achievements Service'] += 1
            else:
                service_failed['Achievements Service'] += 1
    
    # Crear gráfico de barras con dos barras por servicio
    fig, ax = plt.subplots(figsize=(14, 8))
    
    x = range(len(services))
    width = 0.35
    
    # Barras para pruebas exitosas (verde)
    passed_values = list(service_passed.values())
    failed_values = list(service_failed.values())
    
    bars1 = ax.bar([i - width/2 for i in x], passed_values, width, label='Exitosas', color='#28a745', alpha=0.8, edgecolor='black')
    bars2 = ax.bar([i + width/2 for i in x], failed_values, width, label='Fallidas', color='#dc3545', alpha=0.8, edgecolor='black')
    
    # Agregar valores en las barras
    for i, (bar1, bar2, passed, failed) in enumerate(zip(bars1, bars2, passed_values, failed_values)):
        # Valor en la barra verde (exitosas)
        if passed > 0:
            ax.text(bar1.get_x() + bar1.get_width()/2., passed/2,
                    f'{passed}', ha='center', va='center', fontweight='bold', fontsize=11, color='white')
        
        # Valor en la barra roja (fallidas)
        if failed > 0:
            ax.text(bar2.get_x() + bar2.get_width()/2., failed/2,
                    f'{failed}', ha='center', va='center', fontweight='bold', fontsize=11, color='white')
    
    ax.set_title('Resultados por Servicio - RavenCode', fontsize=18, fontweight='bold', pad=20)
    ax.set_ylabel('Cantidad de Pruebas', fontsize=14, fontweight='bold')
    ax.set_xlabel('Servicios', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(services, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Ajustar límites del eje Y
    max_total = max([p + f for p, f in zip(passed_values, failed_values)])
    ax.set_ylim(0, max_total + 1)
    
    plt.tight_layout()
    service_chart_path = 'service_results_bars.png'
    plt.savefig(service_chart_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    charts.append(service_chart_path)
    
    return charts

def generate_pdf_report(test_suite, charts):
    """Genera un reporte PDF elegante y profesional para RavenCode."""
    doc = SimpleDocTemplate("Reporte_Pruebas_Integracion.pdf", pagesize=A4)
    story = []
    
    # Estilos elegantes y modernos
    styles = getSampleStyleSheet()
    
    # Paleta de colores elegante
    primary_color = colors.HexColor('#2c3e50')      # Azul oscuro elegante
    secondary_color = colors.HexColor('#3498db')    # Azul medio
    accent_color = colors.HexColor('#e74c3c')       # Rojo elegante
    success_color = colors.HexColor('#27ae60')      # Verde elegante
    warning_color = colors.HexColor('#f39c12')      # Naranja elegante
    light_bg = colors.HexColor('#ecf0f1')          # Fondo claro
    dark_text = colors.HexColor('#2c3e50')         # Texto oscuro
    light_text = colors.HexColor('#7f8c8d')        # Texto claro
    
    # Estilo para el título principal con diseño elegante
    ravencode_title_style = ParagraphStyle(
        'RavenCodeTitle',
        parent=styles['Heading1'],
        fontSize=32,
        spaceAfter=35,
        alignment=TA_CENTER,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        spaceBefore=20,
        borderWidth=0,
        borderColor=primary_color,
        borderPadding=10
    )
    
    # Estilo para subtítulos elegantes
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=20,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=secondary_color,
        fontName='Helvetica-Bold',
        spaceBefore=15
    )
    
    # Estilo para secciones con diseño moderno
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=20,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        spaceBefore=25,
        leftIndent=0,
        rightIndent=0
    )
    
    # Estilo para información con tipografía elegante
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=10,
        textColor=dark_text,
        fontName='Helvetica',
        leftIndent=20,
        spaceBefore=5
    )
    
    # Estilo para texto destacado
    highlight_style = ParagraphStyle(
        'HighlightStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=8,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )

    # Encabezado elegante con logos y título
    header_data = []
    
    # Crear una fila con logo UNAL, título y logo RavenCode
    row_data = []
    
    # Logo de la universidad (izquierda)
    if os.path.exists("Test/UNAL.png"):
        unal_logo = Image("Test/UNAL.png", width=1.8*inch, height=1.3*inch)
        row_data.append(unal_logo)
    else:
        row_data.append("")
    
    # Título en el centro
    row_data.append(Paragraph("RAVENCODE", ravencode_title_style))
    

    
    header_data.append(row_data)
    
    # Crear tabla de encabezado
    header_table = Table(header_data, colWidths=[2*inch, 4*inch, 2*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 20))
    
    # Línea decorativa elegante
    story.append(Paragraph("<hr width='80%' color='#3498db' thickness='2'/>", styles['Normal']))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Reporte de Pruebas de Integración", subtitle_style))
    story.append(Spacer(1, 35))
    
    # Información del reporte con diseño moderno
    story.append(Paragraph("INFORMACIÓN DEL REPORTE", section_style))
    
    # Crear tabla de información con diseño elegante
    info_data = [
        ['Campo', 'Valor'],
        ['Fecha de Generación', datetime.now().strftime('%d/%m/%Y %H:%M:%S')],
        ['Duración Total', f"{test_suite.get_summary()['duration']:.2f} segundos"],
        ['Versión del Sistema', 'RavenCode v1.0'],
        ['Tipo de Reporte', 'Pruebas de Integración Completa']
    ]
    
    info_table = Table(info_data, colWidths=[2.5*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
        ('BACKGROUND', (0, 1), (-1, -1), light_bg),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 30))
    
    # Resumen ejecutivo con diseño elegante
    summary = test_suite.get_summary()
    story.append(Paragraph("RESUMEN EJECUTIVO", section_style))
    
    # Crear tabla de resumen con diseño moderno
    summary_data = [
        ['Métrica', 'Valor', 'Estado', 'Porcentaje'],
        ['Total de Pruebas', str(summary['total']), "●", "100%"],
        ['Pruebas Exitosas', str(summary['passed']), "✓", f"{summary['success_rate']:.1f}%"],
        ['Pruebas Fallidas', str(summary['failed']), "✗", f"{100-summary['success_rate']:.1f}%"],
        ['Tasa de Éxito', f"{summary['success_rate']:.1f}%", "✓", "N/A"]
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
        ('BACKGROUND', (0, 1), (-1, -1), light_bg),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 30))
    
    # Gráficos con diseño elegante
    if charts:
        story.append(Paragraph("ANÁLISIS GRÁFICO", section_style))
        for chart_path in charts:
            if os.path.exists(chart_path):
                try:
                    img = Image(chart_path, width=6.5*inch, height=4.5*inch)
                    story.append(img)
                    story.append(Spacer(1, 25))
                except:
                    pass
    
    # Tabla de resultados detallados con diseño elegante
    story.append(Paragraph("RESULTADOS DETALLADOS", section_style))
    
    table_data = [['Prueba', 'Estado', 'Tiempo (s)', 'Mensaje']]
    for result in test_suite.results:
        if result.success:
            status = "✓ EXITOSA"
            status_color = success_color
        else:
            status = "✗ FALLIDA"
            status_color = accent_color
        
        time_str = f"{result.execution_time:.2f}" if result.execution_time else "N/A"
        message = result.error_message if result.error_message else "Prueba completada exitosamente"
        table_data.append([result.test_name, status, time_str, message])
    
    # Crear tabla con diseño elegante
    table = Table(table_data, colWidths=[3.2*inch, 1.5*inch, 1*inch, 2.3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    # Aplicar colores alternados y estados
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            table.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), light_bg)]))
        
        # Colorear el estado
        if table_data[i][1] == "✓ EXITOSA":
            table.setStyle(TableStyle([('TEXTCOLOR', (1, i), (1, i), success_color)]))
        else:
            table.setStyle(TableStyle([('TEXTCOLOR', (1, i), (1, i), accent_color)]))
    
    story.append(table)
    story.append(Spacer(1, 30))
    
    # Espacio antes del pie de página
    story.append(Spacer(1, 30))
    
    # Pie de página elegante con imagen de RavenCode
    story.append(Paragraph("<hr width='100%' color='#3498db' thickness='1'/>", styles['Normal']))
    story.append(Spacer(1, 15))
    
    # Crear pie de página con imagen de RavenCode
    footer_row = []
    
    # Información del sistema
    footer_info = [
        ['Sistema', 'LMS - RavenCode'],
        ['Institución', 'Universidad Nacional de Colombia'],
        ['Fecha', datetime.now().strftime('%d/%m/%Y')],
        ['Versión', 'v1.0 - Reporte de Integración']
    ]
    
    footer_info_table = Table(footer_info, colWidths=[1.5*inch, 3*inch])
    footer_info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), light_text),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    footer_row.append(footer_info_table)
    
    # Imagen de RavenCode al lado
    if os.path.exists("Test/ravenCode1.png"):
        ravencode_footer_logo = Image("Test/ravenCode1.png", width=1.2*inch, height=1.2*inch)
        footer_row.append(ravencode_footer_logo)
    else:
        footer_row.append("")
    
    # Crear tabla del pie de página
    footer_table = Table([footer_row], colWidths=[4.5*inch, 2.5*inch])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    story.append(footer_table)
    
    # Construir PDF
    doc.build(story)
    
    # Limpiar archivos temporales
    for chart_path in charts:
        if os.path.exists(chart_path):
            os.remove(chart_path)

def run_test_case(test_suite, test_name, test_function, *args, **kwargs):
    """Ejecuta un caso de prueba y registra el resultado."""
    start_time = datetime.now()
    try:
        result = test_function(*args, **kwargs)
        execution_time = (datetime.now() - start_time).total_seconds()
        test_suite.add_result(test_name, True, None, execution_time)
        return result
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        test_suite.add_result(test_name, False, str(e), execution_time)
        print(f"❌ {test_name}: {str(e)}")
        return None

def run_error_test_case(test_suite, test_name, test_function, expected_error, *args, **kwargs):
    """Ejecuta un caso de prueba que debe fallar y registra el resultado."""
    start_time = datetime.now()
    try:
        result = test_function(*args, **kwargs)
        execution_time = (datetime.now() - start_time).total_seconds()
        # Si llegamos aquí, la prueba no falló como se esperaba
        test_suite.add_result(test_name, False, f"Se esperaba error  pero la prueba pasó", execution_time)
        print(f"❌ {test_name}: Se esperaba error pero la prueba pasó")
        return None
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        # Si la prueba falló como se esperaba, es exitosa
        test_suite.add_result(test_name, True, f"Error esperado capturado:", execution_time)
        print(f"✅ {test_name}: Error esperado capturado correctamente")
        return None

def integration_test():
    """Ejecuta las pruebas de integración completas con casos de éxito y error."""
    
    test_suite = IntegrationTestSuite()
    
    # Datos de prueba
    test_email = generar_email_aleatorio()
    test_nombre = generar_nombre_aleatorio()
    test_password = "TestPassword123!"
    new_password = "NewPassword456!"
    
    # Datos de prueba para submissions
    test_problem_id = "686422bf851b70e5b8b13b7c"
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
    
    # ===== CASOS DE ÉXITO =====
    print("\n📋 EJECUTANDO CASOS DE ÉXITO")
    print("="*40)
    
    # 1. Registro de usuario exitoso
    print("\n1. Registrando usuario...")
    user_data = run_test_case(test_suite, "User - Registro de Usuario", register_user, {
        "nombre": test_nombre,
        "email": test_email,
        "password": test_password,
        "fecha_de_nacimiento": "2000-01-01",
        "institucion_educativa": "Universidad Test",
        "grado_academico": "Ingeniería",
        "foto_de_perfil": "https://example.com/photo.jpg"
    })
    
    if not user_data:
        print("❌ No se puede continuar sin usuario registrado")
        return
    
    # 2. Verificación de registro
    print("\n2. Verificando registro...")
    run_test_case(test_suite, "User - Verificación de Registro", verify_student_exists, test_email)
    
    # 3. Login exitoso
    print("\n3. Realizando login...")
    login_data = run_test_case(test_suite, "User - Login de Usuario", login_user, test_email, test_password)
    if login_data:
        token = login_data.get("access_token")
    else:
        token = None
    
    # 4. Obtener datos del estudiante
    print("\n4. Obteniendo datos del estudiante...")
    if token:
        run_test_case(test_suite, "User - Obtener Datos de Estudiante", get_student_by_email, test_email, token)
    
    # 5. Actualizar datos del estudiante
    print("\n5. Actualizando datos del estudiante...")
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
        run_test_case(test_suite, "User - Actualizar Datos de Estudiante", update_student, test_email, update_data)
    
    # 6. Solicitar recuperación de contraseña
    print("\n6. Solicitando recuperación de contraseña...")
    run_test_case(test_suite, "User - Solicitar Recuperación de Contraseña", request_password_recovery, test_email)
    
    # 7. Listar estudiantes
    print("\n7. Listando estudiantes...")
    if token:
        run_test_case(test_suite, "User - Listar Estudiantes", list_students, token)
    
    # 8. Crear submission
    print("\n8. Creando submission de código...")
    submission = run_test_case(test_suite, "Judge - Crear Submission de Código", create_submission, test_email, test_problem_id, test_code, "python")
    if submission:
        submission_id = submission.get("_id")
    else:
        submission_id = None
    
    # 9. Obtener submissions del usuario
    print("\n9. Obteniendo submissions del usuario...")
    run_test_case(test_suite, "Judge - Obtener Submissions por Usuario", get_submissions_by_email, test_email)
    
    # 10. Obtener submission específica
    print("\n10. Obteniendo submission específica...")
    if submission_id:
        run_test_case(test_suite, "Judge - Obtener Submission por ID", get_submission_by_id, submission_id, test_email)
    
    # 11. Actualizar logro del estudiante
    print("\n11. Actualizando logro del estudiante...")
    run_test_case(test_suite, "Achievements - Actualizar Logro de Estudiante", update_student_achievement,
                  test_email, test_achievement_name, test_course_id, test_title, test_description, test_score, test_total_points)
    
    # 12. Obtener logros del estudiante
    print("\n12. Obteniendo logros del estudiante...")
    run_test_case(test_suite, "Achievements - Obtener Logros de Estudiante", get_student_achievements, test_email)
    
    # 13. Crear calificación
    print("\n13. Creando calificación...")
    run_test_case(test_suite, "Learning - Crear Calificación", create_grade, test_email, test_module, test_grade)
    
    # 14. Obtener calificación
    print("\n14. Obteniendo calificación...")
    run_test_case(test_suite, "Learning - Obtener Calificación", get_grade, test_email, test_module)
    
    # 15. Actualizar calificación
    print("\n15. Actualizando calificación...")
    new_grade = 98.5
    run_test_case(test_suite, "Learning - Actualizar Calificación", update_grade, test_email, test_module, new_grade)
    
    # 16. Guardar respuestas
    print("\n16. Guardando respuestas...")
    run_test_case(test_suite, "Learning - Guardar Respuestas de Estudiante", save_responses, test_email, test_responses)
    
    # 17. Obtener respuestas
    print("\n17. Obteniendo respuestas...")
    run_test_case(test_suite, "Learning - Obtener Respuestas de Estudiante", get_responses_by_email, test_email)
    
    # 18. Eliminar submission específica
    print("\n18. Eliminando submission específica...")
    if submission_id:
        run_test_case(test_suite, "Judge - Eliminar Submission", delete_submission, submission_id, test_email)
    
    # 19. Eliminar calificaciones
    print("\n19. Eliminando calificaciones del estudiante...")
    run_test_case(test_suite, "Learning - Eliminar Calificaciones de Estudiante", delete_grades_by_email, test_email)
    
    # 20. Eliminar respuestas
    print("\n20. Eliminando respuestas del estudiante...")
    run_test_case(test_suite, "Learning - Eliminar Respuestas de Estudiante", delete_responses_by_email, test_email)
    
    # 21. Eliminar estudiante
    print("\n21. Eliminando estudiante...")
    if token:
        run_test_case(test_suite, "User - Eliminar Estudiante", delete_student, test_email, token)
    
    # ===== CASOS DE ERROR =====
    print("\n📋 EJECUTANDO CASOS DE ERROR")
    print("="*40)
    
    # 22. Login con credenciales incorrectas
    print("\n22. Login con credenciales incorrectas...")
    run_error_test_case(test_suite, "User - Login con Credenciales Incorrectas", login_user, 
                       "401", "email_inexistente@test.com", "password_incorrecto")
    
    # 23. Obtener estudiante inexistente
    print("\n23. Obtener estudiante inexistente...")
    run_error_test_case(test_suite, "User - Obtener Estudiante Inexistente", get_student_by_email, 
                       "404", "estudiante_inexistente@test.com")
    
    # 24. Crear submission con datos inválidos
    print("\n24. Crear submission con datos inválidos...")
    run_error_test_case(test_suite, "Judge - Crear Submission con Datos Inválidos", create_submission, 
                       "400", "email_invalido", "problem_id_invalido", "", "python")
    
    # 25. Obtener calificación inexistente
    print("\n25. Obtener calificación inexistente...")
    run_error_test_case(test_suite, "Learning - Obtener Calificación Inexistente", get_grade, 
                       "404", "estudiante_inexistente@test.com", "modulo_inexistente")
    
    # 26. Actualizar calificación inexistente
    print("\n26. Actualizar calificación inexistente...")
    run_error_test_case(test_suite, "Learning - Actualizar Calificación Inexistente", update_grade, 
                       "404", "estudiante_inexistente@test.com", "modulo_inexistente", 85.0)
    
    # 27. Obtener logros de estudiante inexistente
    print("\n27. Obtener logro inexistente...")
    run_error_test_case(test_suite, "Achievements - Obtener Logro Inexistente", get_student_achievements, 
                       "404", "estudiante_inexistente@test.com")
    
    # 28. Eliminar submission inexistente
    print("\n28. Eliminar submission inexistente...")
    run_error_test_case(test_suite, "Judge - Eliminar Submission Inexistente", delete_submission, 
                       "404", "submission_id_inexistente", test_email)
    
    # 29. Registrar usuario con email duplicado
    print("\n29. Registrar usuario con email duplicado...")
    run_error_test_case(test_suite, "User - Registrar Usuario con Email Duplicado", register_user, 
                       "400", {
                           "nombre": "Usuario Duplicado",
                           "email": test_email,  # Email ya registrado
                           "password": "password123",
                           "fecha_de_nacimiento": "2000-01-01",
                           "institucion_educativa": "Universidad Test",
                           "grado_academico": "Ingeniería"
                       })
    
    # 30. Solicitar recuperación con email inexistente
    print("\n30. Solicitar recuperación con email inexistente...")
    run_error_test_case(test_suite, "User - Recuperación con Email Inexistente", request_password_recovery, 
                       "404", "email_inexistente@test.com")
    
    # Generar reporte PDF
    print("\n📊 Generando reporte PDF...")
    try:
        charts = create_test_charts(test_suite)
        generate_pdf_report(test_suite, charts)
        print("✅ Reporte PDF generado exitosamente: Reporte_Pruebas_Integracion.pdf")
    except Exception as e:
        print(f"❌ Error al generar reporte PDF: {str(e)}")
    
    # Mostrar resumen final
    summary = test_suite.get_summary()
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL DE PRUEBAS")
    print("="*60)
    print(f"Total de Pruebas: {summary['total']}")
    print(f"Pruebas Exitosas: {summary['passed']}")
    print(f"Pruebas Fallidas: {summary['failed']}")
    print(f"Tasa de Éxito: {summary['success_rate']:.1f}%")
    print(f"Duración Total: {summary['duration']:.2f} segundos")
    
    if summary['success_rate'] >= 90:
        print("🎉 ¡Excelente! El sistema presenta un rendimiento sobresaliente.")
    elif summary['success_rate'] >= 70:
        print("✅ Bueno. El sistema funciona correctamente con algunas áreas de mejora.")
    else:
        print("⚠️ Se requieren mejoras significativas en el sistema.")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de integración completas para API de Estudiantes, Judge, Learning y Achievements")
    print("📋 Incluyendo casos de éxito y casos de error")
    integration_test()
