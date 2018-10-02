import matplotlib

matplotlib.use('Agg')
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM, Embedding
from keras.layers import Activation
from keras.optimizers import *
from keras.activations import *
from keras.layers.advanced_activations import *

import utils
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('--midi_dir', type=str, default='midi',
                        help='MIDI files direcotry containing .mid files to use for training neural network')
    parser.add_argument('--data_file', type=str, default='data/notes-preludia',
                        help='Path to file containing done parse MIDI files')
    parser.add_argument('--results_dir', type=str, default='results',
                        help='Directory to store model in JSON format, logs for tensorboard and weights')
    parser.add_argument('--lstm_size', type=int, default=128, help='Size of LSTM layer')
    parser.add_argument('--layers', type=int, default=2, help='Number of layers in the neural network')
    parser.add_argument('--learning_rate', type=float, default=0.0001, help='Learning rate')
    parser.add_argument('--sequence_size', type=int, default=100, help='Sequence size for notes')
    parser.add_argument('--batch_size', type=int, default=128, help='Batch size')
    parser.add_argument('--dropout', type=float, default=0.3,
                        help='Dropout percentage value. One of regularization method')
    parser.add_argument('--optimizer', choices=['sgd', 'rmsprop', 'adagrad', 'adadelta',
                                                'adam', 'adamax', 'nadam'], default='rmsprop',
                        help='Optimization algorithm to use')
    parser.add_argument('--activation', choices=['softmax', 'sigmoid', 'linear',
                                                 'tanh', 'elu', 'selu', 'softplus',
                                                 'softsign', 'relu'], default='softmax',
                        help='Activation function to use')

    return parser.parse_args()


def prepare_network():
    args = parse_arguments()

    notes = utils.load_data(args.data_file)
    n_vocab = len(set(notes))
    results_dir = utils.create_results_dir()
    network_input, network_output, X_train, X_test, y_train, y_test = utils.prepare_sequences(notes, n_vocab)
    model = create_network(network_input, n_vocab, X_train, X_test, y_train, y_test, results_dir, args)
    train(model, network_input, network_output, X_train, X_test, y_train, y_test, results_dir)


def create_network(network_input, n_vocab, X_train, X_test, y_train, y_test, results_dir, args):
    model = Sequential()
    for index in range(args.layers):

        if index == 0:
            if args.layers > 1:
                return_seq = True
            else:
                return_seq = False
            model.add(LSTM(units=args.lstm_size,
                           input_shape=(network_input.shape[1], network_input.shape[2]),
                           return_sequences=return_seq))
        else:
            if not index == args.layers -1:
                return_seq = True
            else:
                return_seq = False
            model.add(LSTM(units=args.lstm_size, return_sequences=return_seq))
        model.add(Dropout(rate=args.dropout))
    model.add(Dense(n_vocab))

    if args.activation not in ['LeakyReLU', 'PReLU', 'ELU', 'ThresholdedReLU', 'Softmax', 'ReLU']:
        model.add(Activation(activation=args.activation))
    else:
        if args.activation == 'LeakyReLU':
            model.add(LeakyReLU())
        elif args.activation == 'PReLU':
            model.add(PReLU())
        elif args.activation == 'ELU':
            model.add(ELU())
        elif args.activation == 'ThresholdedReLU':
            model.add(ThresholdedReLU())
        elif args.activation == 'Softmax':
            model.add(Softmax())
        elif args.activation == 'ReLU':
            model.add(ReLU())
    if 'optimizer' in args:
        kwargs = dict()

        if args.learning_rate:
            kwargs['lr'] = args.learning_rate
        if args.optimizer == 'SGD' or args.optimizer == 'sgd':
            optimizer = SGD(**kwargs)
        elif args.optimizer == 'adam':
            optimizer = Adam(**kwargs)
        elif args.optimizer == 'adagrad':
            optimizer = Adagrad(**kwargs)
        elif args.optimizer == 'adadelta':
            optimizer = Adadelta(**kwargs)
        elif args.optimizer == 'adamax':
            optimizer = Adamax(**kwargs)
        elif args.optimizer == 'nadam':
            optimizer = Nadam(**kwargs)
        elif args.optimizer == 'rmsprop':
            optimizer = RMSprop(**kwargs)
        else:
            utils.logging("Error: {} is not supported optimizer...".format(args.optimizer))
            quit()
    else:
        optimizer = RMSprop()

    model.summary()
    model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    return model


def train(model, network_input, network_output, X_train, X_test, y_train, y_test, results_dir):
    callbacks_list = utils.model_callbacks(results_dir)
    utils.logging('Loaded model callbacks')

    utils.save_model_to_json(model, results_dir)
    utils.logging('Model saved to file: {}/{}'.format(results_dir, 'model.json'))

    history = model.fit(network_input, network_output,
                        validation_data=(X_test, y_test),
                        validation_split=0.33,
                        epochs=200,
                        batch_size=64,
                        callbacks=callbacks_list,
                        verbose=1,
                        )

    utils.generate_final_plots(history, results_dir)


if __name__ == '__main__':
    prepare_network()
