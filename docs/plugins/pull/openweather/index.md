# pnp.plugins.pull.sensor.OpenWeather

Periodically polls weather data from the `OpenWeatherMap` api.

__Arguments__

**api_key (str):** The api_key you got from OpenWeatherMap after registration.<br/>
**lat (float):** Latitude. If you pass `lat`, you have to pass `lon` as well.<br/>
**lon (float):** Longitude. If you pass `lon`, you have to pass `lat` as well.<br/>
**city_name (str):** The name of your city. To minimize ambiguity use lat/lon or your country as a suffix,
e.g. London,GB.<br/>
**units (str on of (metric, imperial, kelvin))**: Specify units for temperature and speed.<br/>
imperial = fahrenheit + miles/hour, metric = celsius + m/secs, kelvin = kelvin + m/secs. Default is metric.<br/>
**tz (str, optional)**: Time zone to use for current time and last updated time. Default is your local timezone.

Remark: You have to pass whether `city_name` or `lat/lon`.

__Result__

```json
{
	"temperature": 13.03,
	"pressure": 1021,
	"humidity": 62,
	"cloudiness": 40,
	"wind": {
		"speed": 9.3,
		"deg": 300
	},
	"poll_dts": "2018-10-03T15:41:32.156930+02:00",
	"last_updated_dts": "2018-10-03T15:20:00+02:00",
	"raw": {
		"coord": {
			"lon": 10,
			"lat": 53.55
		},
		"weather": [{
			"id": 521,
			"main": "Rain",
			"description": "shower rain",
			"icon": "09d"
		}],
		"base": "stations",
		"main": {
			"temp": 13.03,
			"pressure": 1021,
			"humidity": 62,
			"temp_min": 12,
			"temp_max": 14
		},
		"visibility": 10000,
		"wind": {
			"speed": 9.3,
			"deg": 300
		},
		"clouds": {
			"all": 40
		},
		"dt": 1538572800,
		"sys": {
			"type": 1,
			"id": 4883,
			"message": 0.0202,
			"country": "DE",
			"sunrise": 1538544356,
			"sunset": 1538585449
		},
		"id": 2911298,
		"name": "Hamburg",
		"cod": 200
	}
}
```

You can consult the specification [https://openweathermap.org/current#parameter](https://openweathermap.org/current#parameter)
to checkout the documentation about the meaning of individual fields.

__Examples__

```yaml
# Make sure you export your api key with: `export OPENWEATHER_API_KEY=<your_api_key>`

- name: openweather
  pull:
    plugin: pnp.plugins.pull.sensor.OpenWeather
    args:
      city_name: "Hamburg,DE"  # Alternative: pass lat and lon
      # lon: 10
      # lat: 53.55
      units: metric  # imperial (fahrenheit + miles/hour), metric (celsius + m/secs), kelvin (kelvin + m/secs)
      instant_run: True
      # tz: GMT
  push:
    plugin: pnp.plugins.push.simple.Echo
```
