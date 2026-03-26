from fastapi import APIRouter, Depends
from app.api import auth
from app.api.endpoints import quotations, users, products
from app.api.endpoints.trcloud import webhook      
from app.dependencies.auth import PermissionChecker

api_router = APIRouter()


api_router.include_router(
    auth.router, 
    tags=["Authentication"]
)

# 1. หมวดใบเสนอราคา
api_router.include_router(
    quotations.router, 
    prefix="/quotations", 
    tags=["Quotations"],
    dependencies=[Depends(PermissionChecker("view_quotation"))]
)

api_router.include_router(
    users.router, 
    prefix="/users", 
    tags=["User Management"],
    dependencies=[Depends(PermissionChecker("manage_users"))]
)

api_router.include_router(
    products.router, 
    prefix="/products", 
    tags=["Products"]
)

# 3. หมวดเชื่อมต่อ TRCloud (Webhook)
api_router.include_router(
    webhook.router, 
    prefix="/trcloud/webhooks", 
    tags=["TRCloud"]
)
