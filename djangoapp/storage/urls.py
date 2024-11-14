from django.urls import path
from .views import (MoveWastesView, CreateNodeView, GetOccupancyView, GetDistanceView, GenerateWastesView)

urlpatterns = [
    path(
        'move_wastes/',
        MoveWastesView.as_view(),
        name='move_wastes'
    ),
    path(
        'create_node/',
        CreateNodeView.as_view(),
        name='node_creation'
    ),
    path(
        'get_occupancy/',
        GetOccupancyView.as_view(),
        name='get_occupancy'
    ),
    path(
        'get_distance/',
        GetDistanceView.as_view(),
        name='get_distance'
    ),
    path(
        'generate_wastes/',
        GenerateWastesView.as_view(),
        name='generate_wastes'
    )
]