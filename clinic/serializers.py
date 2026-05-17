from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PatientProfile, DoctorProfile, AppointmentSlot, Appointment


# 用户序列化（只暴露必要字段）
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "username",
            "date_joined",
        ]

class PatientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = PatientProfile
        fields = [
            "id",
            "phone",
            "gender",
            "birthday",
            "user",
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)

        # 更新 user 信息
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        # 更新 patient 信息
        return super().update(instance, validated_data)

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = ["id", "name", "specialty", "description", "phone", "email", "is_active"]


# 时间段（slot）
class AppointmentSlotSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=DoctorProfile.objects.all(),
        source="doctor",
        write_only=True
    )

    class Meta:
        model = AppointmentSlot
        fields = [
            "id",
            "doctor",
            "doctor_id",
            "date",
            "time",
            "is_booked",
        ]



class AppointmentSerializer(serializers.ModelSerializer):
    patient = UserSerializer(read_only=True)
    slot = AppointmentSlotSerializer(read_only=True)

    slot_id = serializers.PrimaryKeyRelatedField(
        queryset=AppointmentSlot.objects.filter(is_booked=False),
        source="slot",
        write_only=True
    )

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "slot",
            "slot_id",
            "status",
            "created_at",
        ]
        read_only_fields = ["patient", "created_at"]

    def validate(self, data):
        slot = data["slot"]
        if slot.is_booked:
            raise serializers.ValidationError("This slot has been booked. Please choose another slot.")
        return data

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["patient"] = request.user

        slot = validated_data["slot"]
        slot.is_booked = True
        slot.save()

        return Appointment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        new_slot = validated_data.get("slot", instance.slot)

        if new_slot != instance.slot:
            old_slot = instance.slot
            old_slot.is_booked = False
            old_slot.save()

            new_slot.is_booked = True
            new_slot.save()

            instance.slot = new_slot

        instance.save()
        return instance



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", "")
        )
        user.set_password(password)
        user.save()

        PatientProfile.objects.create(user=user)
        return user