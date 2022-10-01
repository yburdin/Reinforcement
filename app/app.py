from tkinter import filedialog as fd
from tkinter import ttk, Menu, Tk
from PIL import Image as pimage
from PIL import ImageTk as pimagetk


class App:
    def __init__(self, master):
        self.master = master
        self.master.geometry('300x300')
        self.master.resizable(False, False)

        main_menu = Menu(self.master)
        self.master.config(menu=main_menu)

        main_menu.add_command(label='Load settings json', command=self.load_json)

    def load_json(self):
        pass


if __name__ == '__main__':
    root = Tk()
    app = App(root)
    root.title('Reinpycement')

    ico = pimage.open('icon.png')
    photo = pimagetk.PhotoImage(ico)
    root.iconphoto(False, photo)

    root.mainloop()
