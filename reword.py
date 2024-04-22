import discord

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True

client = discord.Client(intents=intents)

questions = {}

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$help') or message.content.startswith('$h'):
        help_message = (
            "# Bot Command List:\n"
            "**$ask [question]**: Ask a question. The bot will post your question for others to see and vote on.\n"
            "**$list**: Lists all the questions sorted by their net votes (upvotes minus downvotes).\n"
            "**$answer [question ID] [answer]**: Provide an answer to a specific question using its ID from the **$list** command.\n"
            "**$answers [question ID]**: Lists all answers for a specific question, sorted by their net votes.\n"
            "React with 👍 or 👎 to vote on questions and answers."
        )
        await message.channel.send(help_message)
        return

    if message.content.startswith('$ask'):
        question = message.content[len('$ask '):]
        msg = await message.channel.send(f"**{message.author} asked:** *{question}*")
        questions[msg.id] = {
            'upvotes': 0,
            'downvotes': 0,
            'content': question,
            'author': message.author.display_name,
            'answers': []
        }
        await msg.add_reaction('👍')
        await msg.add_reaction('👎')

    if message.content.startswith('$list'):
        sorted_questions = sorted(questions.values(), key=lambda x: x['upvotes'] - x['downvotes'], reverse=True)
        response = '\n'.join([f"**{idx + 1}: {q['author']} asked** *\"{q['content']}\"* (👍 {q['upvotes']} - 👎 {q['downvotes']})" for idx, q in enumerate(sorted_questions)])
        await message.channel.send(response)

    if message.content.startswith('$answer '):
        parts = message.content.split(' ', 2)
        if len(parts) < 3:
            return await message.channel.send("Format should be: answer [question ID] [answer].")

        question_id, answer_text = parts[1], parts[2]
        try:
            question_id = int(question_id) - 1
            sorted_questions = sorted(questions.items(), key=lambda x: x[1]['upvotes'] - x[1]['downvotes'], reverse=True)
            question_key, question = sorted_questions[question_id]

            author_mention = question['author']
            upvoters_mentions = ' '.join([f"<@{id}>" for id in question.get('upvote_users', [])])
            response = f"**{author_mention} asked:** *\"{question['content']}\"*\n**An answer was provided:** *{answer_text}* {upvoters_mentions}"
            msg = await message.channel.send(response)
            
            # Store the answer with its message ID
            answer = {
                'text': answer_text,
                'upvotes': 0,
                'downvotes': 0,
                'author': message.author.display_name,
                'message_id': msg.id
            }
            question['answers'].append(answer)

            # Add reactions to the answer for voting
            await msg.add_reaction('👍')
            await msg.add_reaction('👎')
        except (IndexError, ValueError):
            await message.channel.send("Invalid question ID.")

    if message.content.startswith('$answers '):
        _, question_id = message.content.split(' ', 1)
        try:
            question_id = int(question_id) - 1
            sorted_questions = sorted(questions.items(), key=lambda x: x[1]['upvotes'] - x[1]['downvotes'], reverse=True)
            question_key, question = sorted_questions[question_id]

            if 'answers' in question:
                sorted_answers = sorted(question['answers'], key=lambda x: x['upvotes'] - x['downvotes'], reverse=True)
                response = f"**Question:** *{question['content']}*\n"
                response += "\n".join([f"**Answer:** *{a['text']}* (👍 {a['upvotes']} - 👎 {a['downvotes']})" for a in sorted_answers])
            else:
                response = "No answers available for this question."

            await message.channel.send(response)
        except (IndexError, ValueError):
            await message.channel.send("Invalid question ID.")

@client.event
async def on_reaction_add(reaction, user):
    if user == client.user:
        return

    # Update upvotes/downvotes for questions
    if reaction.message.id in questions:
        question = questions[reaction.message.id]
        if str(reaction.emoji) == '👍':
            question['upvotes'] += 1
        elif str(reaction.emoji) == '👎':
            question['downvotes'] += 1

    # Update upvotes/downvotes for answers
    for question in questions.values():
        for answer in question.get('answers', []):
            if reaction.message.id == answer.get('message_id'):
                if str(reaction.emoji) == '👍':
                    answer['upvotes'] += 1
                elif str(reaction.emoji) == '👎':
                    answer['downvotes'] += 1

@client.event
async def on_reaction_remove(reaction, user):
    if user == client.user:
        return

    # Handle upvote/downvote removal for questions
    if reaction.message.id in questions:
        question = questions[reaction.message.id]
        if str(reaction.emoji) == '👍':
            question['upvotes'] -= 1
        elif str(reaction.emoji) == '👎':
            question['downvotes'] -= 1

    # Handle upvote/downvote removal for answers
    for question in questions.values():
        for answer in question.get('answers', []):
            if reaction.message.id == answer.get('message_id'):
                if str(reaction.emoji) == '👍':
                    answer['upvotes'] -= 1
                elif str(reaction.emoji) == '👎':
                    answer['downvotes'] -= 1

client.run('key here')
