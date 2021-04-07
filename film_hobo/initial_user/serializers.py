from rest_framework import serializers
from .models import Designation, InitialIntrestedUsers


class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation

        fields = ('pk', 'title')
        read_only_fields = ('pk', 'title')


class InitialIntrestedUsersSerializer(serializers.ModelSerializer):
    designation = DesignationSerializer(read_only=True, many=True)
    designation_id = serializers.PrimaryKeyRelatedField(
        queryset=Designation.objects.all(),
        write_only=True, many=True)

    class Meta:
        model = InitialIntrestedUsers
        fields = ('pk', 'first_name', 'middle_name', 'last_name',
                  'email', 'phone', 'designation', 'designation_id')
        read_only_fields = ('pk',)

    def create(self, validated_data):
        validated_data.pop('user')
        designation = validated_data.pop('designation_id')
        initial_intrested_users = InitialIntrestedUsers.objects.create(
            **validated_data)
        for item in designation:
            initial_intrested_users.designation.add(item)
        return initial_intrested_users
