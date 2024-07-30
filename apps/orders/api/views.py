import requests

from datetime import datetime
from decimal import Decimal

from apps.authentication.models import UserAddress
from apps.services.calculate_delivery_fee import calculate_delivery_fee
from apps.services.calculate_distance import get_distance_between_locations
from apps.services.generate_message import generate_order_message
from apps.services.is_restaurant_open import is_restaurant_open
from rest_framework import generics, status
from rest_framework.response import Response
from apps.orders.models import (
    Restaurant,
    TelegramBotToken,
    Order
)
from .serializers import (
    OrderSerializer,
    OrderPreviewSerializer,
    ReportSerializer,
    RestaurantSerializer,
    OrderListSerializer
)
from ...product.models import ProductSize, Topping  # Set, Ingredient
from ...services.bonuces import (
    calculate_bonus_points,
    apply_bonus_points
)
from ...services.calculate_bonus import calculate_and_apply_bonus
from ...services.send_telegram_message import send_telegram_message


class ListOrderView(generics.ListAPIView):
    serializer_class = OrderListSerializer

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user).order_by('-id')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'request': self.request
        })
        return context


class CreateOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        user_address_id = request.data.get('delivery').get('user_address_id')
        is_pickup = request.data.get('is_pickup', False)
        restaurant_id = request.data.get('restaurant_id', None)
        order_source = request.data.get('order_source', 'unknown')
        comment = request.data.get('comment', '')
        order_time = datetime.now()
        user_address_instance = UserAddress.objects.get(id=user_address_id, user=user)
        token = TelegramBotToken.objects.first()

        if not is_pickup and (not user_address_instance.latitude or not user_address_instance.longitude):
            return Response({"error": "User address does not have coordinates."}, status=status.HTTP_400_BAD_REQUEST)

        if not is_pickup:
            user_location = (user_address_instance.latitude, user_address_instance.longitude)
            nearest_restaurant = None
            min_distance = float('inf')

            for restaurant in Restaurant.objects.all():
                if restaurant.latitude and restaurant.longitude:
                    restaurant_location = (restaurant.latitude, restaurant.longitude)
                    distance = get_distance_between_locations(token.google_map_api_key, user_location,
                                                              restaurant_location)
                    if distance is not None and distance < min_distance and is_restaurant_open(restaurant, order_time):
                        min_distance = distance
                        nearest_restaurant = restaurant

            if not nearest_restaurant:
                return Response({"error": "No available restaurants found or all are closed."},
                                status=status.HTTP_400_BAD_REQUEST)

            delivery_fee = calculate_delivery_fee(min_distance)
        else:
            if restaurant_id:
                try:
                    nearest_restaurant = Restaurant.objects.get(id=restaurant_id)
                    if not is_restaurant_open(nearest_restaurant, order_time):
                        return Response({"error": "Selected restaurant is closed."}, status=status.HTTP_400_BAD_REQUEST)
                except Restaurant.DoesNotExist:
                    return Response({"error": "Restaurant not found."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Restaurant ID is required for pickup."}, status=status.HTTP_400_BAD_REQUEST)

            min_distance = 0
            delivery_fee = 0

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.context['nearest_restaurant'] = nearest_restaurant
        serializer.context['delivery_fee'] = delivery_fee
        serializer.context['user'] = user

        self.perform_create(serializer)

        order = serializer.instance
        order.user = self.request.user
        order.comment = comment
        bonus_points = calculate_bonus_points(Decimal(order.total_amount), Decimal(delivery_fee), order_source)
        apply_bonus_points(user, bonus_points)
        order.total_bonus_amount = bonus_points

        try:
            total_order_amount = calculate_and_apply_bonus(order)
            order.total_amount = total_order_amount + delivery_fee
            order.save()
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


        message = generate_order_message(order, min_distance, delivery_fee)
        print(message)
        bot_token_instance = TelegramBotToken.objects.first()
        if bot_token_instance:
            telegram_bot_token = bot_token_instance.bot_token
            telegram_chat_ids = nearest_restaurant.get_telegram_chat_ids()
            for chat_id in telegram_chat_ids:
                if chat_id:
                    send_telegram_message(telegram_bot_token, chat_id, message)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Не установлен токен бота Telegram."}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OrderPreviewView(generics.GenericAPIView):
    serializer_class = OrderPreviewSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        order_time = datetime.now()
        user_address_id = data.get('user_address_id')
        is_pickup = data.get('is_pickup', False)

        try:
            user_address_instance = UserAddress.objects.get(id=user_address_id, user=user)
        except UserAddress.DoesNotExist:
            return Response({"error": "User address does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        if not is_pickup and (not user_address_instance.latitude or not user_address_instance.longitude):
            return Response({"error": "User address does not have coordinates."}, status=status.HTTP_400_BAD_REQUEST)

        nearest_restaurant = None
        min_distance = float('inf')
        delivery_fee = 0

        if not is_pickup:
            user_location = (user_address_instance.latitude, user_address_instance.longitude)

            for restaurant in Restaurant.objects.all():
                if restaurant.latitude and restaurant.longitude:
                    restaurant_location = (restaurant.latitude, restaurant.longitude)
                    distance = get_distance_between_locations('AIzaSyCWbO5aOn8hS3EWJycj73dHqH8fHHfO4w4', user_location,
                                                              restaurant_location)
                    if distance is not None and distance < min_distance and is_restaurant_open(restaurant, order_time):
                        min_distance = distance
                        nearest_restaurant = restaurant

            if not nearest_restaurant:
                return Response({"error": "No available restaurants found or all are closed."},
                                status=status.HTTP_400_BAD_REQUEST)

            delivery_fee = calculate_delivery_fee(min_distance)

        response_data = {

            "delivery_info": {
                "distance_km": min_distance,
                "delivery_fee": delivery_fee
            } if not is_pickup else None,

        }

        return Response(response_data, status=status.HTTP_200_OK)


class ReportCreateView(generics.CreateAPIView):
    serializer_class = ReportSerializer

    def create(self, request, *args, **kwargs):
        # Получение данных из запроса
        description = request.data.get('description')
        contact_number = request.data.get('contact_number')
        image = request.FILES.get('image') if 'image' in request.FILES else None

        # Подготовка данных для сериализации
        report_data = {
            'description': description,
            'contact_number': contact_number,
            'image': image
        }

        # Валидация данных с помощью сериализатора
        serializer = self.get_serializer(data=report_data)
        serializer.is_valid(raise_exception=True)

        # Сохранение объекта report
        report = serializer.save()

        # Отправка репорта в Telegram
        self.send_report_to_telegram(report)

        # Возврат успешного ответа с данными репорта
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def send_report_to_telegram(self, report):
        # Получение экземпляра настроек бота
        bot_token_instance = TelegramBotToken.objects.first()
        if not bot_token_instance:
            print("Токен бота Telegram не настроен.")
            return

        # Инициализация бота
        telegram_bot_token = bot_token_instance.bot_token
        telegram_chat_ids = bot_token_instance.report_channels.split(',')

        # Формирование сообщения
        message = f"Новый репорт:\nОписание: {report.description}\nКонтактный номер: {report.contact_number}"

        # Отправка сообщения и изображения в каждый чат
        for chat_id in telegram_chat_ids:
            chat_id = chat_id.strip()
            message_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
            photo_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendPhoto"

            # Отправка сообщения
            message_payload = {
                'chat_id': chat_id,
                'text': message
            }
            response = requests.post(message_url, data=message_payload)
            if response.status_code != 200:
                print(f"Ошибка при отправке сообщения в чат {chat_id}: {response.text}")

            # Отправка фотографии
            if report.image:
                with report.image.open('rb') as image_file:
                    files = {'photo': image_file}
                    photo_payload = {'chat_id': chat_id}
                    response = requests.post(photo_url, data=photo_payload, files=files)
                    if response.status_code == 200:
                        print(f"Фотография отправлена в чат {chat_id}")
                    else:
                        print(f"Ошибка при отправке фотографии в чат {chat_id}: {response.text}")


class RestaurantListView(generics.ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
