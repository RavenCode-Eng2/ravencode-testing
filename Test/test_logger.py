import time
import unicodedata
from datetime import datetime
from fpdf import FPDF
import os

class TestLogger:
    def __init__(self, test_name):
        self.test_name = test_name
        self.start_time = None
        self.end_time = None
        self.logs = []
        self.status = "PASSED"
        self.logo_path = os.path.join("assets", "unal_logo.png")  # Update with your logo filename

    def start_test(self):
        self.start_time = datetime.now()
        self.add_log("Test started", status="INFO")

    def end_test(self):
        self.end_time = datetime.now()
        self.add_log("Test ended", status="INFO")

    def add_log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append((timestamp, message, status))
        if status == "FAIL":
            self.status = "FAILED"

    def generate_pdf(self):
        # Use the current directory (Test) for assets, parent for report
        test_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(test_dir)
        report_num = 1
        while os.path.exists(os.path.join(parent_dir, f"frontend_integration_testing_report_{report_num:03d}.pdf")):
            report_num += 1

        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()

        # Add left logo (unal_logo.png)
        left_logo_path = os.path.join(test_dir, "assets", "unal_logo.png")
        if os.path.exists(left_logo_path):
            pdf.image(left_logo_path, x=10, y=10, w=30)
        # Add right logo (ravencode.png)
        right_logo_path = os.path.join(test_dir, "assets", "ravencode.png")
        if os.path.exists(right_logo_path):
            pdf.image(right_logo_path, x=170, y=10, w=30)

        # Move cursor below logos for header
        pdf.set_xy(0, 35)
        try:
            pdf.add_font('Arial', '', r'c:\windows\fonts\arial.ttf', uni=True)
            pdf.set_font('Arial', 'B', 16)
        except:
            pdf.set_font('Arial', 'B', 16)

        # Centered test report number
        pdf.set_x(0)
        pdf.cell(210, 10, f"Test Report #{report_num:03d}", ln=True, align='C')
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(210, 10, f"Test Name: {self.test_name}", ln=True, align='C')
        pdf.set_font('Arial', '', 11)
        if self.start_time:
            pdf.cell(210, 8, f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
        if self.end_time:
            pdf.cell(210, 8, f"End Time: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
            if self.start_time:
                duration = self.end_time - self.start_time
                pdf.cell(210, 8, f"Duration: {duration.total_seconds():.2f} seconds", ln=True, align='C')

        # Calculate pass/fail percentage
        pass_count = sum(1 for _, _, status in self.logs if status == "PASS")
        fail_count = sum(1 for _, _, status in self.logs if status == "FAIL")
        total = pass_count + fail_count
        percent = int(round((pass_count / total) * 100)) if total > 0 else 0
        status_line = f"Status: {self.status} ({percent}%)"
        pdf.cell(210, 8, status_line, ln=True, align='C')
        pdf.ln(8)

        # Table header (restore previous good alignment)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(30, 8, "Time", border=1)
        pdf.cell(110, 8, "Message", border=1)
        pdf.cell(40, 8, "Status", border=1, ln=True)
        row_height = 8

        for (timestamp, message, status) in self.logs:
            safe_message = unicodedata.normalize('NFKD', message).encode('ascii', 'ignore').decode('ascii')
            if len(safe_message) > 500:
                safe_message = safe_message[:500] + '...'
                pdf.set_font('Arial', '', 8)
            else:
                pdf.set_font('Arial', '', 9)
            x = pdf.get_x()
            y = pdf.get_y()
            message_lines = pdf.multi_cell(110, row_height, safe_message, border=0, align='L', split_only=True)
            n_lines = len(message_lines)
            cell_height = row_height * n_lines if n_lines > 0 else row_height
            # Time cell
            pdf.set_xy(x, y)
            pdf.cell(30, cell_height, timestamp, border=1)
            # Message cell
            pdf.set_xy(x + 30, y)
            pdf.multi_cell(110, row_height, safe_message, border=1)
            # Status cell
            pdf.set_xy(x + 140, y)
            pdf.cell(40, cell_height, status if status in ["PASS", "FAIL"] else status, border=1, ln=1)
        try:
            pdf.output(os.path.join(parent_dir, f"frontend_integration_testing_report_{report_num:03d}.pdf"))
        except UnicodeEncodeError:
            safe_path = os.path.join(parent_dir, f"frontend_integration_testing_report_{report_num:03d}.pdf").encode('ascii', 'ignore').decode('ascii')
            pdf.output(safe_path)
        return report_num
