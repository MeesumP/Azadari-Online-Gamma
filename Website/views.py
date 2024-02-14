from flask import render_template, Blueprint, redirect, request
from .models import Lyric, toAdd
from . import db

from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField, StringField, TextAreaField, SelectMultipleField, widgets, SelectField, PasswordField
from wtforms.validators import InputRequired

from werkzeug.security import generate_password_hash, check_password_hash

from urllib.parse import unquote

from .tags import tags

from yt_iframe import yt

import string
import random

#needed functions imported from elsewhere

def update_youtube_src(input_string, parameter):
    # Find the index of the src attribute
    src_index = input_string.find('src="')

    # Check if the src attribute is present
    if src_index == -1:
        raise ValueError("Input string does not contain a 'src' attribute.")

    # Find the end of the src attribute value
    src_value_start = src_index + 5  # Length of 'src="'
    src_value_end = input_string.find('"', src_value_start)

    # Extract the original src value
    original_src = input_string[src_value_start:src_value_end]

    # Append the parameter to the src value
    new_src = original_src + "?start=" + parameter

    # Construct the modified string
    modified_string = input_string[:src_value_start] + new_src + input_string[src_value_end:]

    return modified_string

def time_to_seconds(time_str):
    time_parts = list(map(int, time_str.split(':')))
    
    if len(time_parts) == 2:  # Format: '7:41'
        seconds = time_parts[0] * 60 + time_parts[1]
    elif len(time_parts) == 3:  # Format: '5:41:36'
        seconds = time_parts[0] * 3600 + time_parts[1] * 60 + time_parts[2]
    else:
        raise ValueError("Invalid time format. Use either 'MM:SS' or 'HH:MM:SS'")
    
    return str(seconds)

def generateRotatingKey():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def truncate_string(input_string, target_character):
    index = input_string.find(target_character)
    if index != -1:
        return input_string[:index + 1]
    else:
        return input_string

def decode_and_parse(input_string):
    try:
        # Decoding the URL-encoded string
        decoded_string = unquote(input_string)
        
        # Removing leading and trailing whitespaces, and splitting the string into a list
        result_list = [item.strip() for item in decoded_string.strip('[]').split(',')]
        
        params = []
        for param in result_list:
            params.append(param.replace("'", ""))
        return params
    except Exception as e:
        print(f"Error decoding and parsing: {e}")
        return None
    
def alphabetize(lyrics):
    return sorted(lyrics, key=lambda x: x.title)

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()
  

views = Blueprint('views', __name__)
type = Blueprint('type', __name__)
lyric = Blueprint("lyrics", __name__)
auth = Blueprint('auth', __name__)

#Set global variables outside of request context
global rotatingKey
rotatingKey = generateRotatingKey()

#Home page, maintenance pages
@views.route('/')
def home_page():
    return redirect('/type/search')

@views.route('/admin/<thing>', methods=["POST", "GET"])
def admin_page(thing):

    class PasswordForm(FlaskForm):
        password = PasswordField(u'Password:', render_kw={'class':"textbox-format"})
        submit = SubmitField("Submit", render_kw={'class': 'submit_button'})

    form = PasswordForm()

    if form.is_submitted():
        result = request.form
        password = result.get('password')

        if password == "BaadeQatleShah786!":
            passwordVerified = True
            return render_template('admin.html', URLify=URLify, lyrics=alphabetize(Lyric.query.all()), passwordVerified=passwordVerified, form=form)
        else:
            passwordVerified = False
            return render_template('admin.html', URLify=URLify, lyrics=alphabetize(Lyric.query.all()), passwordVerified=passwordVerified, form=form)
    passwordVerified = False
    if thing == rotatingKey:
        passwordVerified = True
    return render_template('admin.html', URLify=URLify, lyrics=alphabetize(Lyric.query.all()), passwordVerified=passwordVerified, form=form)

