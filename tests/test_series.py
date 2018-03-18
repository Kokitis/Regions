import unittest
from pony.orm import db_session
import pyregions
from .setup_tests import importTestData
import os
from pprint import pprint
import math
import datetime

series_code = 'POP'
region_code = 'USA-NY'

truthset = {1900:         7283000,
			1901:         7449000,
			1902:         7612000,
			1903:         7771000,
			1904:         7927000,
			1905:         8084000,
			1906:         8289000,
			1907:         8499000,
			1908:         8714000,
			1909:         8935000,
			1910:         9137000,
			1911:         9249000,
			1912:         9361000,
			1913:         9473000,
			1914:         9585000,
			1915:         9700000,
			1916:         9848000,
			1917:         9993000,
			1918:         9936000,
			1919:         10252000,
			1920:         10282000,
			1921:         10416000,
			1922:         10589000,
			1923:         10752000,
			1924:         10953000,
			1925:         11186000,
			1926:         11257000,
			1927:         11174000,
			1928:         11599000,
			1929:         12171000,
			1930:         12647000,
			1931:         12848000,
			1932:         13001000,
			1933:         13126000,
			1934:         13253000,
			1935:         13375000,
			1936:         13481000,
			1937:         13511000,
			1938:         13512000,
			1939:         13523000,
			1940:         13456000,
			1941:         13267000,
			1942:         13002000,
			1943:         12807000,
			1944:         12628000,
			1945:         12495000,
			1946:         13398000,
			1947:         13982000,
			1948:         14497000,
			1949:         14892000,
			1950:         14865000,
			1951:         14890000,
			1952:         15192000,
			1953:         15527000,
			1954:         15814000,
			1955:         15966000,
			1956:         16112000,
			1957:         16374000,
			1958:         16601000,
			1959:         16685000,
			1960:         16838000,
			1961:         17061000,
			1962:         17301000,
			1963:         17461000,
			1964:         17589000,
			1965:         17734000,
			1966:         17843000,
			1967:         17935000,
			1968:         18051000,
			1969:         18105000,
			1970:         18241391,
			1971:         18357982,
			1972:         18339400,
			1973:         18177063,
			1974:         18049775,
			1975:         18003485,
			1976:         17940541,
			1977:         17812602,
			1978:         17680589,
			1979:         17583838,
			1980:         17558072,
			1981:         17567734,
			1982:         17589738,
			1983:         17686905,
			1984:         17745684,
			1985:         17791672,
			1986:         17833419,
			1987:         17868848,
			1988:         17941309,
			1989:         17983086,
			1990:         17990455,
			'ISO Code':   'USA-NY',
			'State Code': 'NY'}


class TestSeries(unittest.TestCase):
	def setUp(self):
		self.database_filename = os.path.join(os.path.dirname(__file__), 'test_data', 'test_database.sqlite')
		self.database = pyregions.RegionDatabase(self.database_filename, True, replace = False)
		self.database.addNamespace('ISO')
		self.database.addNamespace('USPS')
		self.database.addFromApi(importTestData())
		self.test_series = self.database.getSeries(region_code, series_code)

	def test_series_datetime_index(self):
		year = datetime.datetime(1981, 1, 1)

		self.assertTrue(year in self.test_series.series.index)
		self.assertTrue(year in self.test_series.index)

	def test_series_int_index(self):
		year = 1981
		self.assertTrue(year in self.test_series.ix)

	def test_series_float_index(self):
		year = 1981.0
		self.assertTrue(year in self.test_series.fx)

	def test_series_operations_yearly_growth(self):
		yearly_growth = self.test_series.timeChange('yearlyGrowth')
		year = 1972

		test_value = yearly_growth[datetime.datetime(year, 1, 1)]

		true_value = (truthset[year] - truthset[year - 1]) / truthset[year - 1]

		self.assertTrue(math.isclose(true_value, test_value))

	def test_series_operations_yearly_change(self):
		yearly_change = self.test_series.timeChange('yearlyChange')
		year = 1984

		test_value = yearly_change[datetime.datetime(year, 1, 1)]
		true_value = truthset[year] - truthset[year - 1]

		self.assertTrue(true_value == test_value)

	def test_series_get_values(self):
		year = 1989

		test_value = self.test_series.getValue(year)
		true_value = truthset[year]

		self.assertTrue(test_value == true_value)

	def test_interpolated_value(self):
		year = 1973.5
		test_value = self.test_series.getValue(year)
		true_value = (truthset[1974] + truthset[1973]) / 2

		self.assertTrue(test_value == true_value)


if __name__ == "__main__":
	pass
