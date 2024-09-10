from django.core.cache import cache
from datetime import timedelta

GREETINGS = [
    "menu",
    "memu",
    "hi",
    "hie",
    "cancel",
    "home",
    "hy",
    "reset",
    "hello",
    "x",
    "c",
    "no",
    "No",
    "n",
    "N",
    "hey",
    "y",
    "yes",
    "retry"
]

import datetime


def get_greeting(name):
    current_time = datetime.datetime.now() + timedelta(hours=2)
    hour = current_time.hour

    if 5 <= hour < 12:
        return f"Good Morning {name} 🌅"
    elif 12 <= hour < 18:
        return f"Good Afternoon {name} ☀️"
    elif 18 <= hour < 22:
        return f"Good Evening{name}  🌆"
    else:
        return f"Hello There {name} 🌙"


class CachedUserState:
    def __init__(self, user) -> None:
        self.user = user
        self.stage = cache.get(f"littertrace_{self.user.mobile_number}_stage", "handle_action_menu")
        self.option = cache.get(f"littertrace_{self.user.mobile_number}_option")
        self.state = cache.get(f"littertrace_{self.user.mobile_number}", {})

    def update_state(self, state: dict, update_from, stage=None, option=None, direction=None):
        """Get wallets by user."""
        # pylint: disable=no-member
        print("UPDATING STATE : ", update_from)
        cache.set(f"littertrace_{self.user.mobile_number}", state, timeout=60*30)
        if stage:
            cache.set(f"littertrace_{self.user.mobile_number}_stage", stage, timeout=60*30)
        if option:
            cache.set(f"littertrace_{self.user.mobile_number}_option", option, timeout=60*30)

    def get_state(self, user):
        self.state = cache.get(f"littertrace_{user.mobile_number}", {})
        return self.state

    def reset_state(self):
        state = cache.get(f"littertrace_{self.user.mobile_number}", {})
        state['state'] = {}
        cache.set(f"littertrace_{self.user.mobile_number}_stage", "handle_action_menu", timeout=60*30)
        cache.delete(f"littertrace_{self.user.mobile_number}_option")
        return cache.set(f"littertrace_{self.user.mobile_number}", state, timeout=60*30)


class CachedUser:
    def __init__(self, mobile_number, record=None) -> None:
        self.record = record
        self.first_name = "Welcome"
        self.last_name = "Visitor"
        self.role = "DEFAULT"
        self.email = "customer@litter.co.zw"
        self.mobile_number = mobile_number
        self.registration_complete = False
        self.state = CachedUserState(self)


MENU_OPTIONS = {
    '1': "handle_report_litter",
    "handle_report_litter": "handle_report_litter",
    '2': "handle_action_locate_litter",
    'handle_action_locate_litter': "handle_action_locate_litter",
    '3': "handle_action_volunteer_coordination",
    'handle_action_volunteer_coordination': "handle_action_volunteer_coordination",
    '4': "handle_action_donation",
    'handle_action_donation': "handle_action_donation",
    '5': "handle_action_frequently_asked",
    'handle_action_frequently_asked': "handle_action_frequently_asked",
}