@views.route('/to-add', methods=["POST", "GET"])
def toAdd_page():
    if len(toAdd.query.all()) == 0:
        db.session.add(toAdd(words=""))
        db.session.commit()
    
    formBool = True
    toAddList = toAdd.query.all()[0].words
    class toAddForm(FlaskForm):
        toAddQ = TextAreaField(u'Lyrics To Add: ', render_kw={'class': 'textbox-format'}, validators=[InputRequired()], default=toAddList.replace('<br>', '\n'))    
        submit = SubmitField("Submit", render_kw={'class': 'submit_button'})

    form = toAddForm()

    if form.is_submitted():
        formBool = False
        result = request.form
        toAddW = result.get('toAddQ')
        toAddW = toAddW.replace('\n', '<br>')

        db.session.delete(toAdd.query.all()[0])
        db.session.commit()
        db.session.add(toAdd(words=toAddW))
        db.session.commit()

        return render_template('toadd.html', toAdd = toAdd.query.all()[0].words, form=form, formBool=formBool)

    return render_template('toadd.html', toAdd = toAdd.query.all()[0].words, form=form, formBool=formBool)

#Pages for each kind of lyric

@type.route('/search', methods=["POST", "GET"])
def search_page():
    global rotatingKey
    rotatingKey = generateRotatingKey()
    lyrics=Lyric.query.all()
    lyrics = alphabetize(lyrics)
    class SearchForm(FlaskForm):
        searchTerm = StringField(u'Search Term: ', validators=[InputRequired()], render_kw={'class': 'textbox-format stringfield-format', 'placeholder': 'Search Titles'})
        submit = SubmitField("Submit", render_kw={'class': 'submit_button'})
    
    form = SearchForm()

    if form.is_submitted():
        result = request.form
        searchTerm = result.get('searchTerm')

        matchingLyrics = Lyric.query.filter(Lyric.title.contains(searchTerm))
        return render_template('home.html', type=f"Search: {searchTerm}", URLify=URLify, lyrics=matchingLyrics)
    return render_template('search.html', lyrics=lyrics, URLify=URLify, form=form)

@type.route('/nohay')
def noha_page():
    lyrics=Lyric.query.filter(Lyric.type.contains("Noha"))
    lyrics = alphabetize(lyrics)
    return render_template('home.html', type="Nohay", lyrics=lyrics, URLify=URLify)

@type.route('/soz')
def soz_page():
    lyrics=Lyric.query.filter(Lyric.type.contains("Soz"))
    lyrics = alphabetize(lyrics)
    return render_template('home.html', type="Soz", lyrics=lyrics, URLify=URLify)

@type.route('/manqabat')
def manqabat_page():
    lyrics=Lyric.query.filter(Lyric.type.contains("Manqabat"))
    lyrics = alphabetize(lyrics)
    return render_template('home.html', type="Manqabat", lyrics=lyrics, URLify=URLify)

@type.route('/filter', methods=['GET', 'POST'])
def filter_page():
    class FilterForm(FlaskForm):
        typeFilter = SelectField(u'Lyric Type: ', choices=['Type', 'Noha', 'Soz', 'Manqabat'], validators=[InputRequired()], render_kw={'class': 'list-items'})
        topicsFilter = SelectField(u'Topic: ', choices=['Topics']+tags, render_kw={'class': 'list-items'}, validators=[InputRequired()])
        handsFilter = SelectField(u'Hands: ', choices=['Hands', '1', '2'], render_kw={'class': 'list-items'}, validators=[InputRequired()])
        paceFilter = SelectField(u'Pace: ', choices=['Pace', 'Fast', 'Slow', 'Build'], render_kw={'class': 'list-items'}, validators=[InputRequired()])
        submit = SubmitField("Submit", render_kw={'class': 'submit_button'}, validators=[InputRequired()])

    form=FilterForm()

    if form.is_submitted():
        result = request.form
        type = result.get('typeFilter')
        topic = result.get('topicsFilter')
        hand = result.get('handsFilter')
        pace = result.get('paceFilter')

        filterList = [type, topic, hand, pace]

        encryptedFilterList = filterList

        return redirect(f'/type/filter/{encryptedFilterList}')

    return render_template('filterlyrics.html', lyrics=alphabetize(Lyric.query.all()), URLify=URLify, form=form)

