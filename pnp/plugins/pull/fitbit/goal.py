"""Pull: fitbit.Goal."""

import asyncio
from typing import Any, Callable, Dict, Iterable

from pnp import validator
from pnp.plugins.pull.fitbit.shared import FitbitBase
from pnp.typing import Payload
from pnp.utils import camel_to_snake, transform_dict_items, make_list


__EXTRA__ = 'fitbit'


GoalName = str
GoalValue = Any
GoalFunction = Callable[[GoalName], GoalValue]
GoalsMap = Dict[GoalName, GoalFunction]


class Goal(FitbitBase):
    """
    Requests your goals (water, steps, ...) from the fitbit api.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#fitbit-goal
    """
    __REPR_FIELDS__ = ['goals']

    def __init__(self, goals: Iterable[GoalName], **kwargs: Any):
        super().__init__(**kwargs)
        self._goals_map = self._create_goal_map()
        self.goals = make_list(goals) or []
        for goal in self.goals:
            validator.one_of(list(self._goals_map.keys()), goal=goal)

    def _create_goal_map(self) -> GoalsMap:
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

    def _get_daily_activity_goal(self, goal: GoalName) -> GoalValue:
        single_goal = goal.split('/')[-1]
        conv = float if single_goal == 'distance' else int
        return conv(self.client.activities_daily_goal().get('goals', {}).get(single_goal))

    def _get_weekly_activity_goal(self, goal: GoalName) -> GoalValue:
        single_goal = goal.split('/')[-1]
        conv = float if single_goal == 'distance' else int
        return conv(self.client.activities_weekly_goal().get('goals', {}).get(single_goal))

    def _call(self, goal: GoalName) -> GoalValue:
        return self._goals_map[goal](goal)

    async def _poll(self) -> Payload:
        loop = asyncio.get_event_loop()
        coros = [loop.run_in_executor(None, self._call, goal) for goal in self.goals]
        results = await asyncio.gather(*coros)
        return transform_dict_items({  # type: ignore
            goal: results[i] for i, goal in enumerate(self.goals)
        }, keys_fun=camel_to_snake)
