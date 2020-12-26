# Pollution API - 2020, Or Aloni, Israel.
# This module receive local pollution data in Israel from different pollution and
# air-quality measurement station from around Israel.
# Parse the pollution data, get pollutants current level, and calculate
# the general air-quality and current pollution level in different
# localities and cities in Israel.
#
# Updated measurements from the Israeli Ministry of Environmental Protection [IMEP] API, at:
#           - http://www.sviva.gov.il/subjectsEnv/SvivaAir/AirQualityData/NationalAirMonitoing/Pages/Developers.aspx
#                                                                                                 (*Hebrew content*)

import requests
import sys

class ApiBase():
    def __init__(self):
        pass

    def requestApi(self, url, token=None, data_source=None):
        '''
        Receive answer from Api.
        :param url: Api's url.
        :param token: Api credentials
        :param data_source: Api credentials.
        :return: api's data.
        '''
        self.url = url
        headers = {'Authorization': token,
                  'envi-data-source': data_source}
        try:
            self.response = requests.get(url, headers=headers)
            if self.response:
                print(f'API status: {self.response.status_code}')
                return self.response
            else:
                print(f'Problem reaching API: {self.response.status_code}')
        except Exception as err:
            print(f'No response: {err}')

    def getApiData(self):
        self.data = self.response.content
        self.j_data = self.response.json()
        return [self.data, self.j_data]


