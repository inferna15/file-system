from tkinter import filedialog, ttk, font, messagebox, simpledialog, Toplevel
from PIL import Image, ImageTk
import tkinter as tk
import os
import struct
import math
import random
import sys

class Block():
    def __init__(self, block_id, offset, status, type, file_no, order_no):
        self.id = block_id
        self.offset = offset
        # Status -> Empty = 0; Non-Empty = 1
        self.status = status
        # Type -> Node = 0; Content = 1
        self.type = type
        # File_no and Order_no for Content
        self.file_no = file_no
        self.order_no = order_no

    def to_binary(self):
        # 24 byte
        return struct.pack("6I", self.id, self.offset, self.status, self.type, self.file_no, self.order_no)
    
    @staticmethod
    def from_binary(binary_data):
        return Block(*struct.unpack("6I", binary_data))
    
class Table():
    def __init__(self):
        self.block_size = 0
        self.block_number = 0
        self.block_list = []

    def reset(self):
        self.block_size = 0
        self.block_number = 0
        self.block_list.clear()


    def to_binary(self):
        # 8 byte
        return struct.pack("2I", self.block_size, self.block_number)

    @staticmethod
    def from_binary(binary_data):
        return Table(*struct.unpack("2I", binary_data))

class Node():
    def __init__(self, name, node_id, parent_id, is_folder, path):
        self.name = name
        self.id = node_id
        self.parent_id = parent_id
        self.is_folder = is_folder
        self.path = path

    def insert(self):
        if self.is_folder:
            treeview.insert(str(self.parent_id), "end", iid=str(self.id), text=f" {self.name}", open=False, image=photo_dir)
        else:
            treeview.insert(str(self.parent_id), "end", iid=str(self.id), text=f" {self.name}", image=photo_file)

    def to_binary(self):
        return struct.pack("256sIII", self.name.encode('utf-8'), self.id, self.parent_id, self.is_folder)

    @staticmethod
    def from_binary(binary_data):
        list = struct.unpack("256sIII", binary_data)
        name = list[0].strip(b'\x00').decode('utf-8')
        is_folder = bool(list[3])
        return Node(name, list[1], list[2], is_folder, "")

