from rest_framework.routers import DefaultRouter
from api import views


# api endpoints
router = DefaultRouter(trailing_slash=False)
router.register(r'waypoints', views.WaypointViewSet, base_name='waypoints')
router.register(r'waypointmedia', views.WaypointMediaViewSet, base_name='waypointmedia')
router.register(r'tracks', views.RouteViewSet, base_name='tracks')
router.register(r'points', views.TrackPointViewSet, base_name='points')
router.register(r'user', views.GetUserViewSet, base_name='user')
router.register(r'routes', views.PublicRouteViewSet, base_name='routes')