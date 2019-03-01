import discord, requests, os, time

dis_id = ''
dis_secret = ''
dis_token = ''
permission_int = ''

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if message.content.startswith('?'):
            file_url = message.attachments[0]['url']
            print(file_url)
            x = message.author

            print('new message ', x)
            msg = await client.send_file(message.channel, 'I will delete myself now...')
            await self.downloadimage(message, str(time.time()), file_url )

            await self.send_the_file(message)
    async def downloadimage(self, message,name, url):

        response = requests.get(url)
        base = r'D:\Python\pubg\bot\needtoprocess'
        endfolder= r'D:\Python\pubg\bot\finished'


        for path in [base, endfolder]:
            try:
                os.makedirs(path)
            except FileExistsError:
                pass

        self.pathname = str(name) + '.png'

        self.processpath = os.path.join(base, self.pathname)
        self.savepath = os.path.join(endfolder, self.pathname)

        # download the actual content
        try:
            with open(self.processpath, 'wb') as fo:
                for chunk in response.iter_content(4096):
                    fo.write(chunk)

            # oh fuck what went wrong better log that bitch
        except Exception as e:
            print('oh shit there was an exception with \nuser %s \nmessage: %s \nerror: %s' % (message.author, message.content, e))
            await client.send_message(message.channel, 'uwu sowwy tere was ewwor!')

    async def remove(self):
        os.remove(self.processpath)

    async def send_the_file(self, message):
        message.send_file(message.channel, self.savepath)

        await self.remove()

if __name__ == '__main__':
        
    client = MyClient()
    client.run(dis_token)