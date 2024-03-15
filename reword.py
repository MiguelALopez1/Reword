import discord

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True

client = discord.Client(intents=intents)

# Dictionary to store question message IDs and their corresponding upvotes and downvotes
questions = {}

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$ask'):
        question = message.content[len('$ask '):]
        msg = await message.channel.send(question)
        questions[msg.id] = {'upvotes': 0, 'downvotes': 0, 'content': question}
        await msg.add_reaction('👍')
        await msg.add_reaction('👎')

    if message.content.startswith('$list'):
        sorted_questions = sorted(questions.values(), key=lambda x: x['upvotes'] - x['downvotes'], reverse=True)
        response = '\n'.join([f"{q['content']} (👍 {q['upvotes']} - 👎 {q['downvotes']})" for q in sorted_questions])
        await message.channel.send(response)

@client.event
async def on_reaction_add(reaction, user):
    if user == client.user:
        return

    if reaction.message.id in questions and str(reaction.emoji) in ['👍', '👎']:
        if str(reaction.emoji) == '👍':
            questions[reaction.message.id]['upvotes'] += 1
        else:
            questions[reaction.message.id]['downvotes'] += 1

@client.event
async def on_reaction_remove(reaction, user):
    if user == client.user:
        return

    if reaction.message.id in questions and str(reaction.emoji) in ['👍', '👎']:
        if str(reaction.emoji) == '👍':
            questions[reaction.message.id]['upvotes'] -= 1
        else:
            questions[reaction.message.id]['downvotes'] -= 1

client.run('key here lol')
