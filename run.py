from flight_path_det import  PlanePath
import model_trainer as mt
from distance_converter import scale_points
from matplotlib import pyplot as plt
from heatmap import min_town_plane_distance, town_list
import numpy as np
from matplotlib.patches import Circle

import discord, requests, os, time, torch

dis_id = ''
dis_secret = ''
dis_token = ''
permission_int = ''

class MyClient(discord.Client):
    def initial(self):
        self.model_path = mt.path
        self.model = load_model(self.model_path)

        self.total_town_data = town_list()
        self.circle_x_center, self.circle_y_center, self.circle_radius, towns =  list(zip(*self.total_town_data))
        self.towns = list(towns) + ['outskirts']

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if not message.content.startswith('?anal'):
            return False



        t1 = time.time()



        try:
            file_url = message.attachments[0]['url']
        except IndexError:
            await client.send_message(message.channel, 'no file w/ ur message')
            return False
        print('new message ', message.author, file_url)
        print(message.content)

        # finishes inc1 
        t2 = time.time()


        await self.downloadimage(message, str(time.time()), file_url )

        # get the closest towns to the plane path
        try:
            data = await get_plane_data(self.processpath)
        except Exception as e:
            print('exception get plane data', e)
            await client.send_message(message.channel, 'uwu sowwy tere was ewwowr: error on image, either wrong picture dimensions or no red path')
            return False
            
        # get the player count
        numbers = [int(s) for s in str(message.content).split() if s.isdigit()]
        if type(numbers) == list and len(numbers) > 0:
            num_players = max(numbers)
        else:
            num_players = 95


        #FINISHES INC2
        t3 = time.time()



        self.predict_data = await exec_model(self.model, data, num_players, self.towns)
        # send the return file
        base_response = ''

        for p in range(len(self.predict_data)):
            base_response += self.towns[p] + '    ' + self.predict_data[p] + '\n'
        base_response = '```' + base_response + '```'


        # finishes inc3
        t4 = time.time()



        if 'text' in message.content:
            await client.send_message(message.channel, base_response)
        elif 'all' in message.content:
            await self.plot_landings()
            await client.send_message(message.channel, base_response)
            await client.send_file(message.channel, self.savepath)

        else:
            await self.plot_landings()
            await client.send_file(message.channel, self.savepath)

        #finishes inc4
        t5 = time.time()
        inc1,inc2,inc3, inc4 = t2-t1, t3-t2, t4-t3, t5-t4

        print("%s\n%s\n%s\n%s\n" % (inc1,inc2, inc3, inc4))


# print('----')
        # remove the older file
        os.remove(self.processpath)
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
    async def plot_landings(self):
        im = plt.imread(self.processpath)
        plt.imshow(im)
        circle_data = []
        ax = plt.gca()
        ax.cla()
        ax.imshow(im)
        index = 0
        for row in self.total_town_data:
            #scale_points(width, height, point, final_unit):
            # print(row)
            x, y, r, name = row
            x, y, r = scale_points(1080, 1080, x, 'pixels'), scale_points(1080, 1080, y, 'pixels'), scale_points(1080, 1080, r, 'pixels')
            plt.text(x,y, self.predict_data[index], fontsize=10,horizontalalignment='center',verticalalignment='center', color='red',bbox=dict(facecolor='black', alpha=0.5))
            ph_circle = plt.Circle((x,y), r, color='b', fill=False)
            circle_data.append(ph_circle)
            index += 1

        for circ in circle_data:
            ax.add_artist(circ)

        plt.savefig(self.savepath, bbox_inches='tight',dpi = 300,pad_inches = 0)



def load_model(path):
    model = mt.NeuralNetwork(mt.D_in, mt.Hidden_1, mt.Hidden_2, mt.Hidden_3, mt.D_out)
    model.load_state_dict(torch.load(path))
    return model

async def get_plane_data(path):
    plane = PlanePath(path)
    plane.find_flight_path()
    print(len(plane.pixel_list))
    plane.plane_slope()

    slope, yint = plane.slope, plane.yintercept
    shortest_distance_to_town = min_town_plane_distance(slope, yint) + [0]

    return torch.Tensor(shortest_distance_to_town)

async def exec_model(model, match_input_data, num_players, towns):
    predicted_landings = model(match_input_data).view(mt.D_out, -1)

    numpy_results = predicted_landings.detach().numpy().flatten()

    player_count_list = []
    for i in range(len(numpy_results)):
        player_count = str(num_players * numpy_results[i])[:4]
        # print(towns[i], player_count)
        player_count_list.append(player_count)

    return player_count_list


client = MyClient()
print(client.__dict__)
client.initial()
client.run(dis_token)
client.close()
x = client.close()
print(x)

