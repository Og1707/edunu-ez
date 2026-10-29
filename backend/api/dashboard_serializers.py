from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    rol = serializers.ChoiceField(choices=('administrador', 'profesor'))
    kpis = serializers.DictField(child=serializers.JSONField())
    cursos = serializers.ListField(child=serializers.DictField(child=serializers.JSONField()))
    estudiantes = serializers.ListField(child=serializers.DictField(child=serializers.JSONField()))
    asignaturas = serializers.ListField(child=serializers.DictField(child=serializers.JSONField()))
    actividades = serializers.ListField(child=serializers.DictField(child=serializers.JSONField()))


class DashboardSubjectKpiSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    promedio = serializers.FloatField(allow_null=True)
    total_actividades = serializers.IntegerField()
    actividades_completadas = serializers.IntegerField()


class DashboardStudentDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    nombre_completo = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField()
    cursos = serializers.ListField(child=serializers.CharField())
    promedio = serializers.FloatField(allow_null=True)
    materias = DashboardSubjectKpiSerializer(many=True, default=list)
    historial = serializers.ListField(child=serializers.DictField(child=serializers.JSONField()))
