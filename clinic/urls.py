
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from clinic.views import DoctorViewSet, AppointmentSlotViewSet, AppointmentViewSet, LoginView, DoctorListView, \
    PatientViewSet, AppointmentSlotBulkSave, RegisterView

router = DefaultRouter()
router.register(r"manage/doctors", DoctorViewSet, basename="admin-doctors")
router.register(r"slots", AppointmentSlotViewSet)
router.register(r"appointments", AppointmentViewSet)
router.register(r"patients", PatientViewSet, basename="patients")

urlpatterns = [
    path("doctors/", DoctorListView.as_view(), name="doctor-list"),  # patient only
    path("", include(router.urls)),
    path("auth/register/", RegisterView.as_view(), name="auth_register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    # JWT 登录
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("manage/slots/bulk_save/", AppointmentSlotBulkSave.as_view()),
]