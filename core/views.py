import os
import pdfplumber
import docx
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from .models import (
    Condominium, Visitor, Reservation, Apartment,
    Vehicle, Finance, Order, Visit, Resident, Notice, Communication, Occurrence
)

from .serializers import (
    VisitorSerializer, ReservationSerializer, ApartmentSerializer,
    VehicleSerializer, FinanceSerializer, OrderSerializer, VisitSerializer,
    CondominiumSerializer, ResidentSerializer,
    NoticeSerializer, CommunicationSerializer, OccurrenceSerializer
)
from .filters import (
    ApartmentFilter, VehicleFilter, FinanceFilter,
    ReservationFilter, VisitorFilter, OrderFilter, CondominiumFilter, VisitFilter,
    queryset_filter_condominium, queryset_filter_apartment, queryset_filter_vehicle, queryset_filter_visitor,
    queryset_filter_visit, queryset_filter_reservation, queryset_filter_resident, queryset_filter_finance,
    queryset_filter_order, queryset_filter_notice, queryset_filter_communication, queryset_filter_occurrence,
    NoticeFilter, ResidentFilter, CommunicationFilter, OccurrenceFilter
)
from core.services_ia import summarize_text

logger = logging.getLogger(__name__)

class VisitorViewSet(viewsets.ModelViewSet):
    serializer_class = VisitorSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filterset_class = VisitorFilter
    search_fields = ('name', 'cpf')
    ordering_fields = ('name', 'cpf')

    def get_queryset(self):
        user = self.request.user
        query_base = Visitor.objects.select_related('condominium', 'registered_by')
        return queryset_filter_visitor(query_base, user)


class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filterset_class = ReservationFilter
    search_fields = ('space',)
    ordering_fields = ('start_time', 'end_time')

    def get_queryset(self):
        user = self.request.user
        query_base = Reservation.objects.select_related('resident__apartment')
        return queryset_filter_reservation(query_base, user)


class ApartmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = ApartmentSerializer
    filterset_class = ApartmentFilter
    search_fields = ('number', 'block')
    ordering_fields = ('number', 'block', 'tread')

    def get_queryset(self):
        user = self.request.user
        query_base = Apartment.objects.select_related('condominium')
        return queryset_filter_apartment(query_base, user)

class ResidentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = ResidentSerializer
    filterset_class = ResidentFilter
    search_fields = ('registered_by__name',)

    def get_queryset(self):
        user = self.request.user
        query_base = Resident.objects.select_related('registered_by', 'apartment')
        return queryset_filter_resident(query_base, user)

class VisitViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = VisitSerializer
    filterset_class = VisitFilter
    search_fields = ('visitor__name',)
    ordering_fields = ('entry_date',)

    def get_queryset(self):
        user = self.request.user
        query_base = Visit.objects.select_related('visitor', 'apartment', 'registered_by')
        return queryset_filter_visit(query_base, user)

class VehicleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = VehicleSerializer
    filterset_class = VehicleFilter
    search_fields = ('plate', 'model')
    ordering_fields = ('plate', 'model')

    def get_queryset(self):
        user = self.request.user
        query_base = Vehicle.objects.select_related('owner', 'condominium', 'registered_by')
        return queryset_filter_vehicle(query_base, user)

class FinanceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = FinanceSerializer
    filterset_class = FinanceFilter
    search_fields = ('description',)
    ordering_fields = ('date',)

    def get_queryset(self):
        user = self.request.user
        query_base = Finance.objects.select_related('creator', 'condominium')
        return queryset_filter_finance(query_base, user)


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = OrderSerializer
    filterset_class = OrderFilter
    search_fields = ('order_code',)
    ordering_fields = ('order_date',)

    def get_queryset(self):
        user = self.request.user
        query_base = Order.objects.select_related('owner', 'registered_by')
        return queryset_filter_order(query_base, user)


# Adicionei um ViewSet para Condominium
class CondominiumViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = CondominiumSerializer
    filterset_class = CondominiumFilter
    search_fields = ('name', 'cnpj')
    ordering_fields = ('name',)


    def get_queryset(self):
        user = self.request.user
        query_base = Condominium.objects.all()
        return queryset_filter_condominium(query_base, user)


class NoticeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = NoticeSerializer
    filterset_class = NoticeFilter
    search_fields = ('title',)
    ordering_fields = ('created_at',)

    def get_queryset(self):
        user = self.request.user
        query_base = Notice.objects.select_related('author', 'condominium')
        return queryset_filter_notice(query_base, user)

    @action(detail=True, methods=['get'], url_path='summarize')
    def summarize(self, request, pk=None):
        notice = self.get_object()
        text_content = ""

        # Prioriza o arquivo complementar, se existir
        if notice.file_complement and hasattr(notice.file_complement, 'path'):
            file_path = notice.file_complement.path
            logger.info(f"Tentando processar o arquivo do caminho: {file_path}")

            # DEBUG: Verificar se o arquivo existe no sistema de arquivos do contêiner
            if not os.path.exists(file_path):
                logger.error(f"FALHA: O arquivo '{file_path}' não foi encontrado no sistema de arquivos do contêiner.")
                return Response(
                    {
                        "error": f"Erro interno: arquivo complementar '{notice.file_complement.name}' não encontrado no servidor."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            logger.info(f"SUCESSO: Arquivo '{file_path}' encontrado. Processando...")
            file_extension = os.path.splitext(file_path)[1].lower()

            try:
                if file_extension == '.pdf':
                    with pdfplumber.open(file_path) as pdf:
                        pages = [page.extract_text() for page in pdf.pages if page.extract_text()]
                        text_content = "\n".join(pages)
                elif file_extension == '.docx':
                    doc = docx.Document(file_path)
                    paragraphs = [p.text for p in doc.paragraphs if p.text]
                    text_content = "\n".join(paragraphs)
                else:
                    # Se não for PDF ou DOCX, usa o conteúdo do aviso como fallback
                    text_content = notice.content
            except FileNotFoundError:
                logger.error(f"Erro de FileNotFoundError ao tentar abrir '{file_path}'.")
                return Response(
                    {"error": "Erro ao abrir o arquivo complementar, pois ele não foi encontrado."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except Exception as e:
                logger.error(f"Erro inesperado ao processar o arquivo '{file_path}': {str(e)}")
                return Response(
                    {"error": f"Erro ao processar o arquivo: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            text_content = notice.content

        if not text_content:
            return Response(
                {"error": "Nenhum conteúdo disponível para resumir."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Usa o serviço de sumarização
        summary = summarize_text(text_content)

        if not summary:
            return Response(
                {"error": "Não foi possível gerar o resumo. Verifique os logs do servidor para mais detalhes."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({"summary": summary})

class OccurrenceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = OccurrenceSerializer
    filterset_class = OccurrenceFilter
    search_fields = ('description',)
    ordering_fields = ('date_reported',)

    def get_queryset(self):
        user = self.request.user
        query_base = Occurrence.objects.select_related('reported_by', 'condominium')
        return queryset_filter_occurrence(query_base, user)


class CommunicationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = CommunicationSerializer
    filterset_class = CommunicationFilter
    search_fields = ('sender', 'recipients__name')

    def get_queryset(self):
        user = self.request.user
        query_base = Communication.objects.select_related('sender', 'condominium').prefetch_related('recipients')
        return queryset_filter_communication(query_base, user)

def home(request):
    from django.shortcuts import render
    return render(request, 'pages/home.html', {})