##########
# DONT NEED THIS CUZ I WILL BE READING PYTHON FILES INSTEAD
##########

# TODO: dialog when not saved

from tkinter import *
from tkinter.ttk import *
from tkinter.scrolledtext import *
from tkinter.filedialog import *

# from https://stackoverflow.com/q/3781670
def highlight_pattern(self, pattern, tag, start="1.0", end="end",
                          regexp=False):
        '''Apply the given tag to all text that matches the given pattern

        If 'regexp' is set to True, pattern will be treated as a regular
        expression according to Tcl's regular expression syntax.
        '''

        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = IntVar()
        while True:
            index = self.search(pattern, "matchEnd","searchLimit",
                                count=count, regexp=regexp)
            if index == "": break
            if count.get() == 0: break # degenerate pattern which matches zero-length strings
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")
setattr(ScrolledText, 'highlight_pattern', highlight_pattern)

def new():
    global filename
    text.delete(1.0, END)
    filename = None

def open_():
    global filename
    f = askopenfilename(filetypes=types)
    if f:
        filename = f
        with open(filename, encoding='utf-8') as f:
            text.delete(1.0, END)
            text.insert(1.0, f.read())
        colorize()

def save():
    if filename is None:
        saveas()

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text.get(1.0, END))

def saveas():
    global filename
    f = asksaveasfilename(filetypes=types)
    if f:
        if not f.endwsith(types[0][1][1:]):
            # force extension
            f += types[0][1]
        filename = f
        save()

def close():
    tk.destroy()

def colorize():
    # remove highlighting
    for tag in text.tag_names():
        text.tag_delete(tag)

    # add it back
    text.tag_configure('red', foreground='red')
    text.tag_configure('blue', foreground='blue')
    for cmd in ['if', 'for', 'while']:
        text.highlight_pattern(cmd, 'red')
    text.highlight_pattern('0', 'blue')
    text.highlight_pattern('1', 'blue')

def pressed(evt):
    if evt.char:
        colorize()

def make_window():
    global tk, text
    tk = Tk()
    tk.title('Assembly editor')
    tk.bind('<Key>', pressed)

    menu = Menu(tk)
    filemenu = Menu(menu, tearoff=0)
    filemenu.add_command(label='New', command=new)
    filemenu.add_command(label='Open', command=open_)
    filemenu.add_command(label='Save', command=save)
    filemenu.add_command(label='Save as...', command=saveas)
    filemenu.add_separator()
    filemenu.add_command(label='Exit', command=close)
    menu.add_cascade(label='File', menu=filemenu)
    tk.config(menu=menu)

    text = ScrolledText(tk, width=80, height=40, font=('Consolas', 10))
    text.pack()

types = (('Assembly file (mc)', '.ass'),)
filename = None

make_window()
tk.mainloop()
