from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton as IKB
from pyrogram.types import InlineKeyboardMarkup as IKM
from pyrogram.types import CallbackQuery, Message
from mp import app

database = {}

@app.on_message(filters.command('start') & filters.private)
async def startfun(_, message: Message):
    user_id = message.from_user.id
    
    if user_id not in database:
        database[user_id] = {}
        
    if 'state' not in database[user_id] or not database[user_id]['state']:
        database[user_id]['state'] = False
    
    if not database[user_id]['state']:
        keyboard = IKM([
            [IKB(text='Discord', callback_data='mode_discord')],
            [IKB(text='Instagram', callback_data='mode_instagram')],
            [IKB(text='Kick', callback_data='mode_kick')],
            [IKB(text='Minecraft', callback_data='mode_minecraft')],
            [IKB(text='Telegram', callback_data='mode_telegram')],
            [IKB(text='Tiktok', callback_data='mode_tiktok')],
            [IKB(text='Twitch', callback_data='mode_twitch')],
            [IKB(text='Twitter', callback_data='mode_twitter')],
            [IKB(text='Snapchat', callback_data='mode_snapchat')],
        ])
        
        await app.send_message(message.chat.id, 'Hello, which platform would you like to create a listing for?', reply_markup=keyboard)
        database[user_id]['state'] = True
    else:
        await message.reply_text('You already have an unprocessed request. Run /cancel to cancel your request.')

@app.on_callback_query(filters.regex(r"mode_"))
async def modecb(_, query: CallbackQuery):
    user_id = query.from_user.id
    mode = query.data.split("_")[1]

    if user_id in database and database[user_id]['state']:
        database[user_id]['mode'] = mode

        keyboard = IKM([[IKB("Cancel", callback_data="cancel")]])

        text = (
            f'Platform: {mode.capitalize()}\n\n'
            f'Please enter the username you will be selling'
        )

        await query.message.edit_text(text=text, reply_markup=keyboard)

@app.on_message(filters.text & filters.private)
async def getuser(_, message: Message):
    user_id = message.from_user.id
    
    if user_id in database and database[user_id]['state']:
        if 'mode' in database[user_id] and 'username' not in database[user_id]:
            database[user_id]['username'] = message.text

            keyboard = IKM([[IKB(text='Cancel', callback_data='cancel')]])

            text = (
                f'**Platform**: {database[user_id]["mode"].capitalize()}\n'
                f'**Username**: {database[user_id]["username"]}\n\n'
                f'Please enter the price of this listing'
            )

            await app.send_message(message.chat.id, text=text, reply_markup=keyboard)
        elif 'username' in database[user_id] and 'price' not in database[user_id]:
            try:
                database[user_id]['price'] = float(message.text)
            except ValueError:
                await message.reply_text("Please enter a valid price.")
                return

            keyboard = IKM([[IKB(text='Cancel', callback_data='cancel')]])

            text = (
                f'**Platform**: {database[user_id]["mode"].capitalize()}\n'
                f'**Username**: {database[user_id]["username"]}\n'
                f'**Price**: {database[user_id]["price"]}\n\n'
                f'Please enter any additional info for this listing (256 characters maximum)'
            )

            await app.send_message(message.chat.id, text=text, reply_markup=keyboard)
        elif 'price' in database[user_id] and 'additional' not in database[user_id]:
            database[user_id]['additional'] = message.text

            keyboard = IKM([
                [IKB(text='Process', callback_data='process')],
                [IKB(text='Cancel', callback_data='cancel')]
            ])

            text = (
                f'**Platform**: {database[user_id]["mode"].capitalize()}\n'
                f'**Username**: {database[user_id]["username"]}\n'
                f'**Price**: {database[user_id]["price"]}\n'
                f'**Additional Info**: {database[user_id]["additional"]}\n\n'
                f'Click **Process** below to send your application.\n\n'
                f'Ensure you have the `Forwarded Messages` privacy setting set to `Everybody`, otherwise your listing will automatically be rejected.'
            )

            await app.send_message(message.chat.id, text=text, reply_markup=keyboard)

@app.on_callback_query(filters.regex('process'))
async def processcb(_, query: CallbackQuery):
    user_id = query.from_user.id

    if user_id in database:
        mode = database[user_id]['mode']
        username = database[user_id]['username']
        price = database[user_id]['price']
        additional = database[user_id]['additional']

        text = (
            f"Username: {username}\n"
            f"BIN: ${price}\n"
            f"Additional Info: `{additional}`\n"
        )

        group = await app.get_chat(-1002180822552)
        async for topic in app.get_forum_topics(-1002180822552):
            if mode.lower() in topic.title.lower():
                thread_id = topic.message_thread_id
                break


        keyboard = IKM([[IKB(text='Contact Owner', user_id=user_id)]])

        message = await app.send_message(-1002180822552, text=text, message_thread_id=thread_id, reply_markup=keyboard)
        
        link = f"https://t.me/{group.username}/{message.message_thread_id}/{message.id}"
        
        keyboard = IKM([[IKB(text='View Listing', url=link)]])

        await app.send_message(user_id, "Your ad has been listed successfully!", reply_markup=keyboard)
                
        database[user_id]['state'] = False

@app.on_callback_query(filters.regex('cancel'))
async def cancelcb(_, query: CallbackQuery):
    user_id = query.from_user.id

    if user_id in database:
        database[user_id]['state'] = False
        await query.message.edit_text("Your request has been canceled.")

@app.on_message(filters.command('cancel') & filters.private)
async def cancelfun(_, message: Message):
    user_id = message.from_user.id

    if user_id in database:
        database[user_id]['state'] = False
        await message.reply_text("Your request has been canceled.")

app.run()
