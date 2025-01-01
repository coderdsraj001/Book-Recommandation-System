from rest_framework import serializers
from .models import CustomUser
from .models import Book
from .models import ReadingList
from .models import ReadingListItem

from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'first_name', 'last_name', ]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user
    

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise ValidationError("Invalid email or password")

        if not user.check_password(password):
            raise ValidationError("Invalid email or password")

        token, created = Token.objects.get_or_create(user=user)
        return {"email": user.email, "token": token.key}


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

    
class ReadingListItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)  

    class Meta:
        model = ReadingListItem
        fields = ['id', 'book', 'order']


class ReadingListSerializer(serializers.ModelSerializer):
    items = ReadingListItemSerializer(many=True)

    class Meta:
        model = ReadingList
        fields = ['id', 'name', 'created_at', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        reading_list = ReadingList.objects.create(**validated_data)
        for item_data in items_data:
            ReadingListItem.objects.create(reading_list=reading_list, **item_data)
        return reading_list

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        existing_items = {item.id: item for item in instance.items.all()}

        new_items = []

        for item_data in items_data:
            item_id = item_data.get('id')
            if item_id and item_id in existing_items:
                item = existing_items[item_id]
                item.order = item_data.get('order', item.order)
                item.book_id = item_data.get('book', item.book_id) 
                item.save()
            else:
                new_items.append(ReadingListItem(reading_list=instance, **item_data))

        if new_items:
            ReadingListItem.objects.bulk_create(new_items)

        return instance

