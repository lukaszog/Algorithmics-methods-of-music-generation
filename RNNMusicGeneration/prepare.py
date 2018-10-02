import argparse
import glob
import os
import pickle

from music21 import converter, instrument, note, chord, interval, pitch


def parse_arguments():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--midi_dir', type=str, default='midi/',
                        help='MIDI files directory containing. mid files')
    parser.add_argument('--out_file', type=str, default='data/notes',
                        help='Path to file containing done parse MIDI files')
    parser.add_argument('--transpose', default='None',
                        type=str, help='Key to transpose all MIDI files')

    return parser.parse_args()


def parse_midi_files(midi_dir, args):
    notes = []
    files = []
    for file in glob.glob(midi_dir + "/*.mid"):
        files.append(os.path.dirname(os.path.realpath(__file__)) + "/" + file)

    k = 1
    for file in glob.glob(midi_dir + "/*.mid"):
        print("Parse file {} {}/{}".format(file, k, len(files)))
        midi = converter.parseFile(os.path.dirname(os.path.realpath(__file__)) + "/" + file)
        midi = midi[0]
        notes_to_parse = None

        try:
            s2 = instrument.partitionByInstrument(midi)
            notes_to_parse = s2.parts[0].recurse()
        except:
            notes_to_parse = midi.flat.notes
        i = 1
        for element in notes_to_parse:
            if isinstance(element, note.Note):
                notes.append(str(element.pitch))
            elif isinstance(element, chord.Chord):
                # print('Akord {}'.format(element.pitchNames[0]))
                # notes.append(element.pitchNames[0])
                notes.append(".".join(str(n) for n in element.pitchNames))
            i += 1
        k += 1

    with open(args.out_file, 'wb') as fw:
        pickle.dump(notes, fw)

    return notes


def create_midi_dir(midi_dir):
    results = os.listdir(midi_dir)
    results = [directory for directory in results if os.path.isdir(os.path.join(midi_dir, directory))]

    last_dir = 0
    for directory in results:
        try:
            last_dir = max(int(directory), last_dir)
        except ValueError as e:
            pass
    results_dir_new = os.path.join(midi_dir, str(last_dir + 1).rjust(2, '0'))
    os.mkdir(results_dir_new)

    return results_dir_new


def transpose(midi_dir, key):
    kk = 0
    save_dir = create_midi_dir(midi_dir)
    for fn in glob.glob(midi_dir + '/*.mid'):
        s = converter.parse(fn)
        k = s.analyze('key')
        i = interval.Interval(k.tonic, pitch.Pitch(key))
        sNew = s.transpose(i)
        head, tail = os.path.split(fn)
        filename = tail.split('.')[0]
        newFileName = save_dir + "/" + key + "_" + str(filename) + ".mid"
        sNew.write('midi', newFileName)
        print("Saved midi file to {}".format(newFileName))
        kk += 1
    return midi_dir


if __name__ == '__main__':
    args = parse_arguments()

    if args.transpose != 'None':
        directory = transpose(args.midi_dir, args.tranpose)
        parse_midi_files(directory, args)
    else:
        parse_midi_files(args.midi_dir, args)
