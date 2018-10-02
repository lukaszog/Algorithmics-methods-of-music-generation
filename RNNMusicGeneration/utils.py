import matplotlib

matplotlib.use('Agg')
import glob
import os
import pickle
import re
import numpy as np
import numpy
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, TensorBoard
from keras.models import model_from_json
from keras.utils import np_utils
from music21 import converter, instrument, note, chord
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt


def save_model_to_json(model, dir):
    with open(os.path.join(dir, 'model.json'), 'w') as f:
        f.write(model.to_json())


def load_model_from_json(model_dir):
    with open(os.path.join(model_dir, 'model.json'), 'r') as f:
        model = model_from_json(f.read())

    checkpoint = max(glob.iglob(model_dir + '/weights/*.hdf5'),
                     key=os.path.getctime)
    if checkpoint:
        logging("Load weights {}".format(checkpoint))
        model.load_weights(checkpoint)
    return model

def create_results_dir():
    results = os.listdir('results')
    results = [directory for directory in results if os.path.isdir(os.path.join('results', directory))]

    last_dir = 0
    for directory in results:
        try:
            last_dir = max(int(directory), last_dir)
        except ValueError as e:
            pass
    results_dir_new = os.path.join('results', str(last_dir + 1).rjust(2, '0'))

    os.mkdir(results_dir_new)
    os.mkdir(os.path.join(results_dir_new, 'weights'))
    os.mkdir(os.path.join(results_dir_new, 'logs'))

    return results_dir_new


def get_results_dir(directory="default"):
    if directory == "default":
        directory = [os.path.join('results', d) for d in os.listdir('results') \
                     if os.path.isdir(os.path.join('results', d))]
        resutls_dir = max(directory, key=os.path.getmtime)
    else:
        return directory

    return resutls_dir


def logging(message):
    print('[*** LOG MESSAGE ***] {}'.format(message))


def model_callbacks(results):
    callbacks_list = []
    weight_pattern = 'checkpoint-epoch_{epoch:03d}-val_acc_{val_acc:.3f}-loss_{loss:.3f}.hdf5'
    filepath = os.path.join(results, 'weights', weight_pattern)

    callbacks_list.append(ModelCheckpoint(
        filepath,
        monitor='val_acc',
        verbose=1,
        save_best_only=True,
        mode='min'
    ))

    callbacks_list.append(TensorBoard(
        log_dir=os.path.join(results, 'logs'),
        write_graph=True,
        write_images=False,
        histogram_freq=1
    ))

    callbacks_list.append(ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.2,
        patience=5,
        verbose=1,
        mode='auto',
        min_lr=0
    ))

    return callbacks_list


def get_notes():
    notes = []

    for file in glob.glob("midi/*.mid"):
        midi = converter.parse(file)
        print("Parsing %s" % file)
        notes_to_parse = None
        try:
            ins = instrument.partitionByInstrument(midi)
            notes_to_parse = ins.parts[0].recurse()
        except:
            notes_to_parse = midi.flat.notes

        for element in notes_to_parse:
            if isinstance(element, note.Note):
                notes.append(str(element.pitch))
            elif isinstance(element, chord.Chord):
                notes.append('.'.join(str(n) for n in element.normalOrder))

    with open('data/notes-preludia', 'wb') as filepath:
        pickle.dump(notes, filepath)
    return notes


def load_data(directory="data/notes-preludia"):

    logging("Dataset: {}".format(directory))
    notes = pickle.load(open(directory, "rb"))
    # print(notes)
    return notes


def prepare_sequences(notes, n_vocab, sequence_length=100, train=0):
    pitchnames = sorted(set(item for item in notes))

    note_to_int = dict((note, number) for number, note in enumerate(pitchnames))
    network_input = []
    network_output = []

    for i in range(0, len(notes) - sequence_length, 1):
        sequence_in = notes[i:i + sequence_length]
        sequence_out = notes[i + sequence_length]
        network_input.append([note_to_int[char] for char in sequence_in])
        network_output.append(note_to_int[sequence_out])

    n_patterns = len(network_input)

    if train != 1:
        network_input = numpy.reshape(network_input, (n_patterns, sequence_length, 1))
        network_input = network_input / float(n_vocab)

    else:
        # predykcja
        normalized_input = numpy.reshape(network_input, (n_patterns, sequence_length, 1))
        normalized_input = normalized_input / float(n_vocab)

    network_output = np_utils.to_categorical(network_output)

    X_train, X_test, y_train, y_test = train_test_split(network_input, network_output,
                                                        test_size=0.2, random_state=7, shuffle=True)
    if train == 1:
        return network_input, normalized_input
    return network_input, network_output, X_train, X_test, y_train, y_test


def generate_final_plots(history, results_dir):
    # acc history
    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.savefig(results_dir + "/acc_history.png")
    plt.close()

    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.savefig(results_dir + "/history_loss.png")


def one_hot_endoing(data):

    keyboard = [0 for i in range(91)]
    n = data.split(".")
    for m in n:
        f = note.Note(m)
        octave = int(f.octave if f.octave else 0)
        mantise = int("0x" + f.pitch.pitchClassString, 0)
        number = mantise + 12 * octave
        keyboard[number] = 1

    return keyboard