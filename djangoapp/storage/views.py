from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
import json

from .models import Node, Connection


def dfs_nodes(node: Node, lengths: dict, length, visited: set):
    visited.add(node.name)
    if node.type != 'operator':
        lengths[node.name] = [node, length]

    for i in node.node_from.all():
        if i.node_to.name not in visited:
            next_node = i.node_to
            dfs_nodes(next_node, lengths, length + i.distance, visited)
    for i in node.node_to.all():
        if i.node_from.name not in visited:
            next_node = i.node_from
            dfs_nodes(next_node, lengths, length + i.distance, visited)


class MoveWastesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        operator_name = request.GET.get("operator_name", None)

        if operator_name:
            try:
                operators = Node.objects.filter(name=operator_name, type='operator')
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            operators = Node.objects.filter(type='operator')

        statuses = []
        operator: Node
        for operator in operators:
            lengths = {}
            dfs_nodes(operator, lengths, 0, set())
            nodes = list(lengths.keys())
            nodes.sort(key=lambda x: lengths[x][1])
            for j in nodes:
                if (operator.glass_current_occupancy == 0 and
                    operator.plastic_current_occupancy == 0 and
                    operator.biowastes_total_capacity == 0):
                    break
                storage: Node = lengths[j][0]
                glass_diff = min(
                    operator.glass_current_occupancy,
                    (storage.glass_total_capacity -
                     storage.glass_current_occupancy)
                )
                plastic_diff = min(
                    operator.plastic_current_occupancy,
                    (storage.plastic_total_capacity -
                     storage.plastic_current_occupancy)
                )
                biowastes_diff = min(
                    operator.biowastes_current_occupancy,
                    (storage.biowastes_total_capacity -
                     storage.biowastes_current_occupancy)
                )
                try:
                    with transaction.atomic():
                        storage.glass_current_occupancy += glass_diff
                        storage.plastic_current_occupancy += plastic_diff
                        storage.biowastes_current_occupancy += biowastes_diff
                        storage.save()
                        operator.glass_current_occupancy -= glass_diff
                        operator.plastic_current_occupancy -= plastic_diff
                        operator.biowastes_current_occupancy -= biowastes_diff
                        operator.save()
                except Exception:
                    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            operator_status = {
                'glass': f'{operator.glass_current_occupancy}/{operator.glass_total_capacity}',
                'plastic': f'{operator.plastic_current_occupancy}/{operator.plastic_total_capacity}',
                'biowastes': f'{operator.biowastes_current_occupancy}/{operator.biowastes_total_capacity}'
            }
            statuses.append(operator_status)

        return Response(statuses, status=status.HTTP_200_OK)



class CreateNodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        name = json.loads(request.body).get("name", None)
        node_type = json.loads(request.body).get("type", None)
        connections = json.loads(request.body).get('connections', [])
        glass_capacity = json.loads(request.body).get('glass_capacity', 0)
        plastic_capacity = json.loads(request.body).get('plastic_capacity', 0)
        biowastes_capacity = json.loads(request.body).get('biowastes_capacity', 0)

        capacity_given = any([glass_capacity, plastic_capacity, biowastes_capacity])
        is_correct = all([glass_capacity >= 0, plastic_capacity >= 0, biowastes_capacity >= 0])

        if name and node_type and capacity_given and is_correct:
            if not all([glass_capacity >= 0, plastic_capacity >= 0, biowastes_capacity >= 0]):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            try:
                with transaction.atomic():
                    node = Node.objects.create(
                        name=name,
                        type=node_type,
                        glass_total_capacity=glass_capacity,
                        plastic_total_capacity=plastic_capacity,
                        biowastes_total_capacity=biowastes_capacity
                    )
                    for i in connections:
                        if type(i) != list and len(i) != 2 or i[0] == node.name:
                            transaction.set_rollback(True)
                            return Response(status=status.HTTP_400_BAD_REQUEST)
                        node_to = Node.objects.get(name=i[0])
                        Connection.objects.create(
                            node_from=node,
                            node_to=node_to,
                            distance=int(i[1])
                        )
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            except ValidationError:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            except IntegrityError:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class GetOccupancyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        name = request.GET.get('name', None)
        if name:
            try:
                node = Node.objects.get(name=name)
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            return Response(
                {
                    'glass': f'{node.glass_current_occupancy}/{node.glass_total_capacity}',
                    'plastic': f'{node.plastic_current_occupancy}/{node.plastic_total_capacity}',
                    'biowastes': f'{node.biowastes_current_occupancy}/{node.biowastes_total_capacity}'
                },
                status=status.HTTP_200_OK
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)


def dfs(node: Node, length, name, visited):
    if node.name == name:
        return length
    for i in node.node_from.all():
        if i.node_to.name not in visited:
            next_node = i.node_to
            visited.add(next_node.name)
            result = dfs(next_node, length + i.distance, name, visited)
            if result:
                return result
    for i in node.node_to.all():
        if i.node_from.name not in visited:
            next_node = i.node_from
            visited.add(next_node.name)
            result = dfs(next_node, length + i.distance, name, visited)
            if result:
                return result


class GetDistanceView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        node1_name = request.GET.get("from", None)
        node2_name = request.GET.get("to", None)

        if node1_name and node2_name:
            try:
                node1 = Node.objects.get(name=node1_name)
                node2 = Node.objects.get(name=node2_name)
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            distance = dfs(node1, 0, node2.name, set())
            if distance:
                return Response(
                    {'distance': distance},
                    status=status.HTTP_200_OK
                )
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class GenerateWastesView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        operator_name = json.loads(request.body).get('operator', None)
        glass = json.loads(request.body).get('glass', 0)
        plastic = json.loads(request.body).get('plastic', 0)
        biowastes = json.loads(request.body).get('biowastes', 0)

        is_not_empty = any([glass, plastic, biowastes])
        try:
            is_correct = all([glass >= 0, plastic >= 0, biowastes >= 0])
        except TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if operator_name and is_not_empty and is_correct:
            try:
                operator = Node.objects.get(name=operator_name, type='operator')
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            try:
                operator.glass_current_occupancy -= glass
                operator.plastic_current_occupancy -= plastic
                operator.biowastes_current_occupancy -= biowastes
                operator.save()
            except ValidationError:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
