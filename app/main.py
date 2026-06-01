import customtkinter as ctk
import tkinter as tk
from .config import APPEARANCE_MODE
from .ui.mainframe import SAFIPNMainframeInterface


def main():
    ctk.set_appearance_mode(APPEARANCE_MODE)
    app = SAFIPNMainframeInterface()

    ruta_icono = "/home/kaliz/Documentos/Progra/safipn/front/Assets/safipn_logo.png"
    imagen_icono = tk.PhotoImage(file=ruta_icono)
    app.iconphoto(True, imagen_icono)

    app.mainloop()
    

if __name__ == "__main__":
    main()
