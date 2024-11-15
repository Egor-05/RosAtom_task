from django.template.context_processors import request
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Node, Connection

class NodeCreationTests(APITestCase):
    def test_create_node_correct_data(self):
        url = reverse('node_creation')
        Node.objects.create(name='storage1', type='storage', glass_total_capacity=30)
        data = {
            "name": "storage2",
            "type": "storage",
            "glass_capacity": 30,
            "connections": [['storage1', 30]]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Node.objects.count(), 2)

    def test_create_node_nonexistent_connections(self):
        url = reverse('node_creation')
        data = {
            "name": "storage1",
            "type": "storage",
            "glass_capacity": 30,
            "connections": [['storage2', 30]]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Node.objects.count(), 0)

    def test_create_node_self_connections(self):
        url = reverse('node_creation')
        data = {
            "name": "storage1",
            "type": "storage",
            "glass_capacity": 30,
            "connections": [['storage1', 30]]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Node.objects.count(), 0)

    def test_create_node_wrong_connections_format(self):
        url = reverse('node_creation')
        data = {
            "name": "storage1",
            "type": "storage",
            "glass_capacity": 30,
            "connections": ['storage2']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Node.objects.count(), 0)

    def test_create_existing_node_name(self):
        url = reverse('node_creation')
        Node.objects.create(name='storage1', type='storage', glass_total_capacity=30)
        data = {
            "name": "storage1",
            "type": "storage",
            "glass_capacity": 30,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Node.objects.count(), 1)

    def test_create_wrong_type(self):
        url = reverse('node_creation')
        data = {
            "name": "storage1",
            "type": "storage1",
            "glass_capacity": 30,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Node.objects.count(), 0)

    def test_create_wrong_num_format(self):
        url = reverse('node_creation')
        data = {
            "name": "storage1",
            "type": "storage1",
            "glass_capacity": -1,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Node.objects.count(), 0)


class FindDistanceTests(APITestCase):
    def test_get_distance_correct_request(self):
        url = reverse('get_distance')
        url += f'?from=storage1&to=storage2'
        node1 = Node.objects.create(name='storage1', type='operator', glass_total_capacity=30)
        node2 = Node.objects.create(name='storage2', type='storage', glass_total_capacity=30)
        Connection.objects.create(node_from=node1, node_to=node2, distance=10)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['distance'], 10)

    def test_get_distance_correct_request_long_path(self):
        url = reverse('get_distance')
        url += f'?from=storage3&to=storage1'
        node1 = Node.objects.create(name='storage1', type='operator', glass_total_capacity=30)
        node2 = Node.objects.create(name='storage2', type='storage', glass_total_capacity=30)
        node3 = Node.objects.create(name='storage3', type='storage', glass_total_capacity=30)
        Connection.objects.create(node_from=node1, node_to=node2, distance=10)
        Connection.objects.create(node_from=node2, node_to=node3, distance=10)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['distance'], 20)

    def test_get_distance_no_path_between_nodes(self):
        url = reverse('get_distance')
        url += f'?from=storage1&to=storage2'
        node1 = Node.objects.create(name='storage1', type='operator', glass_total_capacity=30)
        node2 = Node.objects.create(name='storage2', type='storage', glass_total_capacity=30)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_distance_not_enough_parameters(self):
        url = reverse('get_distance')
        url += f'?from=storage1'
        node1 = Node.objects.create(name='storage1', type='operator', glass_total_capacity=30)
        node2 = Node.objects.create(name='storage2', type='storage', glass_total_capacity=30)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GetNodeDataTests(APITestCase):
    def test_get_node_data_correct_request(self):
        url = reverse('get_occupancy')
        url += f'?name=storage'
        Node.objects.create(name='storage', type='operator', glass_total_capacity=30, glass_current_occupancy=20)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['glass'], '20.0/30.0')
        self.assertEqual(response.json()['plastic'], '0.0/0.0')
        self.assertEqual(response.json()['biowastes'], '0.0/0.0')

    def test_get_node_data_nonexistent_node(self):
        url = reverse('get_occupancy')
        url += f'?name=storage1'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_node_data_wrong_request(self):
        url = reverse('get_occupancy')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class WasteSetTests(APITestCase):
    def test_set_wastes_correct_data(self):
        url = reverse('set_wastes')
        node = Node.objects.create(name='storage1', type='operator', glass_total_capacity=30)
        data = {
            "name": "storage1",
            "glass": 30
        }

        response = self.client.post(url, data, format='json')
        print(node.glass_current_occupancy)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_set_wastes_incorrect_data(self):
        url = reverse('set_wastes')
        node = Node.objects.create(name='storage1', type='operator', glass_total_capacity=30)
        data = {
            "glass": 30
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_wastes_correct_data_negative_value(self):
        url = reverse('set_wastes')
        node = Node.objects.create(name='storage3', type='storage', glass_total_capacity=30, glass_current_occupancy=30)
        data = {
            "name": "storage3",
            "glass": -15,
            '123': 1
        }
        response = self.client.post(url, data, format='json')
        print(node.glass_current_occupancy)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_set_wastes_nonexistent_node(self):
        url = reverse('set_wastes')
        node = Node.objects.create(name='storage1', type='operator', glass_total_capacity=30)
        data = {
            "name": "storage",
            "glass": 30
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class WastesMovingTests(APITestCase):
    def test_move_wastes_correct_information(self):
        url = reverse('move_wastes')
        operator_node = Node.objects.create(
            name='operator1',
            type='operator',
            glass_total_capacity=30,
            glass_current_occupancy=30
        )
        storage_node = Node.objects.create(name='storage1', type='storage', glass_total_capacity=30)
        Connection.objects.create(node_from=operator_node, node_to=storage_node, distance=10)
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()[0]['glass'], '0.0/30.0')

    def test_move_wastes_nonexistent_node(self):
        url = reverse('move_wastes')
        operator_node = Node.objects.create(
            name='operator1',
            type='operator',
            glass_total_capacity=30,
            glass_current_occupancy=30
        )
        storage_node = Node.objects.create(name='storage1', type='storage', glass_total_capacity=30)
        Connection.objects.create(node_from=operator_node, node_to=storage_node, distance=10)
        data = {'operator_name': '123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
