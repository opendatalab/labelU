from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from labelu.version import version as labelu_version

class ContentTypeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # add LabelU-Version header
        response.headers["LabelU-Version"] = labelu_version
        
        # set content-type for javascript files
        if request.url.path.endswith(".js"):
            response.headers["content-type"] = "application/javascript"
            
        return response