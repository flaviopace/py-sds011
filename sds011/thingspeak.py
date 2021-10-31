import httplib2, urllib

class Thingspeak(object):                       # define a class called Thingspeak

    def __init__(self, write_api_key = None, read_api_key=None, channel_id=0):
        """
        :param write_key:  takes a string of write api key
        :param timer: can take integer values
        """
        self.write_key = write_api_key
        self.channel_id = channel_id
        self.read_api_key = read_api_key

        # Private Var cannot change
        self.__url = 'api.thingspeak.com:80'
        self.__read_url = 'https://api.thingspeak.com/channels/{}/feeds.json?api_key='.format(channel_id)

    def post_cloud(self, value1, value2, value3, value4):
        try:
            """
            :param value1: can be interger or float
            :param value2: can be interger or float
            :return: updated to cloud storage
            """
            params = urllib.parse.urlencode({'field1': value1, 'field2': value2, 'field3': value3, \
                                       'field4': value4, 'key': self.write_key})
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            print("Uploading data to : {} ".format(self.__url))
            conn = httplib2.HTTPConnectionWithTimeout(self.__url)
            conn.request("POST", "/update", params, headers)
            response = conn.getresponse()
            print("Response: {} , Status {}".format(response.status, response.reason))
            data = response.read()
            conn.close()

        except Exception as err:
            print('could not post to the cloud server due to: {}'.format(err))

    def read_cloud(self, result=1):
        try:
            """
            :param result: how many data you want to fetch accept interger
            :return: Two List which contains Sensor data
            """
            URL_R = self.__read_url
            read_key = self.read_api_key
            header_r = '&results={}'.format(result)

            new_read_url = URL_R + read_key + header_r
            data = requests.get(new_read_url).json()
            field1 = data['feeds']

            for x in field1:
                self.feild1.append(x['field1'])
                self.feild2.append(x['field2'])

            return self.feild1, self.feild2
        except:
            print('read_cloud failed !!!! ')


class IfTTT(object):

    def __init__(self, eventname='', key=''):

        self.eventname = eventname
        self.Key = key
        self.__Url = 'https://maker.ifttt.com/trigger/{}/with/key/'.format(self.eventname)
        self.New_Url = self.__Url + self.Key

        print(self.New_Url)

    def iftt_post(self, data1=10, data2=11):
        try:
            """
            :param data1:  pass your sensor value only integer
            :param data2: pass your data as interger only
            :return:      True if it was successful
            """

            URl = self.New_Url
            Key = self.Key
            payload = {'value1': data1,
                       'value2': data2}

            requests.post(self.New_Url, data=payload)
            print("Done posted on IFTTT")

            return True
        except:
            print('failed to post to cloud sever ! ')


class Location(object):

    def __init__(self):
        pass

    def get_locations(self):
        """
        :return: Lat and Long
        """
        try:
            g = geocoder.ip('me')
            my_string=g.latlng
            longitude=my_string[0]
            latitude=my_string[1]

            return longitude,latitude
        except:
            print('Error make sure you have Geo-Coder Installed ')


class DateandTime(object):

    def __init__(self):
        pass

    @ staticmethod
    def get_time_date():
        try:
            """
            :return:  date and time
            """
            my = datetime.datetime.now()
            data_time = '{}:{}:{}'.format(my.hour,my.minute,my.second)
            data_date = '{}/{}/{}'.format(my.day,my.month,my.year)
            return data_date,data_time
        except:
            print('could now get date and time ')

    def convert_timestamp(self,timestamp):
        timestamp = 1554506464
        dt_object = datetime.fromtimestamp(timestamp)
        return dt_object


class Weather_details(object):

    def __init__(self,key='', city=''):
        self.city = city
        self.key = key


    def get_weather_data(self):
        try:
            city = self.city
            key = self.key

            URL='http://api.openweathermap.org/data/2.5/weather?appid={}&q={}'.format(key,city)
            print(URL)

            data = requests.get(URL).json()
            long = data['coord']['lon']
            lat = data['coord']['lat']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            wind_degree = data['wind']['deg']
            sunrise = data['sys']['sunrise']
            sunset = data['sys']['sunset']

            m1 = data['weather'][0]['description']
            m2 = data['weather'][0]['main']
            body = '{} {}'.format(m1, m2)

            return long, lat, humidity, wind_speed, wind_degree, sunrise, sunset,body

        except:
            print('Error occured ')