class Pollution():
    def __init__(self):
        token = 'ApiToken 71e67c41-8478-4310-9293-196f559493ca'
        data_src = 'MANA'
        # url = 'https://api.svivaaqm.net/v1/envista/stations'
        self.url = 'https://api.svivaaqm.net/v1/envista/stations/375/data/latest'

        api = ApiBase()
        self.response = api.requestApi(self.url, token, data_src)
        self.data = self.response.content
        self.j_data = self.response.json()

    def setPollutionUrl(self, url):
        self.url = url

    def stationData(self):
        '''
        Retrieve all the station's pollution values.
        :return: self.pollution_values, a dictionary containing sub
        dictionaries with station's pollution latest values.
        '''
        self.dtime = self.j_data['data'][0]['datetime']
        self.values = self.j_data['data'][0]['channels']
        self.pollution_values = {'NOX': self.values[1],
                                 'NO2': self.values[2], 'O3': self.values[3],
                                 'PM2_5': self.values[6], 'SO2': self.values[5]}
        self.weather_values = {'rain': self.values[7], 'temp': self.values[8],
                               'humidity': self.values[9]}
        return self.pollution_values

    def stationWeather(self):
        '''
        The station's current weather values.
        :return: current weather values - rain, temperature and humidity.
        '''
        return self.weather_values

    def getValue(self, pollutant):
        '''
        Retrieve a specific pollutant value.
        :param pollutant: the name of the requested pollutant.
        :return: int of specified pollutant latest measured value.
        '''
        value = self.pollution_values[pollutant]['value']
        return value

    def calcPollution(self, cal_table=None):
        '''
        Calculates general pollution value, based
        on the AQI values of pollutant.
        :param cal_table: user can choose other calculation
        table. The default is the AQI values table.
        :return: general pollution value as an integer.
        '''
        # The AQI table value ranges. AQI ranges and values are
        # set in a two integers tuples list, representing the
        # bottom and top values of that range.
        AQI = [(0, 49), (50, 100), (101, 200), (201, 300), (301, 400), (401, 500)]
        if cal_table is None:
            cal_table = AQI

        # Set the ranges of the pollutants values the same way we set the AQI
        # table, each pollutant and his set ranges, as declared in the Israeli environmental laws.
        O3 = [(0, 35), (36, 70), (71, 97), (98, 117), (118, 155), (156, 188)]
        NO2 = [(0, 53), (54, 105), (106, 160), (161, 213), (214, 260), (261, 316)]
        SO2 = [(0, 67), (68, 133), (134, 163), (164, 191), (192, 253), (254, 303)]
        NOX = [(0, 250), (251, 499), (500, 750), (751, 1000), (1001, 1200), (1201, 1400)]
        PM2_5 = [(0, 18.5), (18.6, 37), (37.5, 84), (84.5, 130), (130.5, 165), (165.5, 200)]

        def calculate(calculation_table, poll_table, poll_value):
            '''
            Calculate the ranges of the cal_table, and pollutant table. Use calculated ranges
            to determine the AQI score (raw pollution level).

            :param calculation_table: the AQI table (default), or other passed measurement system's table.
            :param poll_table: the pollutant ranges table.
            :param poll_value: the latest measured pollutant value.
            :return: integer - AQI score (raw pollution level).
            '''
            # TODO: find out why api receive negative values (O3) from time to time.
            #  might be because of an error at the station, not the module.
            # Handling negative values received from API
            poll_value = abs(poll_value)
            ## DEBUG
            # print(f'poll table: {poll_table} \n poll_value: {poll_value} \n calc_table: {calculation_table}')
            if poll_table[0][0] < poll_value < poll_table[0][1]:
                calc_range = calculation_table[0]
                poll_range = poll_table[0]
            elif poll_table[1][0] <= poll_value <= poll_table[1][1]:
                calc_range = calculation_table[1]
                poll_range = poll_table[1]
            elif poll_table[2][0] <= poll_value <= poll_table[2][1]:
                calc_range = calculation_table[2]
                poll_range = poll_table[2]
            elif poll_table[3][0] <= poll_value <= poll_table[3][1]:
                calc_range = calculation_table[3]
                poll_range = poll_table[3]
            elif poll_table[4][0] <= poll_value <= poll_table[4][1]:
                calc_range = calculation_table[4]
                poll_range = poll_table[4]
            elif poll_table[5][0] <= poll_value <= poll_table[5][1]:
                calc_range = calculation_table[5]
                poll_range = poll_table[5]
            ## DEBUG
            # print(f'poll value: {poll_value}|||calc range: {calc_range[0]} - {calc_range[1]}||| poll_range: {poll_range[0]} - {poll_range[1]}')

            # The AQI score formula.
            # See: https://www.svivaaqm.net/Default.rtl.aspx (hebrew content)
            aqi_score = (calc_range[1] - calc_range[0]) * ((poll_value - poll_range[0]) / (poll_range[1] - poll_range[0])) + calc_range[0]

            return aqi_score

        def getGeneralPollutionValues(general_poll_score):
            '''
            Sets the General Pollution Levels[GPL] as a list.
            Based on the GPL, returns the color and string description
            of the local pollution level.
            :param general_poll_score: The final general pollution score.
            :return: a two elements tuple, containing a string of color name,
                    and descriptor string of the pollution level.
            '''

            # General pollution levels between 100 - (-400)
            GPL = [(-400, -201), (-200, -1), (0, 50), (51, 100)]
            colors = ['green', 'yellow', 'red', 'brown']
            colors.reverse()
            description = ['Good', 'Moderate', 'High', 'Very\nHigh']
            description.reverse()
            if GPL[0][0] < general_poll_score < GPL[0][1]:
                return (colors[0], description[0])
            elif GPL[1][0] < general_poll_score < GPL[1][1]:
                return (colors[1], description[1])
            elif GPL[2][0] < general_poll_score < GPL[2][1]:
                return (colors[2], description[2])
            elif GPL[3][0] < general_poll_score < GPL[3][1]:
                return (colors[3], description[3])


        # Getting the AQI score for all the relevant pollutant in pollution_value dictionary
        raw_aqi_scores = {}
        for pollutant in self.pollution_values.keys():
            ## DEBUG
            # print(eval(pollutant))
            raw_aqi_scores[f'{pollutant}_poll_score'] = calculate(cal_table, eval(pollutant), self.getValue(pollutant))
        ## DEBUG
        # print(raw_aqi_scores)
        # Calculating the pollution score of each pollutant.
        # We do that by subtracting the current value of the pollutant of 100.
        final_aqi_scores = [(100 - value) for value in raw_aqi_scores.values()]
        ## DEBUG
        # print(final_aqi_scores)

        # Finding the lowest pollutant's AQI score, which will set
        # the over all pollution level.
        final_aqi_scores.sort()

        self.general_score = final_aqi_scores[1]
        ## DEBUG
        print('final AQI scores:', final_aqi_scores)
        print('general score:', self.general_score)
        # Based on the lowest pollutant's AQI score, calculate the overall pollution
        # score (100 - (-400)) [100 - AQI score].
        self.pollution_descriptors = getGeneralPollutionValues(self.general_score)
        ## DEBUG
        print('pollution descriptors:', self.pollution_descriptors)

        return self.pollution_descriptors


if __name__ == '__main__':
    poll = Pollution()
    data = poll.stationData()
    ## DEBUG
    print(poll.j_data)
    level = poll.calcPollution()
    print(level)