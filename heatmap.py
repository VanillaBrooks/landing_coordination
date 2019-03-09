from pubg_python import PUBG, Shard, Telemetry
import time, pprint, json
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from multiprocessing import Pool
import pymysql
import math

api = PUBG(apikey, Shard.PC_NA)


class PlayerPosition():
    def __init__(self, ftime, position):
        # the final time this persons position is recorded
        self.final_time = ftime
        # the final position that the person was recorded in
        self.position = position
        self.location = False
    def updateposition(self, newposition):
        self.position = newposition
    def town_location(self):
        if self.location == False:
            self.towns = town_list()
            self.location = self.distance_formula()

        return self.location
    def distance_formula(self):
        for row in self.towns:
            d = math.sqrt(((self.position[0]-row[0])**2) + ((self.position[1]-row[1])**2))
            if d < row[2]:
                return row[3]
        return 'outskirts'
def town_list():
    towns = [[ 81600.0, 167076.0, 12240.0, 'camp_alpha'], [132192.0, 116484.0, 12852.0, 'ha_tinh'],
             [133620.0, 94044.0, 5508.0, 'ha_tinh_docks'], [123012.0, 259896.0, 13056.0, 'ruins'],
          [91392.0, 256224.0, 11628.0, 'ruins_docks'], [86700.0, 291312.0, 23460.0, 'tambang'],
          [115872.0, 335784.0, 12036.0, 'na_khard'], [148512.0, 360060.0, 10404.0, 'sahmee'],
          [177480.0, 378624.0, 9996.0, 'sahmee_docs'], [238680.0, 378420.0, 11628.0, 'ban_tai'],
          [238272.0, 345576.0, 9384.0, 'camp_charlie'], [190944.0, 273768.0, 12852.0, 'pai_nan'],
          [196860.0, 193188.0, 17952.0, 'boot_camp'], [222360.0, 98736.0, 10812.0, 'tat_mek'],
          [234192.0, 72828.0, 11832.0, 'khao'], [252756.0, 139128.0, 16116.0, 'paradise'],
          [313344.0, 82416.0, 24684.0, 'mong_nia'], [346800.0, 156672.0, 13872.0, 'camp_bravo'],
          [352716.0, 226440.0, 11628.0, 'lakawi'], [270912.0, 252960.0, 34272.0, 'quarry'],
          [346188.0, 284172.0, 15096.0, 'kampong'], [333540.0, 350676.0, 9996.0, 'docks'],
          [266220.0, 308448.0, 18972.0, 'cave'], [324564.0, 187884.0, 8568.0, 'bravo_warehouse']]
    return towns

def allusernames(roster):
    totalusers = []

    for i in range(105):
        try:
            team_roster = roster[i]
            for person in team_roster.participants:
                totalusers.append(person.name)
        except IndexError:
            return totalusers


def matchdata(match, verbose=False):
    all_users = allusernames(match.rosters)
    if verbose:
        mapname = str(singularmatchdata.map_name)[:-5].lower()
        total_duration = singularmatchdata.duration
        minutes, seconds = divmod(total_duration, 60)
        print('map name: %s ' % (mapname))
        print  ('game mode: ', match.game_mode)
        print ('min:%s\nsec:%s' %(minutes, seconds))
        print ('roster:')
        all_users = allusernames(match.rosters)
        print('total users len', len(all_users))
        print(all_users)

    return all_users

def showdata(match):
    try:
        maxlandingtime  = 120
        if match.game_mode != 'squad' and match.game_mode != 'squad-fpp':
            return False
        elif str(match.map_name)[:-5].lower() != 'savage':
            return False

        asset = match.assets[0]
        telemetry = api.telemetry(asset.url)

        started_pos_events = [i for i in telemetry.events_from_type('LogPlayerPosition') if i.elapsed_time > 0]

        lastposition = {}
        planepath = []

        for event in started_pos_events:
            character = event.character
            location = character.location
            x, y, z = location.x, location.y, location.z
            if event.elapsed_time < 15 and event.elapsed_time>0:
                planepath.append([x,y])
            if character.name not in lastposition.keys():
                lastposition[character.name] = PlayerPosition(event.elapsed_time, [x,y])
            elif event.elapsed_time < maxlandingtime:
                lastposition[character.name].updateposition([x,y])

        list_of_town_drops = [obj.town_location() for obj in lastposition.values()]

        return match.id, list_of_town_drops, planepath,
    except Exception as e:
        print('there was an exception in showdata ', e)
        time.sleep(60)
        return showdata(match)

def slice(ids, start, stop):
    try:
        matches = []
        c = 0
        for id in ids[start:stop]:
            c+=1
            matches.append(api.matches().get(id))
        return matches
    except Exception as e:
        print('there was an exception in Slice ', e)
        time.sleep(60)
        return slice(ids, start, stop)

# called after slice, this function will call showdata to get statistics from each map
def process_helper(matches):
    with Pool(3) as p:
        storage_plane = p.map(showdata, (matches))

    plane, storage, ids = [], [], []
    for row in storage_plane:
        if row:
            ids.append(row[0])
            storage.append(row[1])
            plane.append(row[2])

    # returns data to 'add_stacked_layers
    return [ids, storage, plane]

