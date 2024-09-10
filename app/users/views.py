import json
import requests
from rest_framework.views import APIView
from django.http import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.parsers import JSONParser
from decouple import config
from datetime import datetime

from services.screens import CachedUser
from services.bot import LitterTraceBotService
from services.utils import LitterTraceWhatsappService

class LitterTraceCloudApiWebhook(APIView):
    """Cloud Api Webhook"""
    parser_classes = (JSONParser,)

    @staticmethod
    def post(request):
        payload = request.data.get('entry')[0].get('changes')[0].get('value')
        print(payload)
        if payload.get('messages'):
            phone_number_id = payload['metadata'].get('phone_number_id')
            message = payload['messages'][0]
            message_type = message['type']
            contact = payload['contacts'][0] if message_type != "system" else payload['messages'][0].get("wa_id")

            if message_type == "system":
                JsonResponse({"message": "received"}, status=status.HTTP_200_OK)

            if message_type == "text":
                payload['body'] = message['text']['body']

            elif message_type == "button":
                payload['body'] = message['button']['payload']

            elif message_type == "interactive":
                if message.get('interactive'):
                    if message['interactive']['type'] == "button_reply":
                        payload['body'] = message['interactive']['button_reply']['id']
                    elif message['interactive'].get('type') == "nfm_reply":
                        message_type = "nfm_reply"
                        payload['body'] = json.loads(message['interactive']['nfm_reply']['response_json'])
                    else:
                        payload['body'] = message['interactive']['list_reply']['id']
                else:
                    return JsonResponse({"message": "received"}, status=status.HTTP_200_OK)
            elif message_type == "location":
                payload['body'] = (message['location']['latitude'], message['location']['longitude'])

            elif message_type == "image":
                image_id = message['image']['id']
                headers = {
                    'Authorization': 'Bearer ' + config('WHATSAPP_ACCESS_TOKEN')
                }
                file = requests.request(
                    "GET", url=f"https://graph.facebook.com/v18.0/{image_id}", headers=headers, data={}).json()

                caption = message['image'].get('caption')
                payload['file_id'] = image_id
                if caption:
                    payload['caption'] = caption
                payload['body'] = file.get('url')
                payload['file_name'] = file.get('name')

            elif message_type == "document":
                document_id = message['document']['id']
                headers = {
                    'Authorization': 'Bearer ' + config('WHATSAPP_ACCESS_TOKEN')
                }
                file = requests.request(
                    "GET", url=f"https://graph.facebook.com/v18.0/{document_id}", headers=headers,
                    data={}).json()
                payload['body'] = file.get('url')
                payload['file_name'] = file.get('name')
                payload['file_id'] = document_id

            elif message_type == "video":
                video_id = message['video']['id']
                headers = {
                    'Authorization': 'Bearer ' + config('WHATSAPP_ACCESS_TOKEN')
                }
                file = requests.request(
                    "GET", url=f"https://graph.facebook.com/v18.0/{video_id}", headers=headers, data={}).json()
                payload['body'] = file.get('url')
                payload['file_name'] = file.get('name')
                payload['file_id'] = video_id
                caption = message['video'].get('caption')
                if caption:
                    payload['caption'] = caption
            elif message_type == "audio":
                audio_id = message['audio']['id']
                headers = {
                    'Authorization': 'Bearer ' + config('WHATSAPP_ACCESS_TOKEN')
                }
                file = requests.request(
                    "GET", url=f"https://graph.facebook.com/v18.0/{audio_id}", headers=headers, data={}).json()
                payload['body'] = file.get('url')
                payload['file_name'] = file.get('name')

            elif message_type == "order":
                payload['body'] = message['order']['product_items']

            elif message_type == "nfm_reply":
                payload['body'] = message['nfm_reply']['response_json']

            if f"{payload.get('body')}".lower() in ["ok", "thanks", "thank you"]:
                MegamarketWhatsappService(payload={
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": contact['wa_id'],
                    "type": "text",
                    "text": {
                        "body": '🙏'
                    }
                }, phone_number_id=payload['metadata']['phone_number_id']).notify()

                return JsonResponse({"message": "received"}, status=status.HTTP_200_OK)

            elif message_type == "reaction":
                payload['body'] = message['reaction'].get('emoji')
                if f"{payload['body']}".lower() in ["👍", "🙏", "❤️", "ok", "thanks", "thank you"]:
                    LitterTraceWhatsappService(payload={
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": contact['wa_id'],
                        "type": "text",
                        "text": {
                            "body": '🙏'
                        }
                    }, phone_number_id=payload['metadata']['phone_number_id']).notify()
                    return JsonResponse({"message": "received"}, status=status.HTTP_200_OK)

            if not contact:
                return JsonResponse({"message": "received"}, status=status.HTTP_200_OK)

            # Format the message
            formatted_message = {
                "to": payload['metadata']['display_phone_number'],
                "phone_number_id": payload['metadata']['phone_number_id'],
                "from": contact['wa_id'],
                "username": contact['profile']['name'],
                "type": message_type,
                "message": payload['body'],
                "filename": payload.get('file_name', None),
                "fileid": payload.get('file_id', None),
                "caption": payload.get('caption', None),
            }
            print(formatted_message)

    
            user = CachedUser(formatted_message.get('from'))
            state = user.state
            current_state = state.get_state(user)
            if not isinstance(current_state, dict):
                current_state = current_state.state
            message_stamp = datetime.fromtimestamp(int(message['timestamp']))

            # Calculate the time difference in seconds
            if (datetime.now() - message_stamp).total_seconds() > 10:
                print("IGNORING OLD HOOK ", message_stamp)
                return JsonResponse({"message": "received"}, status=status.HTTP_200_OK)

            print(f"Litter Trace {state.stage}<|>{state.option}] RECEIVED - > ", payload['body'], " FROM ",
                  formatted_message.get('from'), " @ ", message_stamp,
                  f"({(datetime.now() - message_stamp).total_seconds()} sec ago)")

            try:
                service = LitterTraceBotService(payload=formatted_message, user=user)
                LitterTraceWhatsappService(payload=service.response, phone_number_id= payload['metadata']['phone_number_id']).send_message()
            except Exception as e:
                print(e)
            print(f"TOOK  {(datetime.now() - message_stamp).total_seconds()} s")

            return JsonResponse({"message": "received"}, status=status.HTTP_200_OK)
        return JsonResponse({"message": "received"}, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        return HttpResponse(request.query_params.get('hub.challenge'), 200)

