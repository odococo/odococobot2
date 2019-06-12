import json
from typing import Dict, List
import logging
import requests
from apscheduler.schedulers.background import BackgroundScheduler

from telegram.ids import lampo
from telegram.wrappers import Update, Chat, Message, Keyboard

max_length = 2048


class Bot:
    url = "https://api.telegram.org/bot{token}/{method}"
    scheduler = BackgroundScheduler()

    def __init__(self, token: str):
        self.token = token
        self.scheduler.start()

    def __execute(self, method: str, **params) -> Dict:
        """
        Esegue una httprequest con il metodo

        :param method: nome del metodo da eseguire
        :param params: parametri del metodo da eseguire
        :return: il contenuto della risposta oppure l'errore
        """
        request = requests.get(self.url.format(token=self.token, method=method), params=params)
        if request.ok:
            return request.json()['result']
        else:
            print(request.json())
            print(request.json().get('error', request.json().get('description', request.json())))

            return {}

    def add_cron_job(self, function: callable, single: bool, time_details: Dict[str, int]) -> str:
        job_id = self.scheduler.add_job(function, 'date' if single else 'interval', **time_details).id
        logging.info("Aggiunto job con id {}".format(job_id))

        return job_id

    def remove_cron_job(self, job_id: str):
        logging.info("Rimosso job con id {}".format(job_id))
        self.scheduler.remove_job(job_id)

    def dump(self, to: int = lampo, *args, **kwargs) -> Message:
        return self.send_message(to, json.dumps(args, indent=2, sort_keys=True) + "\n" + json.dumps(kwargs, indent=2,
                                                                                                    sort_keys=True))

    def get_updates(self, last_update=0) -> List[Update]:
        """
        Cerca se ci sono stati update dall'ultima volta che sono stati controllati

        :param last_update: id dell'ultimo update
        :return: la lista, eventualmente vuota, di update
        """
        updates = self.__execute("getUpdates", offset=last_update)

        return [Update.from_dict(update) for update in updates]

    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML", reply_to: int = None,
                     keyboard: Keyboard = Keyboard()) -> Message:
        """
        Manda un messaggio di testo con eventuale tastiera

        :param chat_id: a chi mandare il messaggio
        :param text: il testo da mandare
        :param parse_mode: Markdown o HTML
            Markdown *...* (grassetto) _..._ (corsivo) [nome_url](url_effettivo) [utente](tg://user?id=...)
            `...` (code) ```...``` (block)
            HTML <b>...</b> (grassetto) <i>...</i> (corsivo) <a href="url">nome_url</a>
            <a href="tg://user?id=...">utente</a> <code>...</code> <pre>...</pre>
        :param reply_to: id del messaggio
        :param keyboard: tastiera da mostrare eventualmente
        :return:
        """
        while len(text) > max_length:
            index = text.find("\n", max_length)  # se il messaggio troppo lungo errore oppure perde markup
            result = Message.from_dict(
                self.__execute("sendMessage", chat_id=chat_id, text=text[:index],
                               parse_mode=parse_mode, reply_to_message_id=reply_to))
            text = text[index:]
            reply_to = result.message_id if result.message_id else None

        return Message.from_dict(
            self.__execute("sendMessage", chat_id=chat_id, text=text,
                           parse_mode=parse_mode, reply_to_message_id=reply_to, reply_markup=keyboard.to_json()))

    def edit_message(self, chat_id: int, message_id: int, text: str, parse_mode: str = "HTML",
                     keyboard: Keyboard = Keyboard()) -> Message:
        """
        Edita un messaggio precedentemente inviato

        :param chat_id: chat dov'è presente il messaggio
        :param message_id: id del messaggio da modificare
        :param text: il nuovo testo del messaggio
        :param parse_mode: Markdown o HTML
        :param keyboard: la nuova tastiera da mostrare eventualmente
        :return:
        """
        result = Message.from_dict(self.__execute("editMessageText", chat_id=chat_id, message_id=message_id,
                                                  text=text[:max_length], parse_mode=parse_mode,
                                                  reply_markup=keyboard.to_json()))
        if not result.message_id:
            return self.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode, keyboard=keyboard)
        elif len(text) > max_length:
            return self.send_message(chat_id=chat_id, text=text[max_length:], parse_mode=parse_mode,
                                     reply_to=result.message_id)
        else:
            return result

    def forward_message(self, chat_id: int, from_chat: Chat, message: Message) -> Message:
        """
        Inoltra un messaggio

        :param chat_id: a chi inoltrare il messaggio
        :param from_chat: da dove arriva il messaggio
        :param message: il messaggio da inoltrare
        :return:
        """
        return Message.from_dict(self.__execute("forwardMessage", chat_id=chat_id, from_chat_id=from_chat.chat_id,
                                                message_id=message.message_id))
