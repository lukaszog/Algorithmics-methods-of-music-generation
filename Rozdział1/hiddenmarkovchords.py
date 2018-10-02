import tkinter as tk
from tkinter import *

from PIL import ImageTk, Image
from music21 import *
from hmmlearn import hmm
import numpy as np


us = environment.UserSettings()
us['lilypondPath'] = 'C:/Program Files (x86)/LilyPond/usr/bin/lilypond.exe'
us['musescoreDirectPNGPath'] = 'C:/Program Files (x86)/MuseScore 2/bin/MuseScore.exe'
us['musicxmlPath'] = 'C:/Program Files (x86)/MuseScore 2/bin/MuseScore.exe'

for key in sorted(us.keys()):
    print(key)

class ExampleApp(tk.Tk):
    def __init__(self):
        root = tk.Tk.__init__(self)
        content = tk.Frame(self)


        self.initial_chords()

        frame = tk.LabelFrame(content, width=800, height=190)
        frame.place(relx=0.08, rely=0.0)

        canvas = Canvas(self, width=780, height=100)
        canvas.pack(expand=YES, fill=BOTH)
        canvas.place(relx=0.01, rely=0.0)

        im = Image.open('file.png')
        ph = ImageTk.PhotoImage(im, master=content)

        canvas.image = ph
        canvas.create_image(0, 0, image=ph, anchor=NW)
        canvas.pack()
        content.pack()

        play_chords = tk.Button(text="Zagraj akordy", height=5, width=20,
                                font=44, command=lambda: self.play('initial.midi'))
        play_chords.pack()

        self.start_prob = np.array([1.0, 0.0, 0.0])
        self.emissionmat = [[0.4, 0.0, 0.4],
                            [0.3, 0.3, 0.3],
                            [0.2, 0.8, 0.0]]

        self.transmat = [[0.4, 0.4, 0.2],
                         [0.1, 0.1, 0.8],
                         [0.0, 0.3, 0.7]]

        t = SimpleTable(self, 3, 3, self.emissionmat)
        t2 = SimpleTable(self, 3, 3, self.transmat)

        emmision_label = tk.Label(text="Macierz prawdopodobienstw D(II), G(V), C(I):")
        emmision_label.config(font=44)
        emmision_label.pack()

        t.pack(fill="x")
        prob_label = tk.Label(text="Macierz emisji dominanta (7), minor (min7), major7:")
        prob_label.config(font=44)
        prob_label.pack()
        t2.pack(fill="x")

        generate_button = tk.Button(text="Generuj akordy", height=5, width=20,
                                    command=lambda: self.generate_music(),
                                    font=44, padx=20, pady=20)
        generate_button.pack()

    def generate_music(self):
        root = Tk()
        root.title('Result')
        content = tk.Frame(root)
        content.pack()

        start_prob = np.array([1.0, 0.0, 0.0])

        chord_model = hmm.MultinomialHMM(n_components=2)
        chord_model.startprob_ = start_prob
        chord_model.transmat_ = np.array(self.transmat)
        chord_model.emissionprob_ = np.array(self.emissionmat)

        X, Z = chord_model.sample(20)
        state2name = {}
        state2name[0] = 'D'
        state2name[1] = 'G'
        state2name[2] = 'C'
        chords = [state2name[state] for state in Z]
        print(chords)

        obj2name = {}
        obj2name[0] = 'min7'
        obj2name[1] = 'maj7'
        obj2name[2] = '7'
        observations = [obj2name[item] for sublist in X for item in sublist]
        print(observations)

        chords = [''.join(chord) for chord in zip(chords, observations)]

        d7 = chord.Chord(['D4', 'F4', 'A4', 'C5'])
        dmin7 = chord.Chord(['D4', 'F-4', 'A4', 'C5'])
        dmaj7 = chord.Chord(['D4', 'F#4', 'A4', 'C#5'])

        c7 = d7.transpose(-2)
        cmin7 = dmin7.transpose(-2)
        cmaj7 = dmaj7.transpose(-2)

        g7 = d7.transpose(5)
        gmin7 = dmin7.transpose(5)
        gmaj7 = dmaj7.transpose(5)

        stream1 = stream.Stream()
        stream1.repeatAppend(dmin7, 1)
        stream1.repeatAppend(g7, 1)
        stream1.repeatAppend(cmaj7, 1)
        stream1.repeatAppend(cmaj7, 1)
        print(stream1)

        name2chord = {}
        name2chord['C7'] = c7
        name2chord['Cmin7'] = cmin7
        name2chord['Cmaj7'] = cmaj7

        name2chord['D7'] = d7
        name2chord['Dmin7'] = dmin7
        name2chord['Dmaj7'] = dmaj7

        name2chord['G7'] = g7
        name2chord['Gmin7'] = gmin7
        name2chord['Gmaj7'] = gmaj7

        hmm_chords = stream.Stream()
        for c in chords:
            hmm_chords.repeatAppend(name2chord[c], 1)

        # hmm_chords.show('png')

        conv = converter.subConverters.ConverterLilypond()
        conv.write(hmm_chords, fmt='lilypond', fp='new_chords', subformats=['png'])
        hmm_chords.write('midi', fp='new_chords.midi')

        frame = tk.LabelFrame(content, width=800, height=190)
        frame.place(relx=0.08, rely=0.0)

        canvas = Canvas(frame, width=780, height=160)
        canvas.pack(expand=YES, fill=BOTH)
        canvas.place(relx=0.01, rely=0.0)

        im = Image.open('new_chords.png')
        ph = ImageTk.PhotoImage(im, master=content)

        canvas.image = ph
        canvas.create_image(0, 0, image=ph, anchor=NW)

        btn = tk.Button(content, text="Zagraj", command=lambda: self.play('new_chords.midi'), font=50, width=20, height=5)
        frame.pack()
        btn.pack()

    def play(self, midifile):
        mf = midi.MidiFile()
        mf.open(midifile)
        mf.read()
        mf.close()
        s = midi.translate.midiFileToStream(mf)

        sp = midi.realtime.StreamPlayer(s)
        sp.play()

    def initial_chords(self):
        d7 = chord.Chord(['D4', 'F4', 'A4', 'C5'])
        dmin7 = chord.Chord(['D4', 'F-4', 'A4', 'C5'])
        dmaj7 = chord.Chord(['D4', 'F#4', 'A4', 'C#5'])

        chords = stream.Stream()

        chords.append(d7)
        d7.addLyric("D7")
        chords.append(dmin7)
        dmin7.addLyric("Dmin7")
        chords.append(dmaj7)
        dmaj7.addLyric("Dmaj7")

        g7 = d7.transpose(5)
        g7._setLyric("G7")
        chords.append(g7)
        gmin7 = dmin7.transpose(5)
        gmin7._setLyric("Gmin7")
        chords.append(gmin7)
        gmaj7 = dmaj7.transpose(5)
        gmaj7._setLyric("Gmaj7")
        chords.append(gmaj7)

        c7 = d7.transpose(-2)
        chords.append(c7)
        c7._setLyric("C7")
        cmin7 = dmin7.transpose(-2)
        chords.append(cmin7)
        cmin7._setLyric("Cmin7")
        cmaj7 = dmaj7.transpose(-2)
        chords.append(cmaj7)
        cmaj7._setLyric("Cmaj7")

        conv = converter.subConverters.ConverterLilypond()
        conv.write(chords, fmt='lilypond', fp='file', subformats=['png'])
        chords.write('midi', fp='initial.midi')


class SimpleTable(tk.Frame):
    def __init__(self, parent, rows, columns, array_data):

        tk.Frame.__init__(self, parent, background="black")
        self._widgets = []
        for row, trans in zip(range(0, rows), array_data):
            current_row = []
            for column, tran_value in zip(range(columns), trans):
                label = tk.Text(self, width=2, height=2, font=80)
                label.insert(INSERT, tran_value)
                label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                current_row.append(label)
            self._widgets.append(current_row)

        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)

        for row in self._widgets:
            for val in row:
                print(val.get("1.0", END))


if __name__ == "__main__":
    app = ExampleApp()
    app.title("Hidden Markov Chords")
    app.mainloop()
