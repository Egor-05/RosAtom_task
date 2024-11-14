from django.urls import path
from .views import (MoveWastesView, CreateNodeView, GetOccupancyView, GetDistanceView)

urlpatterns = [
    path(
        'move_wastes/',
        MoveWastesView.as_view(),
        name='move_wastes'
    ),
    path(
        'create_node/',
        CreateNodeView.as_view(),
        name='create_node'
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
    )
]