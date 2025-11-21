from student import Student
from file_manager import FileManager
import os

def test_export():
    print("--- Testing Export ---")
    filename = "test_export.txt"
    if os.path.exists(filename):
        os.remove(filename)
        
    # Create and Populate
    FileManager.create_file(filename, FileManager.TYPE_DELIMITED)
    s1 = Student(1, "Alice", 3.8, "CS")
    s2 = Student(2, "Bob", 3.5, "Math")
    FileManager.add_student(filename, s1)
    FileManager.add_student(filename, s2)
    
    # Test CSV
    csv_out = "test_export.csv"
    if os.path.exists(csv_out):
        os.remove(csv_out)
    
    print("Exporting to CSV...")
    FileManager.export_to_csv(filename, csv_out)
    
    if os.path.exists(csv_out):
        print("CSV file created.")
        with open(csv_out, 'r') as f:
            content = f.read()
            print("CSV Content Preview:")
            print(content)
            assert "Alice" in content
            assert "Bob" in content
    else:
        print("FAILED: CSV file not created.")

    # Test Excel
    xlsx_out = "test_export.xlsx"
    if os.path.exists(xlsx_out):
        os.remove(xlsx_out)
        
    print("\nExporting to Excel...")
    try:
        FileManager.export_to_excel(filename, xlsx_out)
        if os.path.exists(xlsx_out):
            print("Excel file created.")
        else:
            print("FAILED: Excel file not created.")
    except ImportError as e:
        print(f"SKIPPED: {e}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_export()
