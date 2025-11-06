import os
import platform
import subprocess
from PySide6.QtWidgets import QFileDialog, QMessageBox

def generate_output_path(input_path: str)->str:
    if not input_path:
        return ""
    
    dir_path = os.path.dirname(input_path)
    file_name = os.path.basename(input_path)
    name_without_ext, _ = os.path.splitext(file_name)
    new_file_name = f"{name_without_ext}_result.xlsx"
    return os.path.join(dir_path, new_file_name)

def browse_input_lineedit(line_edit_input, line_edit_output):
    path, _ = QFileDialog.getOpenFileName(
        None, "Select Excel File", "",
        "Excel Files (*.xlsx *.xls);;All Files (*)"
    )
    if path:
        line_edit_input.setText(path)
        output_path = generate_output_path(path)
        line_edit_output.setText(output_path)

def browse_output_lineedit(line_edit_output):
    path, _ = QFileDialog.getSaveFileName(
        None, "Save Ouput File", "",
        "Excel Files (*.xlsx *.xls);;All Files (*)"
    )
    if path:
        if not path.lower().endswith(('.xlsx', '.xls')):
            path += '.xlsx'
        line_edit_output.setText(path)

def open_excel_file(output_path: str, log_callback= None):
    if not output_path:
        QMessageBox.warning(None, "لم يتم تحديد مسار ملف الإخراج بعد", "مسار غير محدد .")
        return
    
    if not os.path.exists(output_path):
        QMessageBox.warning(None,"ملف غير موجود", f"لم يتم العثور على الملف:\n{output_path}")
        return 
    
    try:
        if platform.system() == "Windows":
            os.startfile(output_path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", output_path])
        else:
            subprocess.run(["xdg-open", output_path])
            
        if log_callback:
            log_callback(f"✅ تم فتح ملف Excel: {output_path}")
            
    except Exception as e:
        QMessageBox.critical(None, "خطأ في فتح الملف", f"حدث خطأ أثناء فتح الملف:\n{str(e)}")
        if log_callback:
            log_callback(f"❌ خطأ في فتح ملف Excel: {str(e)}")
