from rest_framework import serializers
from .models import CustomUser, Visitor, Reservation, Communication, Apartment

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'name', 'document', 'telephone', 'user_type', 'apartment')

class CustomUserCreateSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'name', 'document', 'telephone', 'user_type', 'apartment', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

class VisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        fields = ('id', 'name', 'document', 'telephone', 'apartment', 'registered_by', 'entry_date')
        read_only_fields = ['registered_by',]

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ('id', 'resident', 'space', 'date', 'time', 'end_time')
        read_only_fields = ['resident',]

class CommunicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Communication
        fields = ('id', 'sender', 'recipient', 'subject', 'message', 'sent_at')
        read_only_fields = ['sender',]

    def validate_recipient(self, recipient):
        sender = self.context['request'].user

        if sender.user_type == "morador" and recipient.user_type not in ["sindico", "admin"]:
            raise serializers.ValidationError("Moradores só podem comunicar com a administração ou síndico.")
        if sender.user_type in ["sindico", "admin"] and recipient.user_type != "morador":
            raise serializers.ValidationError("A administração e síndico só podem comunicar com moradores.")
        return recipient

class ApartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = ('id', 'number', 'block', 'floor')