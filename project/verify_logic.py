from student import Student
from file_manager import FileManager
import os

def test_fixed_length():
    print("--- Testing Fixed Length ---")
    filename = "test_fixed.txt"
    if os.path.exists(filename):
        os.remove(filename)
        
    # Create
    FileManager.create_file(filename, FileManager.TYPE_FIXED)
    print("File created.")
    
    # Add
    s1 = Student(1, "Alice", 3.8, "CS")
    s2 = Student(2, "Bob", 3.5, "Math")
    FileManager.add_student(filename, s1)
    FileManager.add_student(filename, s2)
    print("Students added.")
    
    # Read
    students = FileManager.read_all(filename)
    assert len(students) == 2
    assert students[0].name.strip() == "Alice"
    print("Read verification passed.")
    
    # Search
    s, t = FileManager.search_student(filename, 2)
    assert s.name.strip() == "Bob"
    print(f"Search passed. Time: {t}ms")
    
    # RRN
    s_rrn = FileManager.get_record_by_rrn(filename, 0)
    assert s_rrn.name.strip() == "Alice"
    print("RRN 0 passed.")
    
    s_rrn2 = FileManager.get_record_by_rrn(filename, 1)
    assert s_rrn2.name.strip() == "Bob"
    print("RRN 1 passed.")
    
    # Delete
    FileManager.delete_student(filename, 1)
    students = FileManager.read_all(filename)
    assert len(students) == 1
    assert students[0].name.strip() == "Bob"
    print("Delete passed.")

def test_delimited():
    print("\n--- Testing Delimited ---")
    filename = "test_delim.txt"
    if os.path.exists(filename):
        os.remove(filename)
        
    # Create
    FileManager.create_file(filename, FileManager.TYPE_DELIMITED)
    print("File created.")
    
    # Add
    s1 = Student(10, "Charlie", 3.9, "Physics")
    FileManager.add_student(filename, s1)
    print("Student added.")
    
    # Read
    students = FileManager.read_all(filename)
    assert len(students) == 1
    assert students[0].name == "Charlie"
    print("Read verification passed.")

if __name__ == "__main__":
    try:
        test_fixed_length()
        test_delimited()
        print("\nALL TESTS PASSED!")
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
    except Exception as e:
        print(f"\nERROR: {e}")