class FileSystem():
    def __init__(self):
        self.mode = "None"
        self.last_id = 1
        self.current_nodes = []
        self.table = Table()

    def reset(self):
        self.mode = "None"
        self.last_id = 1
        self.current_nodes.clear()
        self.table.reset()
        FileSystem.clear_treeview()

    def open_folder(self):
        def create_nodes(parent):
            for item in os.listdir(parent.path):
                full_path = os.path.join(parent.path, item)
                self.last_id += 1
                if os.path.isdir(full_path):
                    node = Node(item, self.last_id, parent.id, True, full_path)
                    self.current_nodes.append(node)
                    node.insert()
                    create_nodes(node)
                else:
                    node = Node(item, self.last_id, parent.id, False, full_path)
                    self.current_nodes.append(node)
                    node.insert()

        folder_path = filedialog.askdirectory()
        if folder_path:
            self.reset()
            self.mode = "DirectoryToFileSystem"
            treeview.heading("#0", text=folder_path)

            path, name = os.path.split(folder_path)
            node = Node(name, self.last_id, 0, True, folder_path)
            self.current_nodes.append(node)
            treeview.insert("", "end", iid=str(node.id), text=f" {node.name}", open=True, image=photo_dir)
            create_nodes(node)
        else:
            self.reset()
            self.mode = "None"

    def create_file_system(self):
        def write_header():
            with open(folder_path, "w+b") as file:
                file.write(self.table.to_binary())

        def write_table_and_blocks():
            position_list = [i for i in range(self.table.block_number)]
            random.shuffle(position_list)

            offset = struct.calcsize("2I") + struct.calcsize("6I") * self.table.block_number

            last_id = 0
            for node in self.current_nodes:
                block_offset = offset + self.table.block_size * position_list[last_id]
                last_id += 1
                self.table.block_list.append(Block(last_id, block_offset, 1, 0, 0, 0))
                with open(folder_path, "r+b") as file:
                    file.seek(block_offset)
                    file.write(node.to_binary())
                if not node.is_folder:
                    with open(node.path, "r+b") as file:
                        data = file.read()
                    contents = [data[i:i+self.table.block_size] for i in range(0, len(data), self.table.block_size)]
                    contents[-1] = contents[-1] + b'\x00' * (self.table.block_size - len(contents[-1]))
                    for i, content in enumerate(contents):
                        block_offset = offset + self.table.block_size * position_list[last_id]
                        last_id += 1
                        self.table.block_list.append(Block(last_id, block_offset, 1, 1, node.id, i + 1))
                        with open(folder_path, "r+b") as file:
                            file.seek(block_offset)
                            file.write(content)
            
            for i in range(self.table.block_number - len(self.table.block_list)):
                block_offset = offset + self.table.block_size * position_list[last_id]
                last_id += 1
                self.table.block_list.append(Block(last_id, block_offset, 0, 0, 0, 0))
            
            with open(folder_path, "r+b") as file:
                file.seek(struct.calcsize("2I"))
                for block in self.table.block_list:
                    file.write(block.to_binary())

        block_size = simpledialog.askinteger("", "Type Part Size")
        folder_path = filedialog.askdirectory()
        folder_path = os.path.join(folder_path, "file-system")
        if block_size > 0 and folder_path:
            self.table.block_size = block_size
            content_number = 0
            for node in self.current_nodes:
                if not node.is_folder:
                    file_size = os.path.getsize(node.path)
                    content_number += math.ceil(file_size / block_size)
            self.table.block_number = int((content_number + len(self.current_nodes)) * 1.5)
            write_header()
            write_table_and_blocks()
            messagebox.showinfo("Completed!");
        else:
            messagebox.showerror("Wrong number or place")

    def open_file_system(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.reset()
            self.mode = "FileSystemToDirectory"
            treeview.heading("#0", text=file_path)

            # Read Table
            with open(file_path, "r+b") as file:
                header = struct.unpack("2I", file.read(struct.calcsize("2I")))
                self.table.block_size = header[0]
                self.table.block_number = header[1]
                for i in range(self.table.block_number):
                    self.table.block_list.append(Block.from_binary(file.read(struct.calcsize("6I"))))

                node_blocks = [block for block in self.table.block_list if block.type == 0 and block.status == 1]
                for block in node_blocks:
                    file.seek(block.offset)
                    self.current_nodes.append(Node.from_binary(file.read(struct.calcsize("256sIII"))))
                self.current_nodes.sort(key=lambda x: x.id)

            treeview.insert("", "end", iid="1", text=f" {self.current_nodes[0].name}", open=True, image=photo_dir)
            for node in self.current_nodes[1:]:
                node.insert()
        else:
            self.reset()
            self.mode = "None"

    def run(self):
        if self.mode == "DirectoryToFileSystem":
            self.create_file_system()
        elif self.mode == "FileSystemToDirectory":
            pass
        else:
            messagebox.showwarning("Not selected a mode")

    @staticmethod
    def clear_treeview():
        for item in treeview.get_children():
            treeview.delete(item)



file_system = FileSystem()

if __name__ == "__main__":
    # App
    app = tk.Tk()
    app.title("shuffle-files")
    app.geometry("1000x500")
    app.resizable(False, False)

    # Style
    style = ttk.Style(app)
    style.theme_use("clam")

    tree_style = ttk.Style()
    tree_style.configure("Treeview", font=("Cascadia Code", 9))
    tree_style.configure("Treeview.Heading", font=("Cascadia Code", 9))

    # Font
    custom_font = font.Font(family="Cascadia Code", size=10)

    # Photo
    icon_size = (20, 20)

    def create_icon(image_path):
        image = Image.open(image_path)
        image = image.resize(icon_size)
        return ImageTk.PhotoImage(image)

    icons = {
        'file': "assets/file.png",
        'directory': "assets/directory.png",
        'delete': "assets/delete.png",
        'edit': "assets/edit.png",
        'export': "assets/export.png",
        'import': "assets/import.png",
        'new_file': "assets/new_file.png",
        'new_folder': "assets/new_folder.png",
        'rename': "assets/rename.png",
        'run': "assets/run.png",
        'test': "assets/test.png"
    }

    photo_file = create_icon(icons['file'])
    photo_dir = create_icon(icons['directory'])
    photo_delete = create_icon(icons['delete'])
    photo_edit = create_icon(icons['edit'])
    photo_export = create_icon(icons['export'])
    photo_import = create_icon(icons['import'])
    photo_new_file = create_icon(icons['new_file'])
    photo_new_folder = create_icon(icons['new_folder'])
    photo_rename = create_icon(icons['rename'])
    photo_run = create_icon(icons['run'])
    photo_test = create_icon(icons['test'])

    # Menu
    menu_bar = tk.Menu(app)
    app.config(menu=menu_bar)

    file_menu = tk.Menu(menu_bar, tearoff=0, font=custom_font)
    file_menu.add_command(label="Convert", command=file_system.run, image=photo_run, compound=tk.LEFT)
    file_menu.add_command(label="Open Shuffle Item", command=file_system.open_file_system, image=photo_import, compound=tk.LEFT)
    file_menu.add_command(label="Open Directory", command=file_system.open_folder, image=photo_export, compound=tk.LEFT)

    operation_menu = tk.Menu(menu_bar, tearoff=0, font=custom_font)
    operation_menu.add_command(label="New File", command="select_new_file", image=photo_new_file, compound=tk.LEFT)
    operation_menu.add_command(label="New Folder", command="select_new_folder", image=photo_new_folder, compound=tk.LEFT)
    operation_menu.add_command(label="Edit", command="select_edit", image=photo_edit, compound=tk.LEFT)
    operation_menu.add_command(label="Delete", command="select_delete", image=photo_delete, compound=tk.LEFT)
    operation_menu.add_command(label="Rename", command="select_rename", image=photo_rename, compound=tk.LEFT)


    test_menu = tk.Menu(menu_bar, tearoff=0, font=custom_font)
    test_menu.add_command(label="Print Nodes", command="", image=photo_test, compound=tk.LEFT)
    test_menu.add_command(label="Print Shuffle Info", command="", image=photo_test, compound=tk.LEFT)
    test_menu.add_command(label="Print Treeview Item", command="", image=photo_test, compound=tk.LEFT)

    menu_bar.add_cascade(label="Commands", menu=file_menu)
    menu_bar.add_cascade(label="Operations", menu=operation_menu)
    menu_bar.add_cascade(label="Tests", menu=test_menu)

    # Main Frame
    main_frame = ttk.Frame(app, width=1000, height=500)
    main_frame.pack_propagate(False)
    main_frame.pack()

    # Treeview
    treeview = ttk.Treeview(main_frame)
    treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tree_scroll = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=treeview.yview)
    tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    treeview.configure(yscrollcommand=tree_scroll.set)

    app.mainloop()