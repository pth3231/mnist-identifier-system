from fastapi import HTTPException, status, Request
import httpx
from typing import Optional, Any

async def make_request(
    method: str,
    url: str,
    request: Request,
    json_data: Optional[dict] = None,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    timeout: float = 15.0
) -> dict | HTTPException:
    """
    Generic HTTP request helper with pre-built validation.
    
    Args:
        method: HTTP method (get, post, put, patch, delete)
        url: Full URL to call
        request: FastAPI request object (for accessing app state)
        json_data: JSON body data (dict)
        params: URL query parameters
        headers: Additional headers to send
        timeout: Request timeout in seconds
    
    Returns:
        Response JSON dict, or raises HTTPException on error
    """
    client: httpx.AsyncClient = request.app.state.http_client
    
    try:
        kwargs = {
            "url": url,
            "params": params,
            "headers": headers,
            "timeout": timeout
        }
        if json_data is not None:
            kwargs["json"] = json_data
        
        response = await getattr(client, method)(**kwargs)
        response.raise_for_status()
        return response.json()
        
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Request to {url} timed out"
        )
        
    except httpx.HTTPStatusError as e:
        # Pass through the actual status code from auth service
        try:
            response_data = e.response.json() if e.response.text else {}
            # Extract detail if it exists, otherwise use full response
            detail = response_data.get("detail", response_data) if response_data else "HTTP error"
        except Exception:
            detail = e.response.text or "HTTP error"
        raise HTTPException(
            status_code=e.response.status_code,
            detail=detail
        )
        
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service at {url} is unavailable"
        )


# Convenience wrappers for common HTTP methods
async def get(url: str, request: Request, **kwargs) -> dict | HTTPException:
    return await make_request("get", url, request, **kwargs)

async def post(url: str, request: Request, json_data: Optional[dict] = None, **kwargs) -> dict | HTTPException:
    return await make_request("post", url, request, json_data=json_data, **kwargs)

async def put(url: str, request: Request, json_data: Optional[dict] = None, **kwargs) -> dict | HTTPException:
    return await make_request("put", url, request, json_data=json_data, **kwargs)

async def patch(url: str, request: Request, json_data: Optional[dict] = None, **kwargs) -> dict | HTTPException:
    return await make_request("patch", url, request, json_data=json_data, **kwargs)

async def delete(url: str, request: Request, **kwargs) -> dict | HTTPException:
    return await make_request("delete", url, request, **kwargs)