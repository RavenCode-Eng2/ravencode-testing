import time
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from test_logger import TestLogger

BASE_URL = "http://localhost:3000"

def login(driver, email, password, logger):
    driver.get(BASE_URL)
    time.sleep(1)
    try:
        email_input = driver.find_element(By.ID, "email")
        password_input = driver.find_element(By.ID, "password")
        email_input.clear()
        password_input.clear()
        email_input.send_keys(email)
        password_input.send_keys(password)
        # Click the login button (by visible text)
        login_button = driver.find_element(By.XPATH, "//button[contains(., 'Iniciar sesión')]")
        login_button.click()
        time.sleep(2)
        logger.add_log(f"Attempted login with {email}", "INFO")
        return True
    except Exception as e:
        logger.add_log(f"Login form not found: {str(e)}", "FAIL")
        return False

def register_user(driver, logger, email=None):
    driver.get(BASE_URL + "/register")
    time.sleep(1)
    try:
        # Generate a unique email if not provided
        if not email:
            email = f"testuser_{int(time.time())}_{random.randint(1000,9999)}@example.com"
        # Fill the form
        driver.find_element(By.ID, "nombre").send_keys("Test User")
        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "password").send_keys("TestPassword123")
        driver.find_element(By.ID, "confirmPassword").send_keys("TestPassword123")
        driver.find_element(By.ID, "fecha_de_nacimiento").send_keys("2000-01-01")
        driver.find_element(By.ID, "institucion_educativa").send_keys("Test School")
        driver.find_element(By.ID, "grado_academico").send_keys("Test Grade")
        # Accept terms
        driver.find_element(By.ID, "terms").click()
        # Click the register button
        register_button = driver.find_element(By.XPATH, "//button[contains(., 'Crear cuenta')]")
        register_button.click()
        time.sleep(2)
        logger.add_log(f"Attempted registration with {email}", "INFO")
        return email
    except Exception as e:
        logger.add_log(f"Registration form not found or failed: {str(e)}", "FAIL")
        return None

def test_login_valid_user(driver, logger):
    logger.add_log("Testing valid user login", "INFO")
    login(driver, "camurcioa@unal.edu.co", "RavenCode123", logger)
    try:
        # Wait for a unique dashboard element (adjust XPATH as needed)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Bienvenido')]"))
        )
        logger.add_log("Valid user login: PASS", "PASS")
        return True
    except Exception:
        logger.add_log(
            f"Valid user login: FAIL (URL after login: {driver.current_url}, Title: {driver.title})",
            "FAIL"
        )
        return False

def test_login_invalid_user(driver, logger):
    logger.add_log("Testing invalid user login", "INFO")
    login(driver, "invalid@example.com", "wrongpassword", logger)
    time.sleep(1)
    if "Dashboard" not in driver.title:
        logger.add_log("Invalid user login: PASS", "PASS")
        return True
    else:
        logger.add_log("Invalid user login: FAIL", "FAIL")
        return False

def test_register_new_user(driver, logger):
    logger.add_log("Testing registration of a new user", "INFO")
    email = register_user(driver, logger)
    try:
        # Wait for redirect to login page (after successful registration)
        WebDriverWait(driver, 10).until(EC.url_contains("/login"))
        logger.add_log("New user registration: PASS", "PASS")
        return email  # Return email for reuse in duplicate test
    except Exception:
        logger.add_log(
            f"New user registration: FAIL (URL after register: {driver.current_url}, Title: {driver.title})",
            "FAIL"
        )
        return None

def test_register_existing_user(driver, logger, email):
    logger.add_log("Testing registration of an existing user", "INFO")
    register_user(driver, logger, email=email)
    try:
        time.sleep(2)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'react-hot-toast') or contains(@class, 'toaster')]"))
        )
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Email already registered') or contains(text(), 'Error al registrar')]"))
        )
        logger.add_log("Existing user registration: PASS (error toast shown as expected)", "PASS")
        return True
    except Exception:
        logger.add_log(
            f"Existing user registration: FAIL (URL after register: {driver.current_url}, Title: {driver.title})",
            "FAIL"
        )
        return False

def test_forgot_password_request(driver, logger, test_email):
    logger.add_log("Testing forgot password request", "INFO")
    driver.get(BASE_URL + "/forgot-password")
    time.sleep(1)
    try:
        email_input = driver.find_element(By.ID, "email")
        email_input.clear()
        email_input.send_keys(test_email)
        send_button = driver.find_element(By.XPATH, "//button[contains(., 'Enviar código')]")
        send_button.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Código de recuperación enviado')]"))
        )
        logger.add_log("Forgot password request: PASS (success toast shown)", "PASS")
        return True
    except Exception as e:
        logger.add_log(
            f"Forgot password request: FAIL ({str(e)})",
            "FAIL"
        )
        return False

