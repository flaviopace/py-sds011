import httplib2, urllib

# Station parameter
station = {
    'id': "cremano-station-01",
    'name': "San Giorgio a Cremano (NA) - SDS011",
    'location': {
        'latitude': 40.8352685243,
        'longitude': 14.3311296176
    }
}
org = {
          "website": "https://www.cremano-air.com/",
          "name": "San Giorgio A Cremano Air Quality Monitor",
      },


class Aqicn(object):  # define a class called Aqicn

    def __init__(self, token=None):
        """
        :param token:  takes a string related to the uniqe token
        """
        self.token = token
        self.station_id = "cremano-station-01"
        self.station_name = "San Giorgio a Cremano (NA) - SDS011"
        self.station_latitude = 40.8352685243
        self.station_longitude = 14.3311296176
        self.org_website = "https://www.cremano-air.com/"
        self.org_name = "San Giorgio A Cremano Air Quality Monitor"

        # Private Var cannot change
        self.__url = 'aqicn.org'

    def post_cloud(self, pm2_5, pm10):
        try:
            """
            :param pm2_5: can be interger or float
            :param pm10: can be interger or float
            :return: updated to cloud storage
            """
            params = urllib.parse.urlencode({'token': self.token, 'station.id': self.station_id, \
                                             'station_name': self.station_name, 'station.latitude': self.station_latitude, \
                                             'station.longitude': self.station_longitude, 'org.website': self.org_website, \
                                             'org.name': self.org_name, 'sensor.specie': 'pm25', 'sensor.value': pm2_5, \
                                             'sensor.specie': 'pm10', 'sensor.value': pm10 })
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            conn = httplib2.HTTPConnectionWithTimeout(self.__url)
            print("Uploading data to : {} ".format(self.__url))
            conn.request("POST", "/sensor/upload", params, headers)
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