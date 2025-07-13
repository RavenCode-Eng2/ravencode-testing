# RavenCode - Sistema de Pruebas de Integración

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![ReportLab](https://img.shields.io/badge/ReportLab-4.0+-green.svg)](https://www.reportlab.com/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.0+-orange.svg)](https://matplotlib.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Descripción

Sistema completo de pruebas de integración para la plataforma **RavenCode**, un LMS (Learning Management System) desarrollado con arquitectura de microservicios. Este proyecto incluye una suite automatizada de 30 pruebas que cubren todos los servicios del sistema y genera reportes PDF profesionales con análisis gráfico detallado.

## 🏗️ Arquitectura del Sistema

RavenCode está compuesto por 4 microservicios principales:

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **User Service** | 8001 | Gestión de usuarios, autenticación y perfiles de estudiantes |
| **Judge Service** | 8000 | Evaluación y procesamiento de código enviado por estudiantes |
| **Learning Service** | 8002 | Gestión de calificaciones, respuestas y contenido educativo |
| **Achievements Service** | 8003 | Sistema de logros, badges y gamificación |

## 🚀 Características Principales

### ✅ Suite de Pruebas Completa
- **30 pruebas de integración** automatizadas
- Cobertura completa de todos los microservicios
- Pruebas de casos exitosos y casos de error
- Medición de tiempos de ejecución
- Categorización por tipo de servicio

### 📊 Generación de Reportes PDF
- **Reportes profesionales** con diseño elegante
- **Gráficos estadísticos** con matplotlib y seaborn
- **Análisis visual** de rendimiento y resultados
- **Métricas detalladas** de cada servicio
- **Información de sistema** y versiones

### 🎨 Diseño Elegante
- Paleta de colores profesional
- Tipografías optimizadas (Helvetica)
- Layout moderno y responsive
- Logos institucionales integrados
- Pie de página informativo

## 📦 Instalación

### Prerrequisitos
- Python 3.8 o superior
- Acceso a los microservicios RavenCode ejecutándose

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd ravencode-testing
```

2. **Crear entorno virtual**
```bash
python -m venv venv
```

3. **Activar entorno virtual**
   - **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   - **Mac/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

## 🧪 Ejecución de Pruebas

### Ejecutar Suite Completa
```bash
python Test/BackEnd-Test.py
```

### Resultados
- Se ejecutarán automáticamente 30 pruebas
- Se generará el archivo `Reporte_Pruebas_Integracion.pdf`
- Se mostrarán resultados en consola en tiempo real

### Estructura de Pruebas

#### User Service (8 pruebas)
- Registro de usuarios
- Autenticación y login
- Recuperación de contraseñas
- Gestión de perfiles de estudiantes
- Operaciones CRUD completas

#### Judge Service (8 pruebas)
- Envío de código para evaluación
- Consulta de submissions
- Actualización de código
- Eliminación de submissions
- Validaciones de errores

#### Learning Service (8 pruebas)
- Gestión de calificaciones
- Manejo de respuestas de estudiantes
- Operaciones de lectura y escritura
- Validaciones de datos

#### Achievements Service (6 pruebas)
- Creación de logros
- Consulta de achievements
- Gestión de puntuaciones
- Validaciones de sistema

## 📈 Reportes Generados

### Contenido del PDF
- **Información del sistema** y fecha de generación
- **Resumen ejecutivo** con métricas clave
- **Gráficos estadísticos**:
  - Gráfico de barras de resultados
  - Gráfico de pastel de distribución
  - Gráfico por servicio
- **Tabla detallada** de todas las pruebas
- **Análisis de rendimiento** y tiempos
- **Conclusiones** y recomendaciones

### Ejemplo de Métricas
```
Total de Pruebas: 30
Pruebas Exitosas: 28
Pruebas Fallidas: 2
Tasa de Éxito: 93.3%
Duración Total: 45.2 segundos
```

## 🛠️ Configuración

### Variables de Entorno
```bash
# URLs de los microservicios (por defecto)
USER_SERVICE_URL=http://localhost:8001
JUDGE_SERVICE_URL=http://localhost:8000
LEARNING_SERVICE_URL=http://localhost:8002
ACHIEVEMENTS_SERVICE_URL=http://localhost:8003
```

### Personalización
- Modificar `Test/BackEnd-Test.py` para cambiar endpoints
- Ajustar estilos en la función `generate_pdf_report()`
- Personalizar gráficos en `create_test_charts()`

## 📁 Estructura del Proyecto

```
ravencode-testing/
├── Test/
│   ├── BackEnd-Test.py          # Script principal de pruebas
│   ├── utils.py                 # Utilidades auxiliares
│   ├── logoUNAL.png            # Logo de la universidad
│   └── ravenCode1.png          # Logo de RavenCode
├── requirements.txt             # Dependencias del proyecto
├── README.md                   # Este archivo
├── CHANGELOG.md               # Historial de cambios
└── Reporte_Pruebas_Integracion.pdf  # Reporte generado
```

## 🔧 Dependencias

### Principales
- `requests` - Llamadas HTTP a microservicios
- `reportlab` - Generación de PDFs
- `matplotlib` - Creación de gráficos
- `seaborn` - Estilos de gráficos
- `datetime` - Manejo de fechas y tiempos

### Completas
```
requests>=2.25.1
reportlab>=3.6.0
matplotlib>=3.3.0
seaborn>=0.11.0
```

## 🐛 Solución de Problemas

### Error: "Connection refused"
- Verificar que los microservicios estén ejecutándose
- Confirmar puertos correctos (8000, 8001, 8002, 8003)

### Error: "Module not found"
- Activar entorno virtual
- Reinstalar dependencias: `pip install -r requirements.txt`

### PDF no se genera
- Verificar permisos de escritura en el directorio
- Comprobar espacio en disco disponible





## 👥 Autores

- **Equipo RavenCode** - Universidad Nacional de Colombia
- **Sistema de Pruebas de Integración** - v1.0.0



 