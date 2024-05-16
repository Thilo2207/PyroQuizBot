from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton,InlineKeyboardMarkup
from pyrogram.types import ReplyKeyboardMarkup,KeyboardButton,ReplyKeyboardRemove
import random
import html
import requests
from plugins.database import insert_values
def fetch_categories():
    try:
        response = requests.get("https://opentdb.com/api_category.php")
        response.raise_for_status()  
        categories = response.json()["trivia_categories"]
        return categories
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []

def select_category_keyboard():
    global entertainment,science
    main_categories = []
    entertainment = []
    science = []
    get_categories = fetch_categories()
    all_categories = get_categories
    for category in all_categories:
        name = category["name"]
        if "Entertainment" not in name and "Science" not in name:
            main_categories.append(category)
        if "Entertainment" in name:
            entertainment.append(category)
        if "Science" in name:
            science.append(category)
    join_categories = [{'id':555,'name':'Entertainments'},{'id':777,'name':"Science"}]
    main_categories.extend(join_categories)
    
    buttons = []
    row = []
    for main in main_categories:
        button = InlineKeyboardButton(main['name'], callback_data=str(main['id']))
        row.append(button)
        if len(row) == 3:  
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    reply_markup = InlineKeyboardMarkup(buttons) 
    return reply_markup
    
@Client.on_message(filters.command('select'))
def select_categories(client,message):
     keyboard = select_category_keyboard()
     message.reply_text("Select the Category that interests you the most and let's get started!", reply_markup= keyboard)
def entertainment_keyboard():
    global entertainment
    entertainment_remove = []
    for enter in entertainment:
            remove = enter["name"].replace("Entertainment: ","")
            modified_entertainment = {
                "id":enter["id"],
                "name":remove
            }
            
            entertainment_remove.append(modified_entertainment)
               
    buttons = []
    row = []
    for e in entertainment_remove:
        entertainment_keyboard = InlineKeyboardButton(e['name'],callback_data=str(e["id"]))
        row.append(entertainment_keyboard)
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("Back to Select Category",callback_data= "333")])
    reply = InlineKeyboardMarkup(buttons)
    return reply

    
def science_keyboard():
    global science
    keyboard = []
    row =[]
    for s in science:
        science_keyboard = InlineKeyboardButton(s["name"],callback_data = str(s["id"]))
        row.append(science_keyboard)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("Back to Select Category",callback_data= "333")])
    key = InlineKeyboardMarkup(keyboard)
    return key
     
@Client.on_callback_query()
def callback(client,query):
    global quiz_bot
    category_ID = int(query.data)
    if category_ID == 555:
        enter_keyboard = entertainment_keyboard()
        query.message.edit_text("It's showtime! Pick your preferred entertainment category to begin the quiz.",reply_markup = enter_keyboard)
    elif category_ID == 777:
        sci_keyboard = science_keyboard()
        query.message.edit_text("Ready to explore the wonders of science? Choose your favorite category from the options below.",reply_markup = sci_keyboard)
    elif category_ID == 333:
        query.message.edit_text("Select the Category that interests you the most and let's get started!",reply_markup = select_category_keyboard())
    elif category_ID == 000:
        # Handle next quiz option
        select_categories(client, query.message)
    else:
        quiz_bot = Quiz(category_ID)
        query.message.reply_text("Great Choice! Type /quiz to start playing")
        
class Quiz:
    def __init__(self,category):
        self.amount = 10
        self.category = category
        self.current_question = 0
        self.Answered = False
        self.correct_answers = 0
        self.incorrect_answers = 0

    def quiz_details(self):
        url = f"https://opentdb.com/api.php?amount={self.amount}&category={self.category}"
        try:
             response = requests.get(url)
             response_js = response.json()
             if response.status_code == 200:
                 return response_js["results"]
        except requests.RequestException as e:
               print(f"Error fetching questions: {e}")
               return []
    def quiz(self,client,message):
        details = self.quiz_details()
        if details is None:
            message.reply_text("Faildes Fetching Question:Try Aagin Later")
            return
        quiz = details
        if not self.Answered:
            if self.current_question <len(quiz):
               all_details = quiz[self.current_question]
               question = html.unescape(all_details["question"])
               incorrect_answers = html.unescape(all_details["incorrect_answers"])
               self.correct_answer = html.unescape(all_details["correct_answer"])
               choices = incorrect_answers
               choices.append(self.correct_answer)
               random.shuffle(choices)
               buttons = [
                         [KeyboardButton(choice)] for choice in choices
                         ] 
               key = ReplyKeyboardMarkup(keyboard=buttons,resize_keyboard= True,selective= True,one_time_keyboard=True)
               message.reply_text(f'Question {self.current_question +1}:\n {question}',reply_markup = key)
               self.Answered = True
               
    def check_answer(self,client,message):
        try:
            chosen_answer = message.text
            if chosen_answer == self.correct_answer:
                message.reply_text("Corrrect Answer")
                self.correct_answers += 1
            else:
                message.reply_text(f"Wrong Answer.The Correct Answer is {self.correct_answer}")
                self.incorrect_answers += 1
            insert_values(self.correct_answers,self.incorrect_answers,client,message)
            self.current_question += 1
            self.Answered = False
            self.quiz(client,message)
                
        except Exception as e:
            print(f"An error occurred: {e}")

quiz_bot = None
           
@Client.on_message(filters.command("start") & filters.private)
def start(client,message):
     message.reply_text("Welcome to the GT Quiz! To get started, type /select to pick a category")


@Client.on_message(filters.command('quiz'))
def ask_question(client,message):
    global quiz_bot

    if not quiz_bot:
        quiz_bot = Quiz(None)
        
    quiz_bot.quiz(client,message)

@Client.on_message(filters.text)
def input_check(client,message):
    quiz_bot.check_answer(client,message) 


