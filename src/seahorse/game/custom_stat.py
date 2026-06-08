from typing import TypedDict, Any


class CustomStat(TypedDict):
    """
    A typed dictionary class representing a custom statistic format.

    Attributes:
        name (str): The statistic name.
            Example: 'points_per_game', 'accuracy_rate'
        value (Any): The statistic value.
            Can be any data type (int, float, str, etc.)
        agent_id (int): The Player ID to which the statistic is attributed.
    """

    name: str
    value: Any
    agent_id: int
