from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    rol = serializers.ChoiceField(choices=('administrador', 'profesor'))
    kpis = serializers.DictField(child=serializers.JSONField())
    cursos = serializers.ListField(child=serializers.DictField(child=serializers.JSONField()))
    estudiantes = serializers.ListField(child=serializers.DictField(child=serializers.JSONField()))
    asignaturas = serializers.ListField(child=serializers.DictField(child=serializers.JSONField()))
    actividades = serializers.ListField(child=serializers.DictField(child=serializers.JSONField()))


class DashboardStudentDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    username = serializers.CharField()
    cursos = serializers.ListField(child=serializers.CharField())
    promedio = serializers.FloatField(allow_null=True)
    historial = serializers.ListField(child=serializers.DictField(child=serializers.JSONField()))