def utfcon():
    conn = pymysql.connect(host='localhost', port=3306, user='brooks', password='pass', database='pubg4')
    cursor = conn.cursor()
    return conn, cursor

def add_stacked_layers(matchid_positions_and_plane):
    conn, cursor = utfcon()
    matchids, stacks, plane_path = matchid_positions_and_plane
    # print('stacked layers count of inputs', len(matchids))

    x_town_cord, y_town_cord, town_rad, town_name = list(zip(*town_list()))

    for i in range(len(stacks)):
        print('i in addstacked layers is %s' % (i))
        match_id, towns_landed_at = matchids[i], stacks[i]

        countlist = [towns_landed_at.count(town) for town in town_name]
        countlist.append(towns_landed_at.count('outskirts'))

        tcount = 0
        for k in countlist:
            tcount +=k
        if tcount > 100:
            print('there is a red flag in the match id %s because it has a count of %s' % (match_id[i],tcount))
        gamesql = 'INSERT INTO game (`match_id`, `player_count`) VALUES (%s, %s)'
        idfindersql = 'SELECT id FROM game where match_id = %s'
        dist_sql =  'INSERT INTO distances (`id`, `camp_alpha`, `ha_tinh`, `ha_tinh_docks`,`ruins`, `ruins_docks`, `tambang`, `na_khard`, `sahmee`, `sahmee_docs`, `ban_tai`, `camp_charlie`, `pai_nan`, `boot_camp` ,`tat_mek`,`khao`, `paradise`, `mong_nia`, `camp_bravo`, `lakawi`, `quarry`, `kampong`, `docks`, `cave`, `bravo_warehouse`, `outskirts`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        town_sql=   'INSERT INTO dropcount (`id`, `camp_alpha`, `ha_tinh`, `ha_tinh_docks`,`ruins`, `ruins_docks`, `tambang`, `na_khard`, `sahmee`, `sahmee_docs`, `ban_tai`, `camp_charlie`, `pai_nan`, `boot_camp` ,`tat_mek`,`khao`, `paradise`, `mong_nia`, `camp_bravo`, `lakawi`, `quarry`, `kampong`, `docks`, `cave`, `bravo_warehouse`, `outskirts`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'


        planeslope, plane_yint = plane_slope_calc(plane_path[i][0],plane_path[i][-1])
        distances_from_towns = min_town_plane_distance(planeslope,plane_yint) + [0]
        try:
            cursor.execute(gamesql, (match_id, tcount))
        except pymysql.err.IntegrityError:
            continue
        conn.commit()
        cursor.execute(idfindersql, match_id)
        sqlid = list(cursor.fetchall()[0])

        distanceslist = sqlid + distances_from_towns
        countlist     = sqlid + countlist
        distanceslist = tuple(distanceslist)

        cursor.execute(dist_sql, distanceslist)
        cursor.execute(town_sql, countlist)
        conn.commit()

def min_town_plane_distance(slope, yint):
    towns = town_list()

    slope = -1 * slope
    yint = -1 * yint

    distances = []
    for row in towns:
        x = row[0]
        y = row[1]

        dis = abs((slope*x) + (1*y) + yint) / math.sqrt(((slope**2) + (1)))
        distances.append(dis)
    # print('in min town distance we are returning' , distances)
    return distances


def plane_slope_calc(startpoint, endpoint):         # note that the width and height of the image is hard coded here
    x1,y1 = startpoint
    x2,y2 = endpoint

    slope = ((y1-y2)/(x1-x2))
    yintercept = (slope *(-1*x1)) + y1

    return [slope,yintercept]

if __name__ == '__main__':
    conn = pymysql.connect(host='localhost', port=3306, user='brooks', password='pass', database='pubg')
    cursor = conn.cursor()

    sql = 'SELECT match_id from game'
    cursor.execute(sql)
    base_id_list = [i[0] for i in cursor.fetchall()]

    conn = pymysql.connect(host='localhost', port=3306, user='brooks', password='pass', database='pubg2')
    cursor = conn.cursor()

    sql = 'SELECT match_id from game'
    cursor.execute(sql)
    extra_base_id_list = [i[0] for i in cursor.fetchall()]

    older_ids = base_id_list + extra_base_id_list
    older_ids = list(set(older_ids))
    print(older_ids)
    while True:
        sample = api.samples().get()

        matchidlist = [match.id for match in sample.matches]
        matchidlist = older_ids + matchidlist

        conn, cursor = utfcon()
        cursor.execute('SELECT match_id from game')
        previous_entries = [i[0] for i in cursor.fetchall()]

        matchidlist = [i for i in matchidlist if i not in previous_entries]

        id_length = len(matchidlist)
        start = 0
        stop = 100
        inc = 50
        while id_length > 0:
            if id_length - inc > 0:
                storage = add_stacked_layers(process_helper(slice(matchidlist, start, stop)))
                # process_helper(slice(matchidlist, start, stop))
                start += inc
                stop +=inc
            else:
                print('in the else statement start is %s end is goign to be %s' % (start, len(matchidlist)))
                storage = add_stacked_layers(process_helper(slice(matchidlist, start, len(matchidlist))))
            id_length -= inc
            print('finished %sth level' % (start/inc))

