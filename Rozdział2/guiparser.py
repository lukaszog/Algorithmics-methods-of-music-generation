import os
import tkinter.ttk as ttk
from collections import defaultdict
from tkinter import *

from PIL import ImageTk, Image
from music21 import *
from nltk import CFG
from nltk.parse.generate import generate

filepath = './'

us = environment.UserSettings()
us['lilypondPath'] = 'C:/Program Files (x86)/LilyPond/usr/bin/lilypond.exe'


class Generate:

    def __init__(self, n, depth):
        self.track_array = []
        self.num_to_note = dict()
        self.result_dict = defaultdict(dict)
        self.tracks_notes = []
        self.productions = []
        self.n = n
        self.depth = depth
        self.gramma = Model().read_file()

        self.convert_num_to_notes()
        self.generate_from_grammar(self.n, self.depth)
        self.track_to_notes()
        self.generate_files()
        self.clear_files()

    def convert_num_to_notes(self):
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        num_notes = 127
        num_octaves = 10
        octave_count = 0

        for i in range(0, num_notes + 1):
            self.num_to_note.update({str(i): notes[i % len(notes)] + str(octave_count)})
            if i % 12 == 11:
                octave_count += 1

    def generate_from_grammar(self, n, depth):
        grammar = CFG.fromstring(self.gramma)
        print("Generuje dla n " + n + " i depth " + depth)
        for track in generate(grammar, n=int(n), depth=int(depth)):
            self.track_array.append(' '.join(track))
            # produkcje
            numbers = " ".join(track)
            self.productions.append(numbers)

    def track_to_notes(self):

        for tr in self.track_array:
            s1 = stream.Stream()
            for n in re.findall(r'\S+', tr):
                s1.append(note.Note(self.num_to_note.get(str(n.split('.')[0])), quarterLength=int(n.split('.')[1])))
            self.tracks_notes.append(s1)

    def generate_files(self):
        conv = converter.subConverters.ConverterLilypond()
        for i, k in enumerate(self.tracks_notes):
            print(k)
            self.result_dict[i]['productions'] = self.productions[i]
            self.result_dict[i]['midi_file'] = filepath + 'file' + str(i) + '.midi'
            self.result_dict[i]['png_file'] = filepath + 'file' + str(i) + '.png'
            k.write('midi', fp=filepath + 'file' + str(i) + '.midi')
            conv.write(k, fmt='lilypond', fp=filepath + 'file' + str(i), subformats=['png', 'midi'])

    def clear_files(self):
        test = os.listdir(filepath)
        for item in test:
            if item.endswith(".eps") or item.endswith(".count") \
                    or item.endswith(".tex") or item.endswith(".texi"):
                os.remove(os.path.join(filepath, item))


class Controller:
    def __init__(self):
        self.root = Tk()
        self.view = View(self.root)
        self.model = Model()
        self.view.register(self)

    def run(self):
        self.root.title("GUI Grammar Parser")
        self.view.Text1.insert(INSERT, self.model.read_file())
        self.root.deiconify()
        self.root.mainloop()

    def generate(self, n, depth):
        print("Klikniecie przysku...." + n + " " + depth)
        g = Generate(n, depth)
        self.view.create_window(g.result_dict)
        print(g.result_dict)


class Model:
    def __init__(self):
        pass

    @staticmethod
    def read_file():
        with open("grammar.txt") as file:
            data = file.read()
        return data


