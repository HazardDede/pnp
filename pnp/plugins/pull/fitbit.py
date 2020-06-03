"""Fitbit related plugins."""

import asyncio
import os
import pathlib
from functools import partial
from typing import Iterable, Any

import schema
from ruamel import yaml

from pnp import validator
from pnp.plugins import load_optional_module
from pnp.plugins.pull import AsyncPolling
from pnp.utils import auto_str_ignore, camel_to_snake, transform_dict_items, make_list, FileLock


@auto_str_ignore(['_tokens', '_client', '_tokens_tstamp', '_client_lock'])
class _FitbitBase(AsyncPolling):
    EXTRA = 'fitbit'

    TOKEN_SCHEMA = schema.Schema({
        'client_id': schema.Use(str),
        'client_secret': schema.Use(str),
        'access_token': schema.Use(str),
        'refresh_token': schema.Use(str),
        'expires_at': schema.Use(float)
    })

    def __init__(self, config, system=None, **kwargs):
        super().__init__(**kwargs)
        self._system = system

        # Absolute config path? Relative -> relative to pnp configuration file
        self._config = config
        if not os.path.isabs(config):
            self._config = os.path.join(self.base_path, config)
        validator.is_file(config=self._config)

        import threading
        self._client_lock = threading.Lock()
        self._tokens = None  # Set by _load_tokens
        self._tokens_tstamp = None  # Set by _load_tokens and _save_tokens
        self._client = None  # Set by client property

    @property
    def client(self):
        """Return the configured fitbit client."""
        with self._client_lock:
            if self._load_tokens():  # Check if tokens got refreshed by another process
                fbit = load_optional_module('fitbit', self.EXTRA)
                self._client = fbit.Fitbit(**self._tokens, oauth2=True,
                                           refresh_cb=self._save_tokens, system=self._system)
            return self._client

    def _load_tokens(self):
        current_tstamp = pathlib.Path(self._config).stat().st_mtime
        # Compare memorized modified timestamp (might be None initially) and current
        if self._tokens_tstamp == current_tstamp:
            # Tokens did not change. Skip
            return False

        self.logger.debug("Loading tokens from %s: Requesting lock", self._config)
        with FileLock(self._config):
            self.logger.debug("Loading tokens from %s: Lock acquired", self._config)
            with open(self._config, 'r') as fp:
                _tokens = yaml.safe_load(fp)
                self._tokens = self.TOKEN_SCHEMA.validate(_tokens)
            self._tokens_tstamp = current_tstamp
        self.logger.debug("Loading tokens from %s: Lock released", self._config)
        return True

    def _save_tokens(self, tokens):
        new_config = {
            'client_id': self._tokens.get('client_id'),
            'client_secret': self._tokens.get('client_secret'),
            'access_token': tokens.get('access_token'),
            'refresh_token': tokens.get('refresh_token'),
            'expires_at': tokens.get('expires_at')
        }
        self.logger.debug("Saving tokens to %s: Requesting lock", self._config)
        self.TOKEN_SCHEMA.validate(new_config)
        with FileLock(self._config):
            self.logger.debug("Saving tokens to %s: Lock acquired", self._config)
            with open(self._config, 'w') as fp:
                yaml.dump(new_config, fp, default_flow_style=False)
            self._tokens_tstamp = pathlib.Path(self._config).stat().st_mtime
            self._tokens = new_config
            self.logger.debug("Saving tokens to %s: Lock released", self._config)

    async def async_poll(self):
        raise NotImplementedError()  # pragma: no cover


