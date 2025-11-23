import flet as ft
import os

from student import Student
from file_manager import FileManager

def main(page: ft.Page):
    page.title = "Student File Management System"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed="teal")
    page.window_width = 1100
    page.window_height = 850
    page.padding = 0 # Reset padding for layout

    # Global state
    current_file = None
    
    # --- UI Components (Global to Main) ---
    
    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        e.control.icon = "dark_mode" if page.theme_mode == ft.ThemeMode.LIGHT else "light_mode"
        page.update()
    
    # State controls
    file_name_input = ft.TextField(label="File Name", value="students.txt", width=400, border="underline", filled=True)
    file_type_dropdown = ft.Dropdown(
        label="File Type",
        width=400,
        options=[
            ft.dropdown.Option(FileManager.TYPE_FIXED),
            ft.dropdown.Option(FileManager.TYPE_DELIMITED),
        ],
        value=FileManager.TYPE_FIXED,
        border="underline", filled=True
    )
    active_file_text = ft.Text(f"Active File: {current_file if current_file else 'No file selected'}", size=16, weight=ft.FontWeight.BOLD)

    def update_active_file_text():
        active_file_text.value = f"Active File: {current_file if current_file else 'No file selected'}"
        active_file_text.update()

    # File Pickers
    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            selected_file = e.files[0].path
            nonlocal current_file
            current_file = selected_file
            
            # Update input to match selected file
            file_name_input.value = selected_file
            file_name_input.update()
            
            try:
                meta = FileManager.get_file_metadata(current_file)
                page.snack_bar = ft.SnackBar(ft.Text(f"Selected '{current_file}'. Type: {meta.get('TYPE')}"), bgcolor="blue")
                page.snack_bar.open = True
                update_active_file_text()
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error loading file: {str(ex)}"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(pick_files_dialog)

    def csv_picker_result(e: ft.FilePickerResultEvent):
        if e.files:
            csv_path = e.files[0].path
            target_file = file_name_input.value
            target_type = file_type_dropdown.value
            try:
                FileManager.import_from_csv(csv_path, target_file, target_type)
                page.snack_bar = ft.SnackBar(ft.Text(f"Imported from '{csv_path}' to '{target_file}'"), bgcolor="green")
                page.snack_bar.open = True
                nonlocal current_file
                current_file = target_file
                update_active_file_text()
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Import Error: {str(ex)}"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

    csv_import_dialog = ft.FilePicker(on_result=csv_picker_result)
    page.overlay.append(csv_import_dialog)

    def on_gz_picked(e: ft.FilePickerResultEvent):
        if e.files:
            gz_path = e.files[0].path
            try:
                decomp_file = FileManager.decompress_file(gz_path)
                page.snack_bar = ft.SnackBar(ft.Text(f"Decompressed to '{decomp_file}'"), bgcolor="green")
                page.snack_bar.open = True
                nonlocal current_file
                current_file = decomp_file
                update_active_file_text()
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
    
    gz_picker = ft.FilePicker(on_result=on_gz_picked)
    page.overlay.append(gz_picker)

    def on_file_to_compress_picked(e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            try:
                comp_file = FileManager.compress_file(file_path)
                page.snack_bar = ft.SnackBar(ft.Text(f"Compressed to '{comp_file}'"), bgcolor="green")
                page.snack_bar.open = True
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

    compress_picker = ft.FilePicker(on_result=on_file_to_compress_picked)
    page.overlay.append(compress_picker)

    # Actions
    def create_file_click(e):
        try:
            FileManager.create_file(file_name_input.value, file_type_dropdown.value)
            page.snack_bar = ft.SnackBar(ft.Text(f"File '{file_name_input.value}' created successfully!"), bgcolor="green")
            page.snack_bar.open = True
            nonlocal current_file
            current_file = file_name_input.value
            update_active_file_text()
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def load_file_click(e):
        if os.path.exists(file_name_input.value):
            nonlocal current_file
            current_file = file_name_input.value
            
            # Check if it's a GZ file
            if current_file.endswith('.gz'):
                 page.snack_bar = ft.SnackBar(ft.Text(f"Selected compressed file '{current_file}'. Please decompress it first."), bgcolor="orange")
                 page.snack_bar.open = True
                 update_active_file_text()
                 page.update()
                 return

            try:
                meta = FileManager.get_file_metadata(current_file)
                page.snack_bar = ft.SnackBar(ft.Text(f"Loaded '{current_file}'. Type: {meta.get('TYPE')}"), bgcolor="blue")
                page.snack_bar.open = True
                update_active_file_text()
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error loading file: {str(ex)}"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("File not found!"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def convert_click(e):
        nonlocal current_file
        if not current_file:
            page.snack_bar = ft.SnackBar(ft.Text("No active file to convert!"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return
            
        try:
            # Toggle type
            meta = FileManager.get_file_metadata(current_file)
            current_type = meta.get('TYPE')
            new_type = FileManager.TYPE_DELIMITED if current_type == FileManager.TYPE_FIXED else FileManager.TYPE_FIXED
            
            new_file = FileManager.convert_file_structure(current_file, new_type)
            
            page.snack_bar = ft.SnackBar(ft.Text(f"Converted to '{new_file}' ({new_type})"), bgcolor="green")
            page.snack_bar.open = True
            current_file = new_file
            update_active_file_text()
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Conversion Error: {str(ex)}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def compress_click(e):
        if not current_file:
            # Allow picking a file to compress
            compress_picker.pick_files(allow_multiple=False)
            return
            
        try:
            comp_file = FileManager.compress_file(current_file)
            page.snack_bar = ft.SnackBar(ft.Text(f"Compressed to '{comp_file}'"), bgcolor="green")
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def decompress_click(e):
         nonlocal current_file
         if current_file and current_file.endswith('.gz'):
             try:
                 decomp_file = FileManager.decompress_file(current_file)
                 page.snack_bar = ft.SnackBar(ft.Text(f"Decompressed to '{decomp_file}'"), bgcolor="green")
                 page.snack_bar.open = True
                 current_file = decomp_file
                 update_active_file_text()
                 page.update()
             except Exception as ex:
                 page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"), bgcolor="red")
                 page.snack_bar.open = True
                 page.update()
         else:
             gz_picker.pick_files(allow_multiple=False, allowed_extensions=["gz"])

    # Navigation Rail
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=400,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon="home_outlined", selected_icon="home", label="Home"
            ),
            ft.NavigationRailDestination(
                icon="add_circle_outline", selected_icon="add_circle", label="Add Student"
            ),
            ft.NavigationRailDestination(
                icon="search_outlined", selected_icon="search", label="Search"
            ),
            ft.NavigationRailDestination(
                icon="list_alt_outlined", selected_icon="list_alt", label="View All"
            ),
        ],
        on_change=lambda e: navigate(e.control.selected_index),
    )

    # Content Area
    content_area = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

    # --- Pages ---

    def get_home_page():
        return ft.Container(
            padding=40,
            content=ft.Column(
                [
                    ft.Text("Welcome Back", size=40, weight=ft.FontWeight.BOLD, color="teal"),
                    ft.Text("Manage your student records efficiently.", size=16, color="grey"),
                    ft.Divider(height=30, color="transparent"),
                    
                    ft.Card(
                        elevation=5,
                        content=ft.Container(
                            padding=30,
                            content=ft.Column([
                                ft.Text("File Operations", size=20, weight=ft.FontWeight.W_600),
                                ft.Divider(),
                                ft.Row([
                                    file_name_input,
                                    ft.IconButton(icon="folder_open", on_click=lambda _: pick_files_dialog.pick_files(allow_multiple=False), tooltip="Pick File"),
                                ]),
                                file_type_dropdown,
                                ft.Row([
                                    ft.FilledButton("Create File", on_click=create_file_click, icon="create", width=190),
                                    ft.OutlinedButton("Load File", on_click=load_file_click, icon="file_open", width=190),
                                ], alignment=ft.MainAxisAlignment.START),
                                ft.Divider(),
                                ft.Text("Advanced Operations", size=16, weight=ft.FontWeight.W_600),
                                ft.Row([
                                    ft.ElevatedButton("Import CSV", on_click=lambda _: csv_import_dialog.pick_files(allow_multiple=False, allowed_extensions=["csv"]), icon="upload_file"),
                                    ft.ElevatedButton("Convert Structure", on_click=convert_click, icon="transform"),
                                ]),
                                ft.Row([
                                    ft.ElevatedButton("Compress File", on_click=compress_click, icon="compress"),
                                    ft.ElevatedButton("Decompress File", on_click=decompress_click, icon="expand"),
                                ])
                            ], spacing=20)
                        )
                    ),
                    ft.Divider(height=20, color="transparent"),
                    ft.Container(
                        padding=15,
                        bgcolor="surfaceVariant",
                        border_radius=10,
                        content=ft.Row([
                            ft.Icon("info", color="teal"),
                            active_file_text,
                        ])
                    )
                ],
            )
        )

    def get_add_student_page():
        if not current_file:
            return ft.Container(
                padding=40,
                content=ft.Column([
                    ft.Icon("warning", size=50, color="orange"),
                    ft.Text("Please select or create a file first!", size=20)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )

        id_field = ft.TextField(label="ID (Integer)", width=400, border="underline", filled=True)
        name_field = ft.TextField(label="Name", width=400, border="underline", filled=True)
        gpa_field = ft.TextField(label="GPA (Float)", width=400, border="underline", filled=True)
        dept_field = ft.TextField(label="Department", width=400, border="underline", filled=True)

        def save_student(e):
            try:
                s_id = int(id_field.value)
                s_name = name_field.value
                s_gpa = float(gpa_field.value)
                s_dept = dept_field.value
                
                student = Student(s_id, s_name, s_gpa, s_dept)
                FileManager.add_student(current_file, student)
                
                page.snack_bar = ft.SnackBar(ft.Text("Student added successfully!"), bgcolor="green")
                page.snack_bar.open = True
                
                # Clear fields
                id_field.value = ""
                name_field.value = ""
                gpa_field.value = ""
                dept_field.value = ""
                page.update()
                
            except ValueError as ve:
                page.snack_bar = ft.SnackBar(ft.Text(f"Input Error: {str(ve)}"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

        return ft.Container(
            padding=40,
            content=ft.Column(
                [
                    ft.Text("Add New Student", size=30, weight=ft.FontWeight.BOLD, color="teal"),
                    ft.Divider(),
                    ft.Card(
                        elevation=5,
                        content=ft.Container(
                            padding=30,
                            content=ft.Column([
                                id_field,
                                name_field,
                                gpa_field,
                                dept_field,
                                ft.FilledButton("Save Student", on_click=save_student, icon="save", width=200),
                            ], spacing=20)
                        )
                    )
                ],
                spacing=20
            )
        )

    def get_search_page():
        if not current_file:
            return ft.Container(padding=40, content=ft.Text("Please select/create a file first!", size=20, color="red"))

        search_id_field = ft.TextField(label="Search by ID", width=300, border="underline", filled=True)
        result_area = ft.Column()
        
        rrn_field = ft.TextField(label="Search by RRN (Fixed Only)", width=300, border="underline", filled=True)

        def search_click(e):
            result_area.controls.clear()
            try:
                s_id = int(search_id_field.value)
                student, time_ms = FileManager.search_student(current_file, s_id)
                
                if student:
                    result_area.controls.append(
                        ft.Card(
                            elevation=2,
                            content=ft.Container(
                                content=ft.Column(
                                    [
                                        ft.ListTile(
                                            leading=ft.Icon("person", size=40, color="teal"),
                                            title=ft.Text(student.name, size=20, weight=ft.FontWeight.BOLD),
                                            subtitle=ft.Text(f"ID: {student.id} | GPA: {student.gpa} | Dept: {student.dept}"),
                                        ),
                                        ft.Container(
                                            padding=10,
                                            content=ft.Text(f"Search Time: {time_ms:.4f} ms", italic=True, color="grey")
                                        )
                                    ]
                                ),
                                padding=10,
                            )
                        )
                    )
                else:
                    result_area.controls.append(
                        ft.Container(
                            padding=10, bgcolor="red100", border_radius=5,
                            content=ft.Text("Student not found.", color="red")
                        )
                    )
                
                page.update()
            except ValueError:
                page.snack_bar = ft.SnackBar(ft.Text("Invalid ID format"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

        def rrn_search_click(e):
            result_area.controls.clear()
            try:
                rrn = int(rrn_field.value)
                # Measure time for RRN
                import time
                start = time.time()
                student = FileManager.get_record_by_rrn(current_file, rrn)
                end = time.time()
                time_ms = (end - start) * 1000
                
                if student:
                    result_area.controls.append(
                        ft.Card(
                            elevation=2,
                            content=ft.Container(
                                content=ft.Column(
                                    [
                                        ft.ListTile(
                                            leading=ft.Icon("person_pin", size=40, color="purple"),
                                            title=ft.Text(student.name, size=20, weight=ft.FontWeight.BOLD),
                                            subtitle=ft.Text(f"ID: {student.id} | GPA: {student.gpa} | Dept: {student.dept}"),
                                        ),
                                        ft.Container(
                                            padding=10,
                                            content=ft.Text(f"RRN Access Time: {time_ms:.4f} ms", italic=True, color="grey")
                                        )
                                    ]
                                ),
                                padding=10,
                            )
                        )
                    )
                else:
                    result_area.controls.append(ft.Text("Record not found at this RRN.", color="red"))
                page.update()
            except Exception as ex:
                result_area.controls.append(ft.Text(f"Error: {str(ex)}", color="red"))
                page.update()

        return ft.Container(
            padding=40,
            content=ft.Column(
                [
                    ft.Text("Search Student", size=30, weight=ft.FontWeight.BOLD, color="teal"),
                    ft.Divider(),
                    ft.Card(
                        content=ft.Container(
                            padding=20,
                            content=ft.Column([
                                ft.Text("Sequential Search", weight=ft.FontWeight.BOLD),
                                ft.Row([search_id_field, ft.FilledButton("Search", on_click=search_click, icon="search")]),
                            ])
                        )
                    ),
                    ft.Card(
                        content=ft.Container(
                            padding=20,
                            content=ft.Column([
                                ft.Text("RRN Access (Fixed-Length Only)", weight=ft.FontWeight.BOLD),
                                ft.Row([rrn_field, ft.OutlinedButton("Go to RRN", on_click=rrn_search_click, icon="arrow_forward")]),
                            ])
                        )
                    ),
                    ft.Divider(),
                    ft.Text("Results:", size=18, weight=ft.FontWeight.BOLD),
                    result_area
                ],
                spacing=20
            )
        )

    def get_view_all_page():
        if not current_file:
            return ft.Container(padding=40, content=ft.Text("Please select/create a file first!", size=20, color="red"))

        students = FileManager.read_all(current_file)
        
        # Data Table
        
        def delete_student_click(e):
            s_id = e.control.data
            if FileManager.delete_student(current_file, s_id):
                page.snack_bar = ft.SnackBar(ft.Text(f"Student {s_id} deleted."), bgcolor="green")
                page.snack_bar.open = True
                navigate(3) # Refresh view
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Error deleting student."), bgcolor="red")
                page.snack_bar.open = True
                page.update()

        def export_csv_click(e):
            try:
                output_path = "students_export.csv"
                FileManager.export_to_csv(current_file, output_path)
                page.snack_bar = ft.SnackBar(ft.Text(f"Exported to {output_path}"), bgcolor="green")
                page.snack_bar.open = True
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Export Error: {str(ex)}"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

        def export_excel_click(e):
            try:
                output_path = "students_export.xlsx"
                FileManager.export_to_excel(current_file, output_path)
                page.snack_bar = ft.SnackBar(ft.Text(f"Exported to {output_path}"), bgcolor="green")
                page.snack_bar.open = True
                page.update()
            except ImportError:
                page.snack_bar = ft.SnackBar(ft.Text("Pandas/OpenPyXL not installed."), bgcolor="orange")
                page.snack_bar.open = True
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Export Error: {str(ex)}"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

        columns = [
            ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("GPA", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Dept", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD)),
        ]
        
        rows = []
        for s in students:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(s.id))),
                        ft.DataCell(ft.Text(s.name)),
                        ft.DataCell(ft.Text(str(s.gpa))),
                        ft.DataCell(ft.Text(s.dept)),
                        ft.DataCell(
                            ft.IconButton(
                                icon="delete",
                                icon_color="red",
                                data=s.id,
                                on_click=delete_student_click,
                                tooltip="Delete Student"
                            )
                        ),
                    ]
                )
            )

        return ft.Container(
            padding=40,
            content=ft.Column(
                [
                    ft.Row([
                        ft.Text("All Students", size=30, weight=ft.FontWeight.BOLD, color="teal"),
                        ft.Container(expand=True),
                        ft.OutlinedButton("Export CSV", on_click=export_csv_click, icon="download"),
                        ft.FilledButton("Export Excel", on_click=export_excel_click, icon="table_view"),
                    ]),
                    ft.Divider(),
                    ft.Card(
                        elevation=2,
                        content=ft.Container(
                            padding=10,
                            content=ft.DataTable(
                                columns=columns, 
                                rows=rows, 
                                border=ft.border.all(1, "grey_200"),
                                vertical_lines=ft.border.BorderSide(1, "grey_200"),
                                horizontal_lines=ft.border.BorderSide(1, "grey_200"),
                                heading_row_color="surfaceVariant",
                            )
                        )
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True
            )
        )

    def navigate(index):
        content_area.controls.clear()
        if index == 0:
            content_area.controls.append(get_home_page())
        elif index == 1:
            content_area.controls.append(get_add_student_page())
        elif index == 2:
            content_area.controls.append(get_search_page())
        elif index == 3:
            content_area.controls.append(get_view_all_page())
        page.update()

    # Layout
    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                content_area,
            ],
            expand=True,
        )
    )
    
    # Add theme toggle to app bar or floating action button
    page.floating_action_button = ft.FloatingActionButton(
        icon="dark_mode", on_click=toggle_theme, bgcolor="teal"
    )

    # Init
    navigate(0)

if __name__ == "__main__":
    ft.app(target=main)
