"""Pull: fitbit.Current."""

import asyncio
from functools import partial
from typing import Iterable, Any, Dict, Callable

from pnp import validator
from pnp.plugins.pull.fitbit.shared import FitbitBase
from pnp.typing import Payload
from pnp.utils import camel_to_snake, transform_dict_items, make_list

__EXTRA__ = 'fitbit'

ResourceName = str
ResourceValue = Any
ConversionFunction = Callable[[ResourceValue], ResourceValue]
ResourceFunction = Callable[[ResourceName], ResourceValue]
ResourceMap = Dict[str, ResourceFunction]


class Current(FitbitBase):
    """
    Requests various latest / current metrics (steps, calories, distance, ...)
    from the fitbit api.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#fitbit-current
    """
    __REPR_FIELDS__ = ['resources']

    def __init__(self, resources: Iterable[ResourceName], **kwargs: Any):
        super().__init__(**kwargs)
        self._resource_map = self._create_resource_map()
        self.resources = make_list(resources) or []
        for res in self.resources:
            validator.one_of(list(self._resource_map.keys()), resource=res)

    def _create_resource_map(self) -> ResourceMap:
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

    def _conv(self, resource: ResourceName, conv_fun: ConversionFunction) -> ResourceValue:
        resp = self._api_fetch_current(resource)
        return conv_fun(resp) if conv_fun else resp

    def _api_fetch_current(self, resource: ResourceName) -> ResourceValue:
        resp = self.client.time_series(resource, period='7d')
        first_key = next(iter(resp.values()))
        if first_key is None:
            return None  # pragma: no cover
        return first_key[-1].get('value')

    def _call(self, resource: ResourceName) -> ResourceValue:
        return self._resource_map[resource](resource)

    async def _poll(self) -> Payload:
        loop = asyncio.get_event_loop()
        coros = [loop.run_in_executor(None, self._call, res) for res in self.resources]
        results = await asyncio.gather(*coros)
        return transform_dict_items({  # type: ignore
            res: results[i] for i, res in enumerate(self.resources)
        }, keys_fun=camel_to_snake)
