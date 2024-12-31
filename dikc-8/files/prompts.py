from time import time
from os import getenv, makedirs, name
from os.path import join, isfile, exists, splitext

from tkinter import *
from tkinter.ttk import *
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import showerror
from tkinter.filedialog import askopenfilename, askdirectory

def browse1():
    entries[0].set(askopenfilename(filetypes=[('%s files' %filetype.upper(), '.'+filetype)]))

def browse2():
    entries[1].set(askdirectory())

def done_both():
    # check both file and folder
    path = entries[1].get()
    if not _done(): return
    ok = exists(path)
    if not exists(path):
        try:
            makedirs(path)
            ok = True
        except: return showerror('Critical error', 'Wrong file entry')
    if ok: tk.destroy()

def done_one():
    # only check file
    if _done(): tk.destroy()

def _done():
    file = entries[0].get()
    if not isfile(file):
        showerror('Critical error', 'Wrong file entry')
        return 0

    with open('last', 'w', encoding='utf-8') as f:
        f.write(splitext(file)[0]+'.')
    return 1

def ask_both(_type):
    global tk, entries, filetype
    filetype = _type

    tk = Tk()
    tk.title('Choose file and export path')
    tk.resizable(0, 0)

    entries = [StringVar() for i in (0, 1)]
    if exists('last'):
        with open('last', encoding='utf-8') as f:
            entries[0].set(f.read()+_type)
    if name == 'nt':
        entries[1].set(join(getenv('appdata'), '.minecraft\\schematics\\DIKC-8 ROMs'))
    else:
        entries[1].set('Schematics')

    Label(tk, text='Choose %s file' %filetype).grid(padx=5, pady=5)
    Entry(tk, width=50, textvariable=entries[0]).grid(padx=5, pady=5)
    Button(tk, text='Browse', command=browse1).grid(column=1, row=1, padx=(0, 5))
    Label(tk, text='Choose export folder').grid(padx=5, pady=5)
    Entry(tk, width=50, textvariable=entries[1]).grid(padx=5, pady=5)
    Button(tk, text='Browse', command=browse2).grid(column=1, row=3, padx=(0, 5))
    Button(tk, text='Done', width=63, command=done_both).grid(columnspan=2, padx=5, pady=5)

    tk.mainloop()
    return entries[0].get(), entries[1].get()

def ask_one(_type):
    global tk, entries, filetype
    filetype = _type

    tk = Tk()
    tk.title('Choose file to simulate')
    tk.resizable(0, 0)

    entries = [StringVar()]
    if exists('last'):
        with open('last', encoding='utf-8') as f:
            entries[0].set(f.read()+_type)

    Label(tk, text='Choose %s file' %filetype).grid(padx=5, pady=5)
    Entry(tk, width=50, textvariable=entries[0]).grid(padx=5, pady=5)
    Button(tk, text='Browse', command=browse1).grid(column=1, row=1, padx=(0, 5))
    Button(tk, text='Done', width=63, command=done_one).grid(columnspan=2, padx=5, pady=5)

    tk.mainloop()
    return entries[0].get()

def log_init(title):
    global tk, log_text, start
    tk = Tk()
    tk.title('%s details' %title.capitalize())
    tk.resizable(0, 0)

    log_text = ScrolledText(tk, width=50, height=10, font=('courier new', 11))
    log_text.pack()
    tk.update()

    start = time()

def log(*args):
    log_text.insert(1.0, '[%.5f] ' %(time()-start) + ' '.join(args) + '\n')
    tk.update()

def log_wait(): tk.mainloop()
