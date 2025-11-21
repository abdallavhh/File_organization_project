class Student:
    """
    Represents a student with ID, Name, GPA, and Department.
    Includes methods for serialization to fixed-length and delimited formats.
    """
    
    # Fixed length configuration (in BYTES)
    FIELD_LENGTHS = {
        'id': 5,
        'name': 20,
        'gpa': 4,
        'dept': 10
    }
    
    def __init__(self, student_id: int, name: str, gpa: float, dept: str):
        self.id = student_id
        self.name = name
        self.gpa = gpa
        self.dept = dept

    def to_fixed_length(self) -> str:
        """
        Converts the student object to a fixed-length string record.
        ID(5), NAME(20), GPA(4), DEPT(10) - Lengths in BYTES.
        Returns a string that, when encoded in UTF-8, matches the byte lengths.
        """
        # Helper to pad/truncate to fixed bytes
        def format_field(value: str, length: int) -> str:
            # Encode to bytes
            b_val = str(value).encode('utf-8')
            # Truncate if too long
            if len(b_val) > length:
                b_val = b_val[:length]
                # Ensure we didn't cut a multi-byte char in half
                # If the last byte is a continuation byte (0x80-0xBF), remove it
                while b_val and (b_val[-1] & 0xC0) == 0x80:
                    b_val = b_val[:-1]
            # Pad with spaces
            b_val = b_val + b' ' * (length - len(b_val))
            # Decode back to string (this ensures it writes correctly as UTF-8)
            return b_val.decode('utf-8')

        id_str = format_field(str(self.id).zfill(self.FIELD_LENGTHS['id']), self.FIELD_LENGTHS['id'])
        
        # For ID, zfill operates on string, so we might need to be careful if ID was somehow unicode? 
        # But ID is int. str(int) is ASCII. So zfill is fine.
        # Actually, let's just use the helper for consistency, but zfill is string op.
        # Let's redo ID:
        # ID is usually ASCII digits.
        s_id = str(self.id).zfill(self.FIELD_LENGTHS['id'])
        # Ensure it fits (though 5 digits is max for 5 bytes)
        id_str = format_field(s_id, self.FIELD_LENGTHS['id'])

        name_str = format_field(self.name, self.FIELD_LENGTHS['name'])
        
        # GPA
        s_gpa = f"{self.gpa:.2f}"
        gpa_str = format_field(s_gpa, self.FIELD_LENGTHS['gpa'])
        
        # Dept
        dept_str = format_field(self.dept, self.FIELD_LENGTHS['dept'])
        
        return f"{id_str}{name_str}{gpa_str}{dept_str}"

    def to_delimited(self, delimiter: str = "|") -> str:
        """
        Converts the student object to a delimited string record.
        """
        return f"{self.id}{delimiter}{self.name}{delimiter}{self.gpa}{delimiter}{self.dept}"

    @classmethod
    def from_fixed_length(cls, record: str):
        """
        Creates a Student object from a fixed-length string record.
        Expects the record to be a string that was decoded from UTF-8 bytes.
        """
        # We need to operate on bytes to respect the field lengths
        b_record = record.encode('utf-8')
        
        expected_len = sum(cls.FIELD_LENGTHS.values())
        # Note: b_record length might be slightly different if we stripped newline before passing here?
        # The caller usually strips newline.
        
        if len(b_record) < expected_len:
             # It's possible that the record is short.
             # But let's try to parse what we have.
             pass
            
        offset = 0
        
        # ID
        l_id = cls.FIELD_LENGTHS['id']
        b_id = b_record[offset : offset + l_id]
        s_id = int(b_id.decode('utf-8').strip())
        offset += l_id
        
        # Name
        l_name = cls.FIELD_LENGTHS['name']
        b_name = b_record[offset : offset + l_name]
        s_name = b_name.decode('utf-8').strip()
        offset += l_name
        
        # GPA
        l_gpa = cls.FIELD_LENGTHS['gpa']
        b_gpa = b_record[offset : offset + l_gpa]
        s_gpa = float(b_gpa.decode('utf-8').strip())
        offset += l_gpa
        
        # Dept
        l_dept = cls.FIELD_LENGTHS['dept']
        b_dept = b_record[offset : offset + l_dept]
        s_dept = b_dept.decode('utf-8').strip()
        
        return cls(s_id, s_name, s_gpa, s_dept)

    @classmethod
    def from_delimited(cls, record: str, delimiter: str = "|"):
        """
        Creates a Student object from a delimited string record.
        """
        parts = record.split(delimiter)
        if len(parts) < 4:
            raise ValueError("Record does not have enough fields.")
            
        s_id = int(parts[0])
        s_name = parts[1]
        s_gpa = float(parts[2])
        s_dept = parts[3]
        
        return cls(s_id, s_name, s_gpa, s_dept)

    def __str__(self):
        return f"ID: {self.id}, Name: {self.name}, GPA: {self.gpa}, Dept: {self.dept}"
