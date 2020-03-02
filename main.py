from urllib.request import urlretrieve

import requests
import telebot
import xmltodict
from flask import Flask, make_response, render_template, request
from flask_sslify import SSLify

from config import BOT_TOKEN, CHANNEL, CLIENT_ID

APP = Flask(__name__)
SSLIFY = SSLify(APP)
WIDTH = 1280
HEIGHT = 720
PATH = "full/path/to/stream_start.jpg"
BOT = telebot.TeleBot(BOT_TOKEN)
STREAMS = dict()


def get_game_title(streamer_id):
    """
        Get game title from its ID
    """
    request_url = "https://api.twitch.tv/helix/games?id={0}".format(streamer_id)
    response = requests.get(request_url, headers=CLIENT_ID)
    data_response = response.json()["data"] if response.json()["data"] else str()
    if data_response:
        return data_response[0]["name"]

    return data_response


def send_notification(response, streamer_name, title, game):
    """
        Sends notification to telegram channel
    """
    streamer_id = response["data"][0]["id"]
    if streamer_id not in STREAMS.values():
        STREAMS[streamer_name] = streamer_id
        dl_img(response["data"][0]["thumbnail_url"])
        stream_url = "twitch.tv/" + streamer_name
        photo = open(PATH, "rb")
        BOT.send_photo(
            CHANNEL,
            photo,
            caption=(
                "<b>{0}</b> начал стрим.\n\nОписание стрима: {1}\n\nИгра: {2}\n\n{3}"
            ).format(streamer_name, title, game, stream_url),
            parse_mode="HTML",
        )
        return make_response("Stream online", 200)
    else:
        BOT.send_message(
            CHANNEL,
            "{0}\n\nОписание: {1}\n\nИгра: {2}".format(streamer_name, title, game),
        )
        return make_response("Stream online", 200)


def parse_xml(xml):
    """
        Parses XML and returns youtube video title and URL
    """
    video = list()
    xml = xmltodict.parse(xml, process_namespaces=False)
    video_url = xml["feed"]["entry"]["link"]["@href"]
    video_title = xml["feed"]["entry"]["title"]
    video.append(video_title)
    video.append(video_url)
    return video


def dl_img(url):
    """
        downloads image from URL to specified path
    """
    print(url.format(width=WIDTH, height=HEIGHT))
    urlretrieve(url.format(width=WIDTH, height=HEIGHT), PATH)


def confirm_subscribe(searchword):
    """
        returns hub.challenge id for subscribe confirmation
    """
    response = make_response(searchword, 200)
    response.mimetype = "text/plain"
    return response


@APP.route("/", methods=["POST", "GET"])
def index():
    """
        twitch webhook is set on this url (https://example.com/)
        depending on request method returns response
    """
    if request.method == "POST":
        response = request.get_json()
        streamer_name = response["data"][0]["user_name"]
        if response["data"]:
            response = request.get_json()
            send_notification(
                response,
                streamer_name,
                response["data"][0]["title"],
                get_game_title(response["data"][0]["game_id"]),
            )
        else:
            if streamer_name in STREAMS:
                BOT.send_message(CHANNEL, "{0} оффлайн".format(streamer_name))
                del STREAMS[streamer_name]
                return make_response("Stream offline", 200)

            return make_response("Stream offline", 200)

    if request.args.get("hub.challenge"):
        confirm_subscribe(request.args.get("hub.challenge"))

    return render_template("index.html")


@APP.route("/youtube", methods=["POST", "GET"])
def youtube_view():
    """
        view handles POST method and sends link to new video on youtube
    """
    if request.method == "POST":
        response = request.data
        video = parse_xml(response)
        text = "{0}\n\n{1}".format(video[0], video[1])
        BOT.send_message(CHANNEL, text)
        return make_response(video[0], 200)

    if request.args.get("hub.challenge"):
        confirm_subscribe(request.args.get("hub.challenge"))

    return "<h1>Hello Youtube</h1>"


if __name__ == "__main__":
    APP.run()