def test_dashboard(driver, logger, user_email, user_password, expected_name="Usuario"):
    logger.add_log("Testing dashboard page", "INFO")
    # Log in first
    driver.get(BASE_URL + "/login")
    time.sleep(1)
    try:
        email_input = driver.find_element(By.ID, "email")
        password_input = driver.find_element(By.ID, "password")
        email_input.clear()
        password_input.clear()
        email_input.send_keys(user_email)
        password_input.send_keys(user_password)
        login_button = driver.find_element(By.XPATH, "//button[contains(., 'Iniciar sesión')]")
        login_button.click()
        # Wait for dashboard greeting
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//h2[contains(., '¡Bienvenido de nuevo')]"))
        )
        # Check greeting contains expected name
        greeting = driver.find_element(By.XPATH, "//h2[contains(., '¡Bienvenido de nuevo')]").text
        if expected_name not in greeting:
            logger.add_log(f"Greeting does not contain expected name: {greeting}", "FAIL")
            return False
        # Check ProgressCard title
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Continúa Tu Aventura')]"))
        )
        # Check at least one module title
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Fundamentos de Python')]"))
        )
        # Check Logros section
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Logros')]"))
        )
        logger.add_log("Dashboard page: PASS (all key elements found)", "PASS")
        return True
    except Exception as e:
        logger.add_log(
            f"Dashboard page: FAIL ({str(e)})",
            "FAIL"
        )
        return False

def test_settings_update(driver, logger, user_email, user_password, new_name, new_school, new_grade):
    logger.add_log("Testing settings page update", "INFO")
    # Log in first
    driver.get(BASE_URL + "/login")
    time.sleep(1)
    try:
        email_input = driver.find_element(By.ID, "email")
        password_input = driver.find_element(By.ID, "password")
        email_input.clear()
        password_input.clear()
        email_input.send_keys(user_email)
        password_input.send_keys(user_password)
        login_button = driver.find_element(By.XPATH, "//button[contains(., 'Iniciar sesión')]")
        login_button.click()
        # Wait for dashboard to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Bienvenido')]"))
        )
        # Go to settings page
        driver.get(BASE_URL + "/settings")
        # Wait for settings form to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Configuración de Perfil')]"))
        )
        # Change the name, school, and grade fields
        name_input = driver.find_element(By.ID, "Nombre")
        name_input.clear()
        name_input.send_keys(new_name)
        school_input = driver.find_element(By.ID, "Institucion_educativa")
        school_input.clear()
        school_input.send_keys(new_school)
        grade_input = driver.find_element(By.ID, "Grado_academico")
        grade_input.clear()
        grade_input.send_keys(new_grade)
        # Submit the form
        save_button = driver.find_element(By.XPATH, "//button[contains(., 'Guardar cambios')]")
        save_button.click()
        # Wait for success toast
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Perfil actualizado exitosamente')]"))
        )
        logger.add_log("Settings page update: PASS (profile updated successfully)", "PASS")
        return True
    except Exception as e:
        logger.add_log(
            f"Settings page update: FAIL ({str(e)})",
            "FAIL"
        )
        return False

def main():
    logger = TestLogger("Frontend Login & Registration Integration Test")
    logger.start_test()
    options = Options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    try:
        valid = test_login_valid_user(driver, logger)
        invalid = test_login_invalid_user(driver, logger)
        new_email = test_register_new_user(driver, logger)
        if new_email:
            duplicate = test_register_existing_user(driver, logger, new_email)
        else:
            duplicate = False
        forgot_pass = test_forgot_password_request(driver, logger, "ciamurciamur@gmail.com")
        dashboard_pass = test_dashboard(driver, logger, "camurcioa@unal.edu.co", "RavenCode123", expected_name="Carlos")  # Change expected_name as needed
        settings_pass = test_settings_update(driver, logger, "tatianitalamasbonita@example.com", "Tatis123", "Tatianita Rodriguez", "Colegio Mis Primeras Travesuras", "2")
        overall = valid and invalid and new_email is not None and duplicate and forgot_pass and dashboard_pass and settings_pass
    except Exception as e:
        logger.add_log(f"Test execution error: {str(e)}", "FAIL")
        overall = False
    finally:
        driver.quit()
        logger.end_test()
        report_num = logger.generate_pdf()
        print(f"Report generated: frontend_integration_testing_report_{report_num:03d}.pdf")
        if overall:
            print("All tests passed.")
        else:
            print("Some tests failed.")

if __name__ == "__main__":
    main()