class View():

    def create_window(self, result_dict):

        root = Tk()
        style = ttk.Style()
        style.theme_use('clam')

        content = ttk.Frame(root)

        frame_relx = 0.08
        frame_row = 0

        print(len(result_dict))
        for k, v in result_dict.items():
            print(v['midi_file'])

        for k, v in result_dict.items():
            frame = ttk.LabelFrame(content, width=800, height=190, text=v['productions'])
            frame.place(relx=0.08, rely=0.0)

            canvas = Canvas(frame, width=780, height=160)
            canvas.pack(expand=YES, fill=BOTH)
            canvas.place(relx=0.01, rely=0.0)

            im = Image.open(v['png_file'])
            ph = ImageTk.PhotoImage(im, master=content)

            canvas.image = ph
            canvas.create_image(0, 0, image=ph, anchor=NW)

            btn = ttk.Button(content, text="Zagraj", command=lambda: self.play(v['midi_file']))

            content.grid(column=0, row=0)
            frame.grid(column=0, row=frame_row, columnspan=3, rowspan=2, padx=(10, 10), pady=(10, 10))
            btn.grid(column=3, row=frame_row, columnspan=2, rowspan=2, padx=(10, 10), pady=(10, 10))

            frame_relx += 0.10
            frame_row += 3

    def play(self, midifile):
        mf = midi.MidiFile()
        mf.open(midifile)
        mf.read()
        mf.close()
        s = midi.translate.midiFileToStream(mf)

        sp = midi.realtime.StreamPlayer(s)
        sp.play()

    def __init__(self, master, top=None):
        self.master = master
        self.controller = None
        self.frame = Frame(self.master)
        self.style = ttk.Style()
        if sys.platform == "win32":
            self.style.theme_use('clam')
        self.style.theme_use('clam')

        master.geometry("600x450+650+150")

        self.Frame1 = ttk.Frame(master)
        self.Frame1.place(relx=0.02, rely=0.09, relheight=0.88, relwidth=0.46)
        self.Frame1.configure(relief=GROOVE)
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief=GROOVE)
        # self.Frame1.configure(background="#d9d9d9")
        self.Frame1.configure(width=275)

        self.Text1 = Text(self.Frame1)
        self.Text1.place(relx=0.04, rely=0.03, relheight=0.95, relwidth=0.92)
        self.Text1.configure(font="TkTextFont")
        self.Text1.configure(undo="1")
        self.Text1.configure(width=254)
        self.Text1.configure(wrap=WORD)

        self.Frame2 = ttk.Frame(master)
        self.Frame2.place(relx=0.5, rely=0.09, relheight=0.88, relwidth=0.46)
        self.Frame2.configure(relief=GROOVE)
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief=GROOVE)
        self.Frame2.configure(width=275)

        self.TLabel3 = ttk.Label(self.Frame2)
        self.TLabel3.place(relx=0.04, rely=0.08, height=19, width=59)
        self.TLabel3.configure(relief=FLAT)
        self.TLabel3.configure(text='''Głębokość''')

        self.TLabel4 = ttk.Label(self.Frame2)
        self.TLabel4.place(relx=0.04, rely=0.23, height=19, width=75)
        self.TLabel4.configure(relief=FLAT)
        self.TLabel4.configure(text='''Liczba iteracji''')

        self.TEntry1 = ttk.Entry(self.Frame2)
        self.TEntry1.place(relx=0.51, rely=0.08, relheight=0.06, relwidth=0.46)
        self.TEntry1.configure(takefocus="")

        self.TEntry2 = ttk.Entry(self.Frame2)
        self.TEntry2.place(relx=0.51, rely=0.23, relheight=0.06, relwidth=0.46)
        self.TEntry2.configure(takefocus="")

        self.Button1 = ttk.Button(self.Frame2)
        self.Button1.place(relx=0.55, rely=0.38, height=64, width=107)

        go_function = lambda: self.controller.generate(self.TEntry2.get(), self.TEntry1.get())

        self.Button1.configure(text='''Generuj...''', command=go_function)
        self.Button1.configure(width=107)

        self.TLabel1 = ttk.Label(master)
        self.TLabel1.place(relx=0.02, rely=0.04, height=19, width=86)
        self.TLabel1.configure(relief=FLAT)
        self.TLabel1.configure(text='''Gramatyka''')

        self.TLabel2 = ttk.Label(master)
        self.TLabel2.place(relx=0.5, rely=0.04, height=19, width=36)
        self.TLabel2.configure(relief=FLAT)
        self.TLabel2.configure(text='''Opcje''')

    def register(self, controller):
        self.controller = controller


if __name__ == '__main__':
    c = Controller()
    c.run()