@auto_str_ignore(['_resource_map'])
class Current(_FitbitBase):
    """
    Requests various latest / current metrics (steps, calories, distance, ...)
    from the fitbit api.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/fitbit.Current/index.md
    """
    def __init__(self, resources: Iterable[str], **kwargs: Any):
        super().__init__(**kwargs)
        self._resource_map = self._create_resource_map()
        self._resources = make_list(resources)
        for res in self._resources:
            validator.one_of(list(self._resource_map.keys()), resource=res)

    def _create_resource_map(self):
        return {
            # Activities
            'activities/calories': partial(self._conv, conv_fun=int),
            'activities/caloriesBMR': partial(self._conv, conv_fun=int),
            'activities/steps': partial(self._conv, conv_fun=int),
            'activities/distance': partial(self._conv, conv_fun=float),
            'activities/floors': partial(self._conv, conv_fun=int),
            'activities/elevation': partial(self._conv, conv_fun=int),
            'activities/minutesSedentary': partial(self._conv, conv_fun=int),
            'activities/minutesLightlyActive': partial(self._conv, conv_fun=int),
            'activities/minutesFairlyActive': partial(self._conv, conv_fun=int),
            'activities/minutesVeryActive': partial(self._conv, conv_fun=int),
            'activities/activityCalories': partial(self._conv, conv_fun=int),
            # Body
            'body/bmi': partial(self._conv, conv_fun=float),
            'body/fat': partial(self._conv, conv_fun=float),
            'body/weight': partial(self._conv, conv_fun=float),
            # Foods
            'foods/log/caloriesIn': partial(self._conv, conv_fun=int),
            'foods/log/water': partial(self._conv, conv_fun=float),
            # Sleep
            'sleep/awakeningsCount': partial(self._conv, conv_fun=int),
            'sleep/efficiency': partial(self._conv, conv_fun=int),
            'sleep/minutesAfterWakeup': partial(self._conv, conv_fun=int),
            'sleep/minutesAsleep': partial(self._conv, conv_fun=int),
            'sleep/minutesAwake': partial(self._conv, conv_fun=int),
            'sleep/minutesToFallAsleep': partial(self._conv, conv_fun=int),
            'sleep/startTime': partial(self._conv, conv_fun=None),
            'sleep/timeInBed': partial(self._conv, conv_fun=int)
        }

    def _conv(self, resource, conv_fun):
        resp = self._api_fetch_current(resource)
        return conv_fun(resp) if conv_fun else resp

    def _api_fetch_current(self, resource):
        resp = self.client.time_series(resource, period='7d')
        first_key = next(iter(resp.values()))
        if first_key is None:
            return None  # pragma: no cover
        return first_key[-1].get('value')

    def _call(self, resource):
        return self._resource_map.get(resource)(resource)

    async def async_poll(self):
        loop = asyncio.get_event_loop()
        coros = [loop.run_in_executor(None, self._call, res) for res in self._resources]
        results = await asyncio.gather(*coros)
        return transform_dict_items({
            res: results[i] for i, res in enumerate(self._resources)
        }, keys_fun=camel_to_snake)


class Devices(_FitbitBase):
    """
    Requests details (battery, model, ...) about your fitbit devices / trackers
    associated to your account.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/fitbit.Devices/index.md
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def async_poll(self):
        devices = await asyncio.get_event_loop().run_in_executor(None, self.client.get_devices)
        return [transform_dict_items(d, keys_fun=camel_to_snake) for d in devices]


@auto_str_ignore(['_goals_map'])
class Goal(_FitbitBase):
    """
    Requests your goals (water, steps, ...) from the fitbit api.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/fitbit.Goal/index.md
    """
    def __init__(self, goals, **kwargs):
        super().__init__(**kwargs)
        self._goals_map = self._create_goal_map()
        self._goals = make_list(goals)
        for goal in self._goals:
            validator.one_of(list(self._goals_map.keys()), goal=goal)

    def _create_goal_map(self):
        return {
            'body/fat': lambda goal: float(self.client.body_fat_goal().get('goal', {}).get('fat')),
            'body/weight': lambda goal: (
                float(self.client.body_weight_goal().get('goal', {}).get('weight'))
            ),
            'activities/daily/activeMinutes': self._get_daily_activity_goal,
            'activities/daily/caloriesOut': self._get_daily_activity_goal,
            'activities/daily/distance': self._get_daily_activity_goal,
            'activities/daily/floors': self._get_daily_activity_goal,
            'activities/daily/steps': self._get_daily_activity_goal,
            'activities/weekly/distance': self._get_weekly_activity_goal,
            'activities/weekly/floors': self._get_weekly_activity_goal,
            'activities/weekly/steps': self._get_weekly_activity_goal,
            'foods/calories': lambda goal: (
                int(self.client.food_goal().get('goals', {}).get('calories'))
            ),
            'foods/water': lambda goal: int(self.client.water_goal().get('goal', {}).get('goal'))
        }

    def _get_daily_activity_goal(self, goal):
        single_goal = goal.split('/')[-1]
        conv = float if single_goal == 'distance' else int
        return conv(self.client.activities_daily_goal().get('goals', {}).get(single_goal))

    def _get_weekly_activity_goal(self, goal):
        single_goal = goal.split('/')[-1]
        conv = float if single_goal == 'distance' else int
        return conv(self.client.activities_weekly_goal().get('goals', {}).get(single_goal))

    def _call(self, goal):
        return self._goals_map.get(goal)(goal)

    async def async_poll(self):
        loop = asyncio.get_event_loop()
        coros = [loop.run_in_executor(None, self._call, goal) for goal in self._goals]
        results = await asyncio.gather(*coros)
        return transform_dict_items({
            goal: results[i] for i, goal in enumerate(self._goals)
        }, keys_fun=camel_to_snake)