@type.route('/filter/<encryptedMessage>', methods=["POST", "GET"])
def filterLyrics_page(encryptedMessage):
    params = decode_and_parse(encryptedMessage)
    type = params[0]
    topic = params[1]
    hands = params[2]
    pace = params[3]

    if type == 'Type':
        type = ''
    if topic == 'Topics':
        topic = ''
    if hands == 'Hands':
        hands = ''
    if pace == 'Pace':
        pace = ''

    lyrics = Lyric.query.filter(Lyric.type.contains(type), Lyric.topics.contains(topic), Lyric.hands.contains(hands), Lyric.pace.contains(pace))
    lyrics = alphabetize(lyrics)

    return render_template('home.html', type="Filtered Lyrics", lyrics=lyrics, URLify=URLify)

#Specific lyric pages

def URLify(text):
    return str(text).replace(" ", "-")

def textify(URL):
    return str(URL).replace("-", " ")

@lyric.route('/<kalam>/<platform>')
def lyric_page(kalam, platform):
    kalam = textify(kalam)
    thisLyric = Lyric.query.filter_by(title=kalam).first()
    if not thisLyric.link == None and not thisLyric.link == '':
        if platform == 'desktop':
            iframeCode = yt.video(thisLyric.link, width='50%')
        elif platform == 'mobile':
            iframeCode = yt.video(thisLyric.link, width='100%')
        if not thisLyric.linkTime == '':
            iframeCode = update_youtube_src(iframeCode, time_to_seconds(thisLyric.linkTime))
    else:
        iframeCode = ""
    return render_template('lyric.html', lyric=thisLyric, URLify=URLify, iframeCode=iframeCode)

@lyric.route('/add', methods=['GET', 'POST'])
def lyricAdd_page():
    class InputLyricForm(FlaskForm):
        title = StringField(u'Title: ', render_kw={'class': 'textbox-format stringfield-format'}, validators=[InputRequired()])
        type = MultiCheckboxField(u'Type: ', choices=['Noha', 'Soz', 'Manqabat'], render_kw={'class': 'multiselect_items'})
        link = StringField(u'YouTube Link (Optional): ', render_kw={'class': 'textbox-format stringfield-format'})
        linkTime = StringField(u'Time of Recitation During YouTube Video (Optional):', render_kw={'class': 'textbox-format stringfield-format'})
        pace = RadioField(u'Pace (Optional): ', choices=['Fast', 'Slow', 'Build'], render_kw={'class': 'list_items'})
        hands = MultiCheckboxField(u'Hands (Optional): ', choices=["1", "2"], render_kw={'class': "multiselect_items"})
        topics = MultiCheckboxField(u'Topics/Tags: ', choices=tags, render_kw={'class': 'multiselect_items'})
        words = TextAreaField(u'Lyrics: ', render_kw={'class': 'textbox-format'}, validators=[InputRequired()])
        submit = SubmitField("Submit", render_kw={'class': 'submit_button'})

    form = InputLyricForm()

    if form.is_submitted():
        result = request.form
        title = result.get('title')
        type = result.getlist('type')
        link = result.get('link')
        linkTime = result.get('linkTime')
        pace = result.get('pace')
        hands = result.getlist('hands')
        topics = result.getlist('topics')
        words = result.get('words')

        words = words.replace('\n', '<br>')
        words = words.replace('en-', '<small>')
        words = words.replace(';', '</small>')

        if type == 'Soz' or type == 'Manqabat':
            pace = ''
            hands = []

        if 'youtu.be' in link and not '=' in link:
            identifier = link.replace('https://youtu.be/', '')
            link = "https://www.youtube.com/watch?v=" + identifier
        #if its copied from the video and with a time
        elif 'youtu.be' in link and '=' in link:
            identifier = link.replace('https://youtu.be/', '')
            identifier = truncate_string(identifier, '=')
            identifier = identifier.replace(identifier[-1], '')
            identifier = identifier.replace(identifier[-1], '')
            identifier = identifier.replace(identifier[-1], '')
            link = "https://www.youtube.com/watch?v=" + identifier

        add = Lyric(title=title.title(), type=type, link=link, linkTime=linkTime, pace=pace, hands=hands, topics=topics, words=words)
        db.session.add(add)
        db.session.commit()
        return redirect(f'/lyrics/{URLify(Lyric.query.order_by(Lyric.id.desc()).first().title)}')

    return render_template('addLyric.html', form=form)

