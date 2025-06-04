from typing import TypedDict


class CustomStat(TypedDict):
    """
    A typed dictionary class representing a custom statistic format.

    Attributes:
        name (str): The statistic name.
        value (object): The statistic value.
        agent_id (int): The Player ID to which the statistic is attributed.
    """

    name: str
    value: object
    agent_id: int
