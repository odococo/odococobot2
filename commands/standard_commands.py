import json
import random
import unicodedata as ucd
from dataclasses import dataclass

from commands.commands import Command
from telegram.wrappers import InlineKeyboard, InlineButton, Message


@dataclass
class Standard(Command):
    def echo(self) -> Message:
        return self.answer("To you from you: {}".format(" ".join(self.params())))

    def random(self) -> Message:
        """
        Estrae 1 numero random tra min (intero) e max (intero

        Sintassi: /random min max [X]
        """
        min_value = int(self.params()[0])
        max_value = int(self.params()[1])

        return self.answer(str(random.randint(min_value, max_value)))

    def roll(self) -> Message:
        if not len(self.params()):
            text = "Specifica il numero di facce:"
            keyboard = InlineKeyboard()
            keyboard.add(1,
                         InlineButton("6", "/{} 6".format(self.command())),
                         InlineButton("10", "/{} 10".format(self.command())),
                         InlineButton("20", "/{} 20".format(self.command())))
            keyboard.add(2,
                         InlineButton("50", "/{} 50".format(self.command())),
                         InlineButton("100", "/{} 100".format(self.command())),
                         InlineButton("1000", "/{} 1000".format(self.command())))

            return self.answer(text, keyboard)
        elif len(self.params()) == 1:
            facce = int(self.params()[0])
            text = "Specifica il numero di lanci:"
            keyboard = InlineKeyboard()
            keyboard.add(1,
                         InlineButton("1", "/{} {} 1".format(self.command(), facce)),
                         InlineButton("2", "/{} {} 2".format(self.command(), facce)),
                         InlineButton("3", "/{} {} 3".format(self.command(), facce)))
            keyboard.add(2,
                         InlineButton("4", "/{} {} 4".format(self.command(), facce)),
                         InlineButton("5", "/{} {} 5".format(self.command(), facce)),
                         InlineButton("6", "/{} {} 6".format(self.command(), facce)))
            keyboard.add(3,
                         InlineButton("7", "/{} {} 7".format(self.command(), facce)),
                         InlineButton("8", "/{} {} 8".format(self.command(), facce)),
                         InlineButton("9", "/{} {} 9".format(self.command(), facce)))

            return self.replace(text, keyboard)
        else:
            facce = int(self.params()[0])
            lanci = int(self.params()[1])
            text = "Dado a {} facce\n".format(facce)
            text += "\n".join(["Lancio {} di {}: {}".format(i + 1, lanci, lancio) for i, lancio in
                               enumerate(random.choices(range(1, facce), k=lanci))])

            return self.replace(text)

    def utf(self) -> Message:
        string = " ".join(self.params())

        return self.answer(
            "\n".join(["Input: {}\nCodifica: {}\nCode point: {}\nNome: {}\nCategoria: {}".format(
                carattere, ord(carattere), json.dumps(carattere), ucd.name(carattere), ucd.category(carattere))
                for carattere in string]))

    def string(self) -> Message:
        codice = self.params()[0]

        if codice.isdigit():  # codice unicode
            return self.answer("Il carattere corrispondente a {} è {}".format(codice, chr(int(codice))))
        else:  # codifica unicode \u...
            return self.answer(
                "Il carattere corrispondente a {} è {}".format(codice, codice.encode('utf-8').decode('unicode_escape')))
