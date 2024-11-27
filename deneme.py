import tkinter as tk
from tkinter import ttk

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter Navigation Example")
        self.geometry("400x300")
        
        # Sayfaları saklayacak bir container (ana çerçeve)
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Sayfa yönetimi için bir dictionary
        self.frames = {}
        
        # Sayfaları oluştur ve container'a ekle
        for F in (HomePage, Page1, Page2):
            frame = F(parent=self.container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Başlangıç sayfasını göster
        self.show_frame(HomePage)
    
    def show_frame(self, page_class):
        """Belirtilen sayfayı ekrana getirir."""
        frame = self.frames[page_class]
        frame.tkraise()

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = ttk.Label(self, text="Ana Sayfa", font=("Arial", 16))
        label.pack(pady=10)
        
        button1 = ttk.Button(self, text="Sayfa 1'e Git", 
                             command=lambda: controller.show_frame(Page1))
        button1.pack()
        
        button2 = ttk.Button(self, text="Sayfa 2'ye Git", 
                             command=lambda: controller.show_frame(Page2))
        button2.pack()

class Page1(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = ttk.Label(self, text="Sayfa 1", font=("Arial", 16))
        label.pack(pady=10)
        
        button = ttk.Button(self, text="Ana Sayfa'ya Dön", 
                            command=lambda: controller.show_frame(HomePage))
        button.pack()

class Page2(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = ttk.Label(self, text="Sayfa 2", font=("Arial", 16))
        label.pack(pady=10)
        
        button = ttk.Button(self, text="Ana Sayfa'ya Dön", 
                            command=lambda: controller.show_frame(HomePage))
        button.pack()

if __name__ == "__main__":
    app = App()
    app.mainloop()
