from matrx.actions.action import Action, ActionResult


class Idle(Action):
    def __init__(self, duration_in_ticks=1):
        super().__init__(duration_in_ticks)

    def is_possible(self, grid_world, agent_id, **kwargs):
        # Maybe do a check to see if the empty location is really and still empty?
        return IdleResult(IdleResult.RESULT_SUCCESS, True)


class IdleResult(ActionResult):
    """ Result when falling succeeded. """
    RESULT_SUCCESS = 'Idling action successful'

    """ Result when the emptied space was not actually empty. """
    RESULT_FAILED = 'Failed to idle'

    def __init__(self, result, succeeded):
        super().__init__(result, succeeded)