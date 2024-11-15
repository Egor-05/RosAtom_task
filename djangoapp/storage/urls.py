from django.urls import path
from .views import (MoveWastesView, CreateNodeView, GetOccupancyView, GetDistanceView, SetWastesView)

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
        'set_wastes/',
        SetWastesView.as_view(),
        name='set_wastes'
    )
]