import os
import discord
from discord.ext import commands
from keep_alive import keep_alive
import requests
import re
import asyncio
import aiohttp
import io
import random

intents = discord.Intents.all()
client = commands.Bot(command_prefix='?', intents=intents)


@client.event
async def on_ready():
  print("I'm in")
  print(client.user)


@client.command(name='8ball',
                description='Answers a yes/no question',
                aliases=['eight_ball', 'eightball'],
                pass_context=True)
async def eightBall(ctx):
  possibleResponses = [
      'Nope',
      'Probably not',
      "Mmm, I don't know",
      'Yeah, probably',
      'Hell yeah',
  ]
  await ctx.send(
      random.choice(possibleResponses) + ", " + ctx.message.author.mention)


@client.command(name='square',
                description='Returns the squared number of the user')
async def square(ctx, num):
  await ctx.send(str((int(num)**2)))


@client.command()
async def copy(ctx):
  if ctx.author.guild_permissions.manage_messages:
    messages = []
    async for message in ctx.channel.history(limit=250):
      messages.append(message)

    # Create a list of message content and attachments
    copied_messages = []
    for message in messages:
      if not message.author.bot:
        content = message.content
        attachments = [attachment.url for attachment in message.attachments]
        copied_messages.append((content, attachments))

    # Store the copied messages in a variable accessible in the bot's context
    ctx.bot.copied_messages = copied_messages

    await ctx.send("Messages and attachments copied successfully!")
  else:
    await ctx.send(
        "You don't have the necessary permissions to use this command.")


@client.command()
async def paste(ctx):
  if hasattr(ctx.bot, 'copied_messages'):
    copied_messages = ctx.bot.copied_messages

    for content, attachments in copied_messages:
      # Send the message content
      await ctx.send(content)

      # Send the attachments
      for attachment_url in attachments:
        async with aiohttp.ClientSession() as session:
          async with session.get(attachment_url) as resp:
            if resp.status == 200:
              data = io.BytesIO(await resp.read())
              file = discord.File(data, filename='image.png')
              await ctx.send(file=file)
  else:
    await ctx.send(
        "No messages and attachments have been copied yet. Use the `copy` command first."
    )


@client.command(
    name='purge',
    description=
    'Delete all messages in a channel up to the last bot message. Useful for cleaning up role-playing channels.',
    aliases=['clear'
             ])  # Replace 'purgeAliases' with the actual list of aliases
async def purge(ctx):
  if ctx.author.guild_permissions.manage_messages:
    await ctx.message.delete()

    messages = []
    async for message in ctx.channel.history(limit=250):
      messages.append(message)
    print("Number of fetched messages:", len(messages))

    n = 0
    for message in messages:
      if message.author.bot or message.attachments:
        break  # Stop when a bot/image message is encountered

      if message.content.startswith("```") and message.content.endswith("```"):
        break  # Stop when a message starts and ends with triple backticks

      n += 1

    deleted_messages = await ctx.channel.purge(limit=n)
    response = f"Deleted {len(deleted_messages)} message(s) from users up to the last bot/image message."
    await ctx.send(response, delete_after=2)
  else:
    await ctx.send(
        "You don't have the necessary permissions to use this command.")


@client.command()
async def translate(ctx, *args):
  await ctx.send("Processing translation request...")
  deturl = "https://api.apptek.com/api/v2/language_id/"
  query = ' '.join(args)
  print(args)
  unt_text = re.sub("[!,*)@#%(&$_?.^']", '', query)
  url = "https://api.apptek.com/api/v2/language_id"

  payload = query.encode()
  headers = {
      "Accept": "application/json",
      "x-token": "a5f5bdaa-f8d1-4353-b721-e2fc2ed9602d",
      "Content-Type": "text/plain"
  }

  detresponse = requests.post(deturl, data=payload, headers=headers)
  print(detresponse.text)
  detdict = detresponse.json()
  print(detresponse.headers)
  print(detresponse.json())
  print(detdict.get('request_id'))

  resurl = "https://api.apptek.com/api/v2/language_id/" + detdict.get(
      'request_id')
  print(resurl)
  headers = {
      "Accept": "text/plain",
      "x-token": "a5f5bdaa-f8d1-4353-b721-e2fc2ed9602d"
  }
  response = requests.get(resurl, headers=headers)
  data = response.text

  def refresh_data():
    response = requests.get(resurl, headers=headers)
    data = response.headers['x-status']
    return data

  while data != 'Completed':
    print(data)
    data = refresh_data()
    await asyncio.sleep(1)
  response = requests.get(resurl, headers=headers)
  print(response.text)
  raw_lang = str(response.text)
  lang = raw_lang[:2]
  print(lang)
  url = "https://api.apptek.com/api/v2/translate/" + lang + "-en"
  encoded_text = unt_text.encode()

  headers = {
      "Accept": "application/json",
      "Content-Type": "text/plain",
      "x-token": "a5f5bdaa-f8d1-4353-b721-e2fc2ed9602d",
      "priority": "50"
  }

  presponse = requests.post(url, data=encoded_text, headers=headers)
  print(presponse.text)
  predict = presponse.json()
  print(presponse.headers)
  print(presponse.json())
  print(predict.get('request_id'))

  resurl = "https://api.apptek.com/api/v2/translate/" + predict.get(
      'request_id')
  print(resurl)
  headers = {
      "Accept": "text/plain",
      "x-token": "a5f5bdaa-f8d1-4353-b721-e2fc2ed9602d"
  }
  finalres = requests.get(resurl, headers=headers)
  data = finalres.text

  def refresh_data():
    finalres = requests.get(resurl, headers=headers)
    data = finalres.headers['x-status']
    return data

  while data != 'Completed':
    print(data)
    data = refresh_data()
    await asyncio.sleep(1)
  finalres = requests.get(resurl, headers=headers)
  print(finalres.text)
  await ctx.send(finalres.text)


keep_alive()
my_secret = os.environ['DISCORD_BOT_SECRET']
client.run(my_secret)
