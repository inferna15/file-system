from tkinter import filedialog, ttk, font, messagebox, simpledialog, Toplevel
from PIL import Image, ImageTk
import tkinter as tk
import os
import struct
import math
import random
import chiper_utils

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
        return struct.pack("256sIII", self.name.encode('utf-8'), self.id, self.parent_id, 1 if self.is_folder else 0)

    @staticmethod
    def from_binary(binary_data):
        list = struct.unpack("256sIII", binary_data)
        name = list[0].strip(b'\x00').decode('utf-8')
        is_folder = True if list[3] == 1 else False
        return Node(name, list[1], list[2], is_folder, "")

    def __str__(self):
        return f'''
---------------------------
Name: {self.name}
Id: {self.id}
Parent Id: {self.parent_id}
Is Folder: {self.is_folder}
Path: {self.path}
        '''

class FileSystem():
    def __init__(self):
        self.mode = "None"
        self.last_id = 1
        self.current_nodes = []
        self.table = Table()
        self.current_file_path = ""
        self.salt = b'\x00'
        self.key = b'\x00'
        self.nonce = b'\x00'

    def reset(self):
        self.mode = "None"
        self.last_id = 1
        self.current_nodes.clear()
        self.current_file_path = ""
        self.table.reset()
        FileSystem.clear_treeview()
        self.salt = b'\x00'
        self.key = b'\x00'
        self.nonce = b'\x00'

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
            print(f"{folder_path} yoluna sahip olan klasör açılacak.")
            self.reset()
            self.mode = "DirectoryToFileSystem"
            treeview.heading("#0", text=folder_path)

            path, name = os.path.split(folder_path)
            node = Node(name, self.last_id, 0, True, folder_path)
            self.current_nodes.append(node)
            treeview.insert("", "end", iid=str(node.id), text=f" {node.name}", open=True, image=photo_dir)
            create_nodes(node)
            print(f"{node.name} isimli dosya açıldı.")
        else:
            self.reset()
            self.mode = "None"

    def create_file_system(self):
        def write_header():
            print("Başlık verileri oluşturuluyor..")
            print("Salt oluşturuluyor.")
            self.salt = chiper_utils.create_salt()
            print("Nonce oluşturuluyor.")
            self.nonce = chiper_utils.create_nonce()
            password = None
            while password is None or len(password) != 4:
                password = simpledialog.askstring("Şifre", "Şifreyi giriniz:")
            print("Anahtar oluşturuluyor.")
            self.key = chiper_utils.create_key(password, self.salt)

            print("Başlık verileri yazdırılıyor.")
            with open(folder_path, "w+b") as file:
                file.write(self.salt)
                file.write(self.nonce)
                file.write(chiper_utils.encrypt_data(self.salt, self.key, self.nonce, 3))
                file.write(chiper_utils.encrypt_data(self.table.to_binary(), self.key, self.nonce, 4))
                # 48 byte = 16 + 8 + 16 + 8

        def write_table_and_blocks():
            print("Tablo ve blok verileri oluşturuluyor.")
            print("Karıştırma işlemi yapılıyor.")
            position_list = [i for i in range(self.table.block_number)]
            random.shuffle(position_list)

            offset = 48 + 24 * self.table.block_number

            last_id = 0
            for node in self.current_nodes:
                with open(folder_path, "r+b") as file:
                    print(f"{node.name} adlı dosyanın meta bilgileri yazdırılmaya başlandı.")
                    block_offset = offset + self.table.block_size * position_list[last_id]
                    last_id += 1
                    self.table.block_list.append(Block(last_id, block_offset, 1, 0, node.id, 0))
                    file.seek(block_offset)
                    # 268 byte = 264 + 4 + 4 + 4
                    file.write(chiper_utils.encrypt_data(node.to_binary(), self.key, self.nonce, last_id))
                    file.write(chiper_utils.create_dummy_data(self.table.block_size - 268))
                if not node.is_folder:
                    print(f"{node.name} adlı dosyanın içerikleri yazdırılmaya başlandı.")
                    with open(node.path, "r+b") as file:
                        # Dosya çok büyük olursa, bu kısımda sorun çıkabilir.
                        data = file.read()
                    contents = [data[i:i+self.table.block_size] for i in range(0, len(data), self.table.block_size)]
                    if len(contents) > 0:
                        contents[-1] = contents[-1] + b'\x00' * (self.table.block_size - len(contents[-1]))
                    with open(folder_path, "r+b") as file:
                        for i, content in enumerate(contents):
                            block_offset = offset + self.table.block_size * position_list[last_id]
                            last_id += 1
                            self.table.block_list.append(Block(last_id, block_offset, 1, 1, node.id, i + 1))
                            file.seek(block_offset)
                            file.write(chiper_utils.encrypt_data(content, self.key, self.nonce, last_id))
            
            for i in range(self.table.block_number - len(self.table.block_list)):
                block_offset = offset + self.table.block_size * position_list[last_id]
                last_id += 1
                self.table.block_list.append(Block(last_id, block_offset, 0, 0, 0, 0))
            print("İçerikler yazdırılmaya başladı.")
            with open(folder_path, "r+b") as file:
                file.seek(48)
                for block in self.table.block_list:
                    file.write(chiper_utils.encrypt_data(block.to_binary(), self.key, self.nonce, block.id))

        print("Dosya sistemi oluşturulmaya başlandı.")
        size = simpledialog.askinteger("", "Parça boyutunu yazın:")

        # Bu kısım hoca ile konuşulacak.
        # Değeri 1024'e tam bölünmüyorsa, bir üst 1024'e tamamla
        block_size = size if size % 1024 == 0 else size + 1024 - (size % 1024)

        folder_path = filedialog.askdirectory()
        folder_path = os.path.join(folder_path, "file-system")
        print(f"{folder_path} isimli dosya oluşturulacak.")
        print(f"Parça boyutu: {block_size} byte")
        if block_size > 0 and folder_path:
            print("Dosya sistemi oluşturuluyor.")
            self.table.block_size = block_size
            content_number = 0  # Buradan devam et
            for node in self.current_nodes:
                if not node.is_folder:
                    file_size = os.path.getsize(node.path)
                    content_number += math.ceil(file_size / block_size)
            self.table.block_number = int((content_number + len(self.current_nodes)) * 1.5)
            print(f"Parça sayısı: {self.table.block_number}")
            write_header()
            write_table_and_blocks()
            print("Dosya sistemi oluşturuldu.")
            messagebox.showinfo("Bilgi", "Dosya sistemi oluşturuldu.")
        else:
            print("Dosya sistemi oluşturulamadı.")
            messagebox.showerror("Hata", "Bir sorun çıktı.")

    def open_file_system(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            password = None
            while password is None or len(password) != 4:
                password = simpledialog.askstring("Şifre", "Şifreyi giriniz:")
            print(f"{file_path} isimli dosya sistemi açılacak.")
            self.reset()
            self.mode = "FileSystemToDirectory"
            treeview.heading("#0", text=file_path)
            self.current_file_path = file_path

            # Read Table
            with open(file_path, "r+b") as file:
                print("Şifre çözülüyor.")
                self.salt = file.read(16)
                self.nonce = file.read(8)
                self.key = chiper_utils.create_key(password, self.salt)
                verify_salt = chiper_utils.decrypt_data(file.read(16), self.key, self.nonce, 3)
                if self.salt == verify_salt:
                    print("Meta data okunuyor.")
                    header = struct.unpack("2I", chiper_utils.decrypt_data(file.read(8), self.key, self.nonce, 4))
                    self.table.block_size = header[0]
                    self.table.block_number = header[1]
                    for i in range(self.table.block_number):
                        self.table.block_list.append(Block.from_binary(chiper_utils.decrypt_data(file.read(24), self.key, self.nonce, i + 1)))

                    node_blocks = [block for block in self.table.block_list if block.type == 0 and block.status == 1]
                    for block in node_blocks:
                        file.seek(block.offset)
                        self.current_nodes.append(Node.from_binary(chiper_utils.decrypt_data(file.read(268), self.key, self.nonce, block.id)))
                    self.current_nodes.sort(key=lambda x: x.id)
                else:
                    messagebox.showerror("Hata", "Şifre yanlış.")
                    self.reset()
                    self.mode = "None"
                    return
                    
            treeview.insert("", "end", iid="1", text=f" {self.current_nodes[0].name}", open=True, image=photo_dir)
            for node in self.current_nodes[1:]:
                node.insert()
            self.last_id = self.current_nodes[-1].id
            print("Dosya sistemi açıldı.")
        else:
            self.reset()
            self.mode = "None"

    def create_folder(self):
        def create_paths(file_path):
            root = file_path
            for node in self.current_nodes:
                if node.id == 1:
                    node.path = os.path.join(root, node.name + "-unshuffled")
                else:
                    parent = next((obj for obj in self.current_nodes if obj.id == node.parent_id), None)
                    node.path = os.path.join(parent.path, node.name)

        folder_path = filedialog.askdirectory()
        if folder_path:
            print(f"{self.current_file_path} isimli dosya sistemi {folder_path} yoluna çıkartılacak.")
            create_paths(folder_path)
            for node in self.current_nodes:
                if node.is_folder:
                    print(node.path)
                    os.mkdir(node.path)
                else:
                    content_blocks = [block for block in self.table.block_list if block.status == 1 and block.type == 1 and block.file_no == node.id]
                    content_blocks.sort(key=lambda x: x.order_no)
                    data = []
                    with open(self.current_file_path, "r+b") as file:
                        for block in content_blocks:
                            file.seek(block.offset)
                            data.append(chiper_utils.decrypt_data(file.read(self.table.block_size), self.key, self.nonce, block.id))
                    if len(data) > 0:
                        data[-1] = data[-1].strip(b'x\00')
                    with open(node.path, "w+b") as file:
                        for item in data:
                            file.write(item)
            messagebox.showinfo("Bilgi", "Dosya sistemi çıkartıldı.")
        else:
            messagebox.showerror("Hata", "Bir sorun çıktı.")

    def run(self):
        if self.mode == "DirectoryToFileSystem":
            self.create_file_system()
        elif self.mode == "FileSystemToDirectory":
            self.create_folder()
        else:
            messagebox.showwarning("Uyarı", "Bir mod seçili değil.")

    def new_file(self):
        if self.mode == "FileSystemToDirectory":
            if len(treeview.selection()) == 0 or len(treeview.selection()) > 1:
                messagebox.showwarning("Uyarı", "Bir klasör seçiniz.")
            else:
                parent = treeview.selection()[0]
                parent_node = next((node for node in self.current_nodes if node.id == int(parent)), None)
                if parent_node.is_folder:
                    file_name = simpledialog.askstring("Dosya Adı", "Dosyanın adını yazınız:")
                    if file_name is None or file_name == "":
                        messagebox.showerror("Hata", "Dosya adı boş olamaz.")
                        return
                    for child in treeview.get_children(parent):
                        if f" {file_name}" == treeview.item(child, 'text'):
                            messagebox.showerror("Hata", "Aynı isimde iki dosya aynı klasörde olamaz.")
                            return
                    path = os.path.join(parent_node.path, file_name)
                    self.last_id += 1
                    node = Node(file_name, self.last_id, int(parent), False, path)
                    print(node)
                    node.insert()
                    treeview.update_idletasks()
                    self.current_nodes.append(node)

                    empty = None
                    for block in self.table.block_list:
                        if block.status == 0:
                            empty = block
                            break

                    if empty is None:
                        messagebox.showerror("Hata", "Optimizasyon tuşuna basınız.")
                        treeview.delete(str(node.id))
                        treeview.update_idletasks()
                        self.current_nodes.remove(node)
                        return

                    block = Block(empty.id, empty.offset, 1, 0, node.id, 0)
                    self.table.block_list[block.id - 1] = block
                    offset = 48 + 24 * (block.id - 1)
                    with open(self.current_file_path, 'r+b') as file:
                        file.seek(offset)
                        file.write(chiper_utils.encrypt_data(block.to_binary(), self.key, self.nonce, block.id))
                        file.seek(block.offset)
                        file.write(chiper_utils.encrypt_data(node.to_binary(), self.key, self.nonce, block.id))
                        file.write(chiper_utils.create_dummy_data(self.table.block_size - 268))
                    print(f"{node.name} adlı dosya oluşturuldu.")
                else:
                    messagebox.showwarning("Uyarı", "Bir klasör seçin dosya değil.")
        else:
            messagebox.showwarning("Uyarı", "Dosya sistemine daha dönüştürülmedi.")

    def new_folder(self):
        if self.mode == "FileSystemToDirectory":
            if len(treeview.selection()) == 0 or len(treeview.selection()) > 1:
                messagebox.showwarning("Uyarı", "Bir klasör seçiniz.")
            else:
                parent = treeview.selection()[0]
                parent_node = next((node for node in self.current_nodes if node.id == int(parent)), None)
                if parent_node.is_folder:
                    file_name = simpledialog.askstring("Klasör Adı", "Klasörün adını yazınız:")
                    if file_name is None or file_name == "":
                        messagebox.showerror("Hata", "Dosya adı boş olamaz.")
                        return
                    for child in treeview.get_children(parent):
                        if f" {file_name}" == treeview.item(child, 'text'):
                            messagebox.showerror("Hata", "Aynı isimde iki dosya aynı klasörde olamaz.")
                            return
                    path = os.path.join(parent_node.path, file_name)
                    self.last_id += 1
                    
                    node = Node(file_name, self.last_id, int(parent), True, path)
                    print(node)
                    node.insert()
                    treeview.update_idletasks()
                    self.current_nodes.append(node)

                    empty = None
                    for block in self.table.block_list:
                        if block.status == 0:
                            empty = block
                            break

                    if empty is None:
                        messagebox.showerror("Hata", "Optimizasyon tuşuna basınız.")
                        treeview.delete(str(node.id))
                        treeview.update_idletasks()
                        self.current_nodes.remove(node)
                        return

                    block = Block(empty.id, empty.offset, 1, 0, node.id, 0)
                    self.table.block_list[block.id - 1]  = block
                    offset = 48 + 24 * (block.id - 1)  
                    with open(self.current_file_path, 'r+b') as file:
                        file.seek(offset)
                        file.write(chiper_utils.encrypt_data(block.to_binary(), self.key, self.nonce, block.id))
                        file.seek(block.offset)
                        file.write(chiper_utils.encrypt_data(node.to_binary(), self.key, self.nonce, block.id))
                        file.write(chiper_utils.create_dummy_data(self.table.block_size - 268))
                    print(f"{node.name} adlı klasör oluşturuldu.")
                else:
                    messagebox.showwarning("Uyarı", "Bir klasör seçin dosya değil.")
        else:
            messagebox.showwarning("Uyarı", "Dosya sistemine daha dönüştürülmedi.")

    def delete(self):
        def delete_recursnoncee(item):
            if item not in deleted_items:
                if not treeview.get_children(item):
                    treeview.delete(item)
                    deleted_items.append(item)
                    self.current_nodes = [node for node in self.current_nodes if node.id != int(item)]
                    return
                else:
                    for node in treeview.get_children(item):
                        delete_recursnoncee(node)
                    treeview.delete(item)
                    deleted_items.append(item)
                    self.current_nodes = [node for node in self.current_nodes if node.id != int(item)]

        if self.mode == "FileSystemToDirectory":
            if len(treeview.selection()) > 0:
                if messagebox.askokcancel("Soru", "Emin misin?"):
                    flag = True
                    deleted_items = []
                    for node in treeview.selection():
                        if int(node) == 1:
                            head, tail = os.path.split(self.current_file_path)
                            path = os.path.join(head, "file-system")
                            os.remove(path)
                            treeview.heading("#0", text="")
                            self.clear_treeview()
                            self.mode = 'None'
                            flag = False
                            print("Dosya sistemi silindi.")
                            break
                        else:
                            delete_recursnoncee(node)
                    if flag:
                        treeview.update_idletasks()
                        
                        node_block = []
                        content_blocks = []
                        for item in deleted_items:
                            node_block.append(next((block for block in self.table.block_list if block.status == 1 and block.file_no == int(item) and block.type == 0), None))
                            content_blocks.extend([block for block in self.table.block_list if block.status == 1 and block.file_no == int(item) and block.type == 1])
                            
                        list = []
                        list.extend(node_block)
                        list.extend(content_blocks)
                        self.table.block_list = [block for block in self.table.block_list if block not in list]
                        with open(self.current_file_path, 'r+b') as file:
                            for item in list:
                                offset = 48 + 24 * (item.id - 1)
                                file.seek(offset)
                                item.status = 0
                                item.type = 0
                                item.file_no = 0
                                item.order_no = 0
                                file.write(chiper_utils.encrypt_data(item.to_binary(), self.key, self.nonce, item.id))
                        print("Seçili dosyalar silindi.")
                    else:
                        messagebox.showinfo("Bilgi", "Dosya sistemi silindi.")
        else:
            messagebox.showwarning("Uyarı", "Dosya sistemine daha dönüştürülmedi.")

    def rename(self):
        if self.mode == "FileSystemToDirectory":
            if len(treeview.selection()) == 0 or len(treeview.selection()) > 1:
                messagebox.showwarning("Uyarı", "Bir dosya seçin.")
            else:
                node_id = treeview.selection()[0]
                parent = treeview.parent(node_id)
                rename = simpledialog.askstring("Dosya Adı", "Dosyanın adını yazınız:")
                if rename is None or rename == "":
                    messagebox.showerror("Hata", "Dosya adı boş olamaz.")
                    return
                for child in treeview.get_children(parent):
                    if f" {rename}" == treeview.item(child, 'text'):
                        messagebox.showerror("Hata", "Aynı isimde iki dosya aynı klasörde olamaz.")
                        return
                treeview.item(node_id, text=f" {rename}")
                node = next((node for node in self.current_nodes if node.id == int(node_id)), None)
                node.name = rename
                treeview.update_idletasks()
                block = next((block for block in self.table.block_list if block.file_no == node.id), None)
                with open(self.current_file_path, 'r+b') as file:
                    file.seek(block.offset)
                    file.write(chiper_utils.encrypt_data(node.to_binary(), self.key, self.nonce, block.id))
                print(f"{node.name} adlı dosya yeniden adlandırıldı.")
        else:
            messagebox.showwarning("Uyarı", "Dosya sistemine daha dönüştürülmedi.")

    def edit(self):
        def cancel():
            print("İçerikler güncellenmedi.")
            edit_window.destroy()
            app.deiconify()

        def save_changes():
            new_content = text_area.get("1.0", "end-1c").encode("utf-8")
            new_data = [new_content[i:i+self.table.block_size] for i in range(0, len(new_content), self.table.block_size)]

            if len(data) < len(new_data):
                print(1)
                amount_of_new_block = len(new_data) - len(data)
                new_blocks = []
                for i in range(amount_of_new_block):
                    block = next((block for block in self.table.block_list if block.status == 0), None)
                    if block is not None:
                        new_blocks.append(block)
                    else:
                        messagebox.showerror("", "Press the optimization button.")
                        return

                with open(self.current_file_path, "r+b") as file:
                    for i in range(len(data)):
                        if data[i] != new_data[i]:
                            file.seek(content_blocks[i].offset)
                            file.write(chiper_utils.encrypt_data(new_data[i], self.key, self.nonce, content_blocks[i].id))
                    
                    for i in range(amount_of_new_block):
                        file.seek(new_blocks[i].offset)
                        if len(new_data[len(data) + i]) < self.table.block_size:
                            new_data[len(data) + i] = new_data[len(data) + i] + b'\x00' * (self.table.block_size - len(new_data[len(data) + i]))
                        file.write(chiper_utils.encrypt_data(new_data[len(data) + i], self.key, self.nonce, new_blocks[i].id))
                        offset = 48 + 24 * (new_blocks[i].id - 1)
                        file.seek(offset)
                        new_blocks[i].status = 1
                        new_blocks[i].type = 1
                        new_blocks[i].file_no = int(selected)
                        new_blocks[i].order_no = len(data) + i + 1
                        file.write(chiper_utils.encrypt_data(new_blocks[i].to_binary(), self.key, self.nonce, new_blocks[i].id))

            elif len(data) > len(new_data):
                print(2)
                amount_of_deleted_block = len(data) - len(new_data)

                with open(self.current_file_path, "r+b") as file:
                    for i in range(len(new_data)):
                        if data[i] != new_data[i]:
                            file.seek(content_blocks[i].offset)
                            if len(new_data[i]) < self.table.block_size:
                                new_data[i] = new_data[i] + b'\x00' * (self.table.block_size - len(new_data[i]))
                            file.write(chiper_utils.encrypt_data(new_data[i], self.key, self.nonce, content_blocks[i].id))

                    for i in range(amount_of_deleted_block):
                        offset = 48 + 24 * (content_blocks[len(new_data) + i].id - 1)
                        file.seek(offset)
                        content_blocks[len(new_data) + i].status = 0
                        content_blocks[len(new_data) + i].type = 0
                        content_blocks[len(new_data) + i].file_no = 0
                        content_blocks[len(new_data) + i].order_no = 0
                        file.write(chiper_utils.encrypt_data(content_blocks[len(new_data) + i].to_binary(), self.key, self.nonce, content_blocks[len(new_data) + i].id))

            else:
                print(3)
                with open(self.current_file_path, "r+b") as file:
                    for i in range(len(new_data)):
                        if data[i] != new_data[i]:
                            file.seek(content_blocks[i].offset)
                            if len(new_data[i]) < self.table.block_size:
                                new_data[i] = new_data[i] + b'\x00' * (self.table.block_size - len(new_data[i]))
                            file.write(chiper_utils.encrypt_data(new_data[i], self.key, self.nonce, content_blocks[i].id))

            print("İçerikler güncellendi.")
            edit_window.destroy()
            app.deiconify()

        def edit_exit():
            answer = messagebox.askyesnocancel("Soru", "Kaydedilsin mi?")
            if answer is None:
                return
            elif answer:
                save_changes()
            else:
                cancel()

        if self.mode == "FileSystemToDirectory":
            if len(treeview.selection()) == 0 or len(treeview.selection()) > 1:
                messagebox.showwarning("Uyarı", "Bir dosya seçin.")
            else:
                selected = treeview.selection()[0]
                node = next((node for node in self.current_nodes if node.id == int(selected)), None)
                if node.is_folder:
                    messagebox.showerror("Hata", "Klasör seçmeyin.")
                else:
                    app.withdraw()
                    edit_window = Toplevel(app)
                    edit_window.title("edit")
                    edit_window.geometry(f"1000x500+{app.winfo_x()}+{app.winfo_y()}")
                    edit_window.protocol("WM_DELETE_WINDOW", lambda : edit_exit())
                    edit_window.resizable(False, False)
                    edit_window.grab_set()

                    text_area = tk.Text(edit_window, wrap=tk.WORD, font=custom_font)
                    text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                    text_scroll = tk.Scrollbar(edit_window, orient=tk.VERTICAL, command=text_area.yview)
                    text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

                    text_area.configure(yscrollcommand=text_scroll.set)

                    content_blocks = [block for block in self.table.block_list if block.status == 1 and block.type == 1 and block.file_no == int(selected)]
                    content_blocks.sort(key=lambda x: x.order_no)
                    data = []
                    with open(self.current_file_path, "r+b") as file:
                        for block in content_blocks:
                            file.seek(block.offset)
                            data.append(chiper_utils.decrypt_data(file.read(self.table.block_size), self.key, self.nonce, block.id))
                    if len(data) > 0:
                        data[-1] = data[-1].strip(b'x\00')
                    for content in data:
                        text_area.insert(tk.END, content)

        else:
            messagebox.showwarning("Uyarı", "Dosya sistemine daha dönüştürülmedi.")

    def optimization(self):
        number_of_non_empty = 0
        for block in self.table.block_list:
            if block.status == 1:
                number_of_non_empty += 1

        default_number_of_non_empty = int((self.table.block_number * 2) / 3)

        result = False
        if number_of_non_empty < default_number_of_non_empty:
            ratio = int(number_of_non_empty * 1.5) / len(self.table.block_list) * 100
            size = (len(self.table.block_list) - int(number_of_non_empty * 1.5)) * self.table.block_size
            result = messagebox.askyesno("", f"Veri %{ratio} oranına küçülecek yani {size} byte küçülecek. Emin misin?")
        elif number_of_non_empty > default_number_of_non_empty:
            ratio = int(number_of_non_empty * 1.5) / len(self.table.block_list) * 100
            size = (int(number_of_non_empty * 1.5) - len(self.table.block_list)) * self.table.block_size
            result = messagebox.askyesno("", f"Veri %{ratio} oranına büyüyecek yani {size} byte büyüyecek. Emin misin?")
        else:
            messagebox.showinfo("", "Veri optimize haldedir.")

        # Arttırma
        if result and number_of_non_empty > default_number_of_non_empty:
            new_table_number = int(number_of_non_empty * 1.5)
            new_position_list = [number for number in range(self.table.block_number, new_table_number)]
            random.shuffle(new_position_list)
            
            last_id = max(self.table.block_list, key=lambda x: x.id).id
            offset = 48 + 24 * self.table.block_number

            for position in new_position_list:
                block_offset = offset + self.table.block_size * position
                last_id += 1
                self.table.block_list.append(Block(last_id, block_offset, 0, 0, 0, 0))
            
            new_offset = 48 + 24 * new_table_number
            for block in self.table.block_list:
                block.offset += (new_offset - offset)
            self.table.block_number = new_table_number
            with open(self.current_file_path, "r+b") as file:
                file.seek(offset)

                # İleride sorun çıkartabilir
                data = file.read()      

                file.seek(40)
                file.write(chiper_utils.encrypt_data(self.table.to_binary(), self.key, self.nonce, 4))
                for block in self.table.block_list:
                    file.write(chiper_utils.encrypt_data(block.to_binary(), self.key, self.nonce, block.id))
                file.write(data)

            messagebox.showinfo("Bilgi", "Optimizasyon tamamlandı.")

        # Azaltma
        elif result and number_of_non_empty < default_number_of_non_empty:
            new_table_number = int(number_of_non_empty * 1.5)
            self.table.block_list.sort(key=lambda x: x.offset)
            new_table = self.table.block_list[:new_table_number]
            delete_table = self.table.block_list[new_table_number:]

            offset = 48 + 24 * self.table.block_number
            new_offset = 48 + 24 * new_table_number

            with open(self.current_file_path, "r+b") as file:
                for block in delete_table:
                    if block.status == 1:
                        new_block = next((block for block in new_table if block.status == 0), None)
                        file.seek(block.offset)
                        if block.type == 0:
                            data = chiper_utils.decrypt_data(file.read(268), self.key, self.nonce, block.id)
                        elif block.type == 1:
                            data = chiper_utils.decrypt_data(file.read(self.table.block_size), self.key, self.nonce, block.id)
                        file.seek(new_block.offset)
                        if block.type == 0:
                            file.write(chiper_utils.encrypt_data(data, self.key, self.nonce, new_block.id))
                            file.write(chiper_utils.create_dummy_data(self.table.block_size - 268))
                        elif block.type == 1:
                            file.write(chiper_utils.encrypt_data(data, self.key, self.nonce, new_block.id))
                        new_block.status = 1
                        new_block.type = block.type
                        new_block.file_no = block.file_no
                        new_block.order_no = block.order_no

                self.table.block_list.clear()
                self.table.block_list = new_table[:]
                self.table.block_list.sort(key=lambda x: x.id)
                self.table.block_number = new_table_number

                for i, block in enumerate(self.table.block_list):
                    file.seek(48 + 24 * i)
                    table_block = Block.from_binary(chiper_utils.decrypt_data(file.read(24), self.key, self.nonce, block.id))
                    file.seek(block.offset)
                    if block.type == 0:
                        data = chiper_utils.decrypt_data(file.read(268), self.key, self.nonce, block.id)
                    elif block.type == 1:
                        data = chiper_utils.decrypt_data(file.read(self.table.block_size), self.key, self.nonce, block.id)

                    block.id = i + 1
                    file.seek(48 + 24 * i)
                    file.write(chiper_utils.encrypt_data(table_block, self.key, self.nonce, block.id))
                    file.seek(block.offset)
                    if block.type == 0:
                        file.write(chiper_utils.encrypt_data(data, self.key, self.nonce, block.id))
                        file.write(chiper_utils.create_dummy_data(self.table.block_size - 268))
                    elif block.type == 1:
                        file.write(chiper_utils.encrypt_data(data, self.key, self.nonce, block.id))
                    

                file.seek(offset)
                # İleride sorun çıkarabilir.
                data = file.read()

                file.seek(40)
                file.write(chiper_utils.encrypt_data(self.table.to_binary(), self.key, self.nonce, 4))      
                for block in self.table.block_list:
                    block.offset += (new_offset - offset)
                    file.write(chiper_utils.encrypt_data(block.to_binary(), self.key, self.nonce, block.id))
                file.write(data)
                file.seek(0)
                file.truncate(new_offset + self.table.block_size * self.table.block_number)

            messagebox.showinfo("Bilgi", "Optimizasyon tamamlandı.")

    @staticmethod
    def clear_treeview():
        for item in treeview.get_children():
            treeview.delete(item)

    def print_nodes(self):
        for node in self.current_nodes:
            print(node)

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
        'test': "assets/test.png",
        'optimize': "assets/optimize.png"
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
    photo_optimize = create_icon(icons['optimize'])

    # Menu
    menu_bar = tk.Menu(app)
    app.config(menu=menu_bar)

    file_menu = tk.Menu(menu_bar, tearoff=0, font=custom_font)
    file_menu.add_command(label="Optimize Et", command=file_system.optimization, image=photo_optimize, compound=tk.LEFT)
    file_menu.add_command(label="Dönüştür", command=file_system.run, image=photo_run, compound=tk.LEFT)
    file_menu.add_command(label="Dosya Sistem Seç", command=file_system.open_file_system, image=photo_import, compound=tk.LEFT)
    file_menu.add_command(label="Klasör Seç", command=file_system.open_folder, image=photo_export, compound=tk.LEFT)

    operation_menu = tk.Menu(menu_bar, tearoff=0, font=custom_font)
    operation_menu.add_command(label="Yeni Dosya", command=file_system.new_file, image=photo_new_file, compound=tk.LEFT)
    operation_menu.add_command(label="Yeni Klasör", command=file_system.new_folder, image=photo_new_folder, compound=tk.LEFT)
    operation_menu.add_command(label="Düzenle", command=file_system.edit, image=photo_edit, compound=tk.LEFT)
    operation_menu.add_command(label="Sil", command=file_system.delete, image=photo_delete, compound=tk.LEFT)
    operation_menu.add_command(label="Yeniden İsimlendir", command=file_system.rename, image=photo_rename, compound=tk.LEFT)


    test_menu = tk.Menu(menu_bar, tearoff=0, font=custom_font)
    test_menu.add_command(label="Print Nodes", command=file_system.print_nodes, image=photo_test, compound=tk.LEFT)
    test_menu.add_command(label="Print Shuffle Info", command="", image=photo_test, compound=tk.LEFT)
    test_menu.add_command(label="Print Treeview Item", command="", image=photo_test, compound=tk.LEFT)

    menu_bar.add_cascade(label="Komutlar", menu=file_menu)
    menu_bar.add_cascade(label="Eylemler", menu=operation_menu)
    menu_bar.add_cascade(label="Testler", menu=test_menu)

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