@lyric.route('/delete/<kalam>')
def deleteLyric(kalam):
    kalam = textify(kalam)
    lyricToDelete = Lyric.query.filter_by(title=kalam).first()
    db.session.delete(lyricToDelete)
    db.session.commit()
    if '/admin' in request.referrer:
        return redirect(f'/admin/{rotatingKey}')
    return redirect('/')

@lyric.route('/edit/<kalam>', methods=["POST", "GET"])
def editLyric_page(kalam):
    kalam = textify(kalam)
    kalamObject = Lyric.query.filter_by(title=kalam).first()

    theseWords = kalamObject.words.replace('<br>', '\n')

    class InputLyricForm(FlaskForm):
        title = StringField(u'Title: ', render_kw={'class': 'textbox-format stringfield-format'}, validators=[InputRequired()], default=kalamObject.title)
        type = MultiCheckboxField(u'Type: ', choices=['Noha', 'Soz', 'Manqabat'], render_kw={'class': 'multiselect_items'}, default=kalamObject.type)
        link = StringField(u'YouTube Link (Optional):', render_kw={'class': 'textbox-format stringfield-format'}, default=kalamObject.link)
        linkTime = StringField(u'Time of Recitation During YouTube Video (Optional):', render_kw={'class': 'textbox-format stringfield-format'}, default=kalamObject.linkTime)
        pace = RadioField(u'Pace (Optional): ', choices=['Fast', 'Slow', 'Build'], render_kw={'class': 'list_items'}, default=kalamObject.pace)
        hands = MultiCheckboxField(u'Hands (Optional): ', choices=["1", "2"], render_kw={'class': "multiselect_items"}, default=kalamObject.hands)
        topics = MultiCheckboxField(u'Topics/Tags: ', choices=tags, render_kw={'class': 'multiselect_items'}, default=kalamObject.topics)
        words = TextAreaField(u'Lyrics: ', render_kw={'class': 'textbox-format'}, validators=[InputRequired()], default=theseWords)
        submit = SubmitField("Submit", render_kw={'class': 'submit_button'})

    form = InputLyricForm()

    if form.is_submitted():
        db.session.delete(kalamObject)
        db.session.commit()

        result = request.form
        title = result.get('title')
        type = result.getlist('type')
        link = result.get('link')
        linkTime = result.get('linkTime')
        pace = result.get('pace')
        hands = result.getlist('hands')
        topics = result.getlist('topics')
        words = result.get('words')

        words = words.replace('\n', '<br>')
        words = words.replace('en-', '<small>')
        words = words.replace(';', '</small>')

        if type == 'Soz' or type == 'Manqabat':
            pace = ''
            hands = []

        if 'youtu.be' in link and not '=' in link:
            identifier = link.replace('https://youtu.be/', '')
            link = "https://www.youtube.com/watch?v=" + identifier
        #if its copied from the video and with a time
        elif 'youtu.be' in link and '=' in link:
            identifier = link.replace('https://youtu.be/', '')
            identifier = truncate_string(identifier, '=')
            identifier = identifier.replace(identifier[-1], '')
            identifier = identifier.replace(identifier[-1], '')
            identifier = identifier.replace(identifier[-1], '')
            link = "https://www.youtube.com/watch?v=" + identifier

        add = Lyric(title=title.title(), type=type, link=link, linkTime=linkTime, pace=pace, hands=hands, topics=topics, words=words)
        db.session.add(add)
        db.session.commit()

        return redirect(f'/lyrics/{URLify(Lyric.query.order_by(Lyric.id.desc()).first().title)}')

    return render_template('addLyric.html', form=form)