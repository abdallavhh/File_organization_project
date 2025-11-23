import os
import time
from datetime import datetime
from student import Student

class FileManager:
    """
    Manages file operations for student records.
    Supports Fixed-Length and Delimited formats.
    """
    
    TYPE_FIXED = "FIXED"
    TYPE_DELIMITED = "DELIMITED"
    
    # Header constants
    HEADER_PREFIX = "HEADER:"
    
    @staticmethod
    def create_file(filename: str, file_type: str, delimiter: str = "|"):
        """
        Creates a new file with a header record.
        Header format: HEADER:TYPE=FIXED,DATE=2023-10-27
        or HEADER:TYPE=DELIMITED,DELIMITER=|,DATE=2023-10-27
        """
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if file_type == FileManager.TYPE_FIXED:
            # For fixed, we might store field lengths in header, but for this assignment
            # we know them from Student class. We'll store basic metadata.
            header = f"{FileManager.HEADER_PREFIX}TYPE={file_type},DATE={date_str},FIELDS=ID|Name|GPA|Dept"
        else:
            header = f"{FileManager.HEADER_PREFIX}TYPE={file_type},DELIMITER={delimiter},DATE={date_str},FIELDS=ID|Name|GPA|Dept"
            
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(header + "\n")
            
    @staticmethod
    def get_file_metadata(filename: str):
        """
        Reads the header and returns metadata dict.
        """
        if not os.path.exists(filename):
            raise FileNotFoundError("File does not exist.")
            
        with open(filename, 'r', encoding='utf-8') as f:
            header_line = f.readline().strip()
            
        if not header_line.startswith(FileManager.HEADER_PREFIX):
            raise ValueError("Invalid file format: Missing header.")
            
        # Parse header
        content = header_line[len(FileManager.HEADER_PREFIX):]
        parts = content.split(',')
        metadata = {}
        for part in parts:
            if '=' in part:
                key, value = part.split('=', 1)
                metadata[key] = value
                
        return metadata

    @staticmethod
    def add_student(filename: str, student: Student):
        """
        Appends a student record to the file.
        """
        metadata = FileManager.get_file_metadata(filename)
        file_type = metadata.get('TYPE')
        
        with open(filename, 'a', encoding='utf-8') as f:
            if file_type == FileManager.TYPE_FIXED:
                record = student.to_fixed_length()
                f.write(record + "\n")
            elif file_type == FileManager.TYPE_DELIMITED:
                delimiter = metadata.get('DELIMITER', '|')
                record = student.to_delimited(delimiter)
                f.write(record + "\n")
            else:
                raise ValueError(f"Unknown file type: {file_type}")

    @staticmethod
    def read_all(filename: str):
        """
        Reads all student records from the file.
        Returns a list of Student objects.
        """
        metadata = FileManager.get_file_metadata(filename)
        file_type = metadata.get('TYPE')
        delimiter = metadata.get('DELIMITER', '|')
        
        students = []
        with open(filename, 'r', encoding='utf-8') as f:
            # Skip header
            f.readline()
            
            for line in f:
                line = line.strip('\n') # Keep spaces for fixed length, just remove newline
                if not line:
                    continue
                    
                try:
                    if file_type == FileManager.TYPE_FIXED:
                        student = Student.from_fixed_length(line)
                    else:
                        student = Student.from_delimited(line, delimiter)
                    students.append(student)
                except ValueError:
                    # Skip malformed lines or handle error
                    continue
                    
        return students

    @staticmethod
    def search_student(filename: str, student_id: int):
        """
        Sequentially searches for a student by ID.
        Returns (Student, time_taken_ms) or (None, time_taken_ms).
        """
        start_time = time.time()
        
        students = FileManager.read_all(filename)
        for student in students:
            if student.id == student_id:
                end_time = time.time()
                return student, (end_time - start_time) * 1000
                
        end_time = time.time()
        return None, (end_time - start_time) * 1000

    @staticmethod
    def get_record_by_rrn(filename: str, rrn: int):
        """
        Directly accesses a record by Relative Record Number (RRN).
        Only works for FIXED length files.
        RRN is 0-indexed (0 is the first student record after header).
        """
        metadata = FileManager.get_file_metadata(filename)
        if metadata.get('TYPE') != FileManager.TYPE_FIXED:
            raise ValueError("RRN access is only supported for Fixed-Length files.")
            
        # Calculate record length in BYTES
        # ID(5) + Name(20) + GPA(4) + Dept(10) = 39 bytes.
        # Plus newline. 
        # On Windows with 'w' mode, newline is \r\n (2 bytes). On Linux \n (1 byte).
        # However, we are now using encoding='utf-8'.
        # If we write with 'w', Python handles newline translation.
        # To effectively seek, we should open in BINARY mode or know the exact newline char.
        # Let's assume standard newline behavior for the platform or enforce one.
        # But we can't easily enforce it without rewriting create_file.
        # Let's try to detect it from the header line.
        
        record_len_bytes = 39
        
        with open(filename, 'rb') as f:
            header_bytes = f.readline()
            header_offset = len(header_bytes)
            
            # Determine newline size from header
            # If header ends with \r\n, it's 2 bytes.
            if header_bytes.endswith(b'\r\n'):
                newline_len = 2
            else:
                newline_len = 1
                
            full_record_len = record_len_bytes + newline_len
            
            # Calculate target offset
            target_offset = header_offset + (rrn * full_record_len)
            
            f.seek(target_offset)
            record_bytes = f.readline()
            
            if not record_bytes:
                return None
                
            # Check if we got a full record (ignoring potential EOF missing newline)
            # If it's the last record, it might not have a newline if manually edited, 
            # but our app writes newlines.
            # Let's just check if we got at least record_len_bytes
            if len(record_bytes) < record_len_bytes:
                 return None

            try:
                line = record_bytes.decode('utf-8').strip('\r\n')
                return Student.from_fixed_length(line)
            except Exception:
                return None

    @staticmethod
    def _create_header_string(metadata: dict) -> str:
        """
        Reconstructs the header string from metadata.
        """
        file_type = metadata.get('TYPE')
        date_str = metadata.get('DATE')
        
        if file_type == FileManager.TYPE_FIXED:
            return f"{FileManager.HEADER_PREFIX}TYPE={file_type},DATE={date_str},FIELDS=ID|Name|GPA|Dept"
        else:
            delimiter = metadata.get('DELIMITER', '|')
            return f"{FileManager.HEADER_PREFIX}TYPE={file_type},DELIMITER={delimiter},DATE={date_str},FIELDS=ID|Name|GPA|Dept"

    @staticmethod
    def delete_student(filename: str, student_id: int):
        """
        Deletes a student by ID.
        """
        students = FileManager.read_all(filename)
        metadata = FileManager.get_file_metadata(filename)
        file_type = metadata.get('TYPE')
        delimiter = metadata.get('DELIMITER', '|')
        
        found = False
        new_students = []
        for s in students:
            if s.id == student_id:
                found = True
                continue
            new_students.append(s)
            
        if found:
            header = FileManager._create_header_string(metadata)
                
            with open(filename, 'w', encoding='utf-8') as f_write:
                f_write.write(header + "\n")
                for s in new_students:
                    if file_type == FileManager.TYPE_FIXED:
                        f_write.write(s.to_fixed_length() + "\n")
                    else:
                        f_write.write(s.to_delimited(delimiter) + "\n")
            return True
        return False

    @staticmethod
    def update_student(filename: str, student_id: int, new_student_data: Student):
        """
        Updates a student record.
        """
        students = FileManager.read_all(filename)
        metadata = FileManager.get_file_metadata(filename)
        file_type = metadata.get('TYPE')
        delimiter = metadata.get('DELIMITER', '|')
        
        found = False
        for i, s in enumerate(students):
            if s.id == student_id:
                students[i] = new_student_data
                found = True
                break
        
        if found:
            header = FileManager._create_header_string(metadata)
            with open(filename, 'w', encoding='utf-8') as f_write:
                f_write.write(header + "\n")
                for s in students:
                    if file_type == FileManager.TYPE_FIXED:
                        f_write.write(s.to_fixed_length() + "\n")
                    else:
                        f_write.write(s.to_delimited(delimiter) + "\n")
            return True
        return False
                
    @staticmethod
    def export_to_csv(filename: str, output_path: str):
        """
        Exports all students from the given file to a CSV file.
        """
        import csv
        students = FileManager.read_all(filename)
        
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(['ID', 'Name', 'GPA', 'Department'])
            # Write data
            for s in students:
                writer.writerow([s.id, s.name, s.gpa, s.dept])
                
    @staticmethod
    def export_to_excel(filename: str, output_path: str):
        """
        Exports all students from the given file to an Excel file.
        Requires pandas and openpyxl.
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for Excel export. Please install it.")
            
        students = FileManager.read_all(filename)
        
        data = []
        for s in students:
            data.append({
                'ID': s.id,
                'Name': s.name,
                'GPA': s.gpa,
                'Department': s.dept
            })
            
        df = pd.DataFrame(data)
        df.to_excel(output_path, index=False)

    @staticmethod
    def import_from_csv(csv_path: str, target_filename: str, target_type: str):
        """
        Imports students from a CSV file into a new data file.
        """
        import csv
        
        if os.path.exists(target_filename):
            os.remove(target_filename)
            
        FileManager.create_file(target_filename, target_type)
        
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            # Check if header exists and matches expected fields roughly
            # We assume CSV has headers: ID, Name, GPA, Department (or Dept)
            
            for row in reader:
                # Map CSV columns to Student fields
                # Try to be flexible with column names
                s_id = row.get('ID') or row.get('id')
                s_name = row.get('Name') or row.get('name')
                s_gpa = row.get('GPA') or row.get('gpa')
                s_dept = row.get('Department') or row.get('Dept') or row.get('dept')
                
                if s_id and s_name:
                    try:
                        student = Student(int(s_id), s_name, float(s_gpa), s_dept)
                        FileManager.add_student(target_filename, student)
                    except ValueError:
                        continue # Skip invalid rows

    @staticmethod
    def convert_file_structure(filename: str, new_type: str):
        """
        Converts the file to a different structure type (Fixed <-> Delimited).
        Returns the new filename.
        """
        students = FileManager.read_all(filename)
        
        # Create new filename
        base, ext = os.path.splitext(filename)
        new_filename = f"{base}_converted{ext}"
        
        if os.path.exists(new_filename):
            os.remove(new_filename)
            
        FileManager.create_file(new_filename, new_type)
        
        for s in students:
            FileManager.add_student(new_filename, s)
            
        return new_filename

    @staticmethod
    def compress_file(filename: str):
        """
        Compresses the file using gzip.
        Returns the compressed filename.
        """
        import gzip
        import shutil
        
        compressed_filename = f"{filename}.gz"
        
        with open(filename, 'rb') as f_in:
            with gzip.open(compressed_filename, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
                
        return compressed_filename

    @staticmethod
    def decompress_file(filename: str):
        """
        Decompresses a gzip file.
        Returns the decompressed filename (removes .gz).
        """
        import gzip
        import shutil
        
        if not filename.endswith('.gz'):
            raise ValueError("File must end with .gz")
            
        decompressed_filename = filename[:-3]
        
        with gzip.open(filename, 'rb') as f_in:
            with open(decompressed_filename, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
                
        return decompressed_filename

