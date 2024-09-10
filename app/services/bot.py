import locale
from services.screens import *
from services.constants import *
from django.db.models import Q

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


class LitterTraceBotService:
    def __init__(self, payload, user: object) -> None:
        self.message = payload
        self.user = user
        self.body = self.message['message']

        # Load
        state = self.user.state
        print("####### ", self.user.state)
        current_state = state.get_state(self.user)
        if not isinstance(current_state, dict):
            current_state = current_state.state

        self.current_state = current_state
        try:
            self.response = self.handle()
            # print(self.response)
        except Exception as e:
            print("ERROR : ", e)

    def handle(self):

        state = self.user.state
        current_state = state.get_state(self.user)
        if not isinstance(current_state, dict):
            current_state = current_state.state

        if f"{self.body}".lower() in GREETINGS and f"{self.body}".lower() not in ["y", "yes", "retry", "n", "no"]:
            self.user.state.reset_state()
            state = self.user.state
            current_state = state.get_state(self.user)
            if not isinstance(current_state, dict):
                current_state = current_state.state
            current_state = {"state": {}}
            state.update_state(current_state, update_from='menu')
            return self.handle_action_menu
        

        # IF USER IS AT MENU STAGE FIND THE NEXT ROUTE BASED ON MESSAGE
        if self.user.state.stage == "handle_action_menu":
            selected_action = MENU_OPTIONS.get(f"{self.body}".lower())
            if not selected_action:
                return self.wrap_text(INVALID_ACTION, x_is_menu=True, navigate_is="Menu", plain=True)
            self.body = selected_action

        if f"{self.body}".startswith("handle_action_"):
            state = self.user.state
            if state:
                current_state = state.get_state(self.user)
                if not isinstance(current_state, dict):
                    current_state = current_state.state
                state.update_state(state=current_state, update_from="handle_action_", stage=self.body)

            self.user.state.reset_state()
            return getattr(self, self.body)
        else:
            state = self.user.state
            return getattr(self, state.stage)
 
    @property
    def handle_action_menu(self):
        state = self.user.state
        current_state = state.get_state(self.user)

        if not isinstance(current_state, dict):
            current_state = current_state.state

        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.user.mobile_number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": HOME.format(greeting=get_greeting(name=''), name=self.message['username'].title())
                },
                "action":
                    {
                        "button": "🕹️ Choose",
                        "sections": [
                            {
                                "title": "Options",
                                "rows":[
                                    {
                                        "id": "handle_report_litter",
                                        "title": f"🗣️ Report Litter"
                                    },
                                    {
                                        "id": "handle_action_locate_litter",
                                        "title": f"📍 Find Litter"
                                    },
                                    {
                                        "id": "handle_action_volunteer_coordination",
                                        "title": f"✋🏽 Volunteer"
                                    },
                                    {
                                        "id": "handle_action_donation",
                                        "title": f"💰 Donate"
                                    },
                                    {
                                        "id": "handle_action_frequently_asked",
                                        "title": f"❓Frequently Asked"
                                    }
                                ]
                            }
                        ]
                    }
            }
        }
