from pyrogram import Client
import mysql.connector
from pyrogram.types import InlineKeyboardButton,InlineKeyboardMarkup

my = mysql.connector.connect(
    host = "localhost",
    user  = "telebot",
    password = "gt",
    auth_plugin = "mysql_native_password",
    database = "quizbot"
)
def insert_values(correct_answers, incorrect_answers,client,message):
    try:
        cursor = my.cursor()
        sql = "INSERT INTO quizmarks(correct_answer, wrong_answer) VALUES(%s, %s)"
        value = (correct_answers, incorrect_answers)
        cursor.execute(sql, value)
        my.commit()

        filter = "SELECT * FROM quizmarks WHERE id = 10"
        if filter:
          cursor.execute(filter)
          result = cursor.fetchall()
          for x in result:
             correct = x[0]
             wrong = x[1]
             message_text = f"Correct Answer:{correct}\nWrong Answer:{wrong}\nTotal Mark:{correct}/10"
             keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Next Quiz", callback_data="000")]
            ])
             message.reply_text(message_text, reply_markup = keyboard)
             delete_all_values()
        

    except Exception as e:
        print(f"Error inserting values: {e}")
        my.rollback()
    finally:
        cursor.close()

def delete_all_values():
    try:
        cursor = my.cursor()
        cursor.execute("TRUNCATE TABLE quizmarks")
        my.commit()
        print("delete all values")
    except Exception as e:
        print(f"Error resetting auto-increment: {e}")
        my.rollback()
    finally:
        cursor.close()
"""
def insert_values(correct_answers, incorrect_answers,):
    try:
        cursor = my.cursor()
        sql = "INSERT INTO quizmarks(correct_answer, wrong_answer) VALUES(%s, %s)"
        value = (correct_answers, incorrect_answers)
        cursor.execute(sql, value)
        my.commit()

        cursor = my.cursor()
        cursor.execute("SELECT * FROM quizmarks ORDER BY id DESC LIMIT 1")
        last_inserted_row = cursor.fetchone()
        print("Information associated with the last inserted row:")
        print(last_inserted_row)
        
    except Exception as e:
        print(f"Error inserting values: {e}")
        my.rollback()
    finally:
        cursor.close()

def reset_auto_increment():
    try:
        cursor = my.cursor()
        cursor.execute("TRUNCATE TABLE quizmarks")
        my.commit()
        print("Auto-increment value reset to 1.")
    except Exception as e:
        print(f"Error resetting auto-increment: {e}")
        my.rollback()
    finally:
        cursor.close()

reset_auto_increment() """