"""
API routes for the MCP Account Provisioning Server.
"""
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from models.account import ProvisioningRequest, ProvisioningResponse, BatchProvisioningRequest, BatchProvisioningResponse, ErrorResponse
from services.email_provisioning_service import provision_email_account
from services.git_provisioning_service import provision_git_account
from services.batch_provisioning_service import provision_batch_accounts
from utils.logging import logger, log_provisioning_event


def setup_routes(app: FastAPI) -> None:
    """
    Set up all API routes.

    Args:
        app (FastAPI): FastAPI application instance
    """

    @app.post("/provision/email",
              operation_id="provision_email",
              response_model=ProvisioningResponse,
              responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
              summary="Provision an email account",
              description="Creates an email account for an employee after validating their ID")
    async def provision_email(request: ProvisioningRequest):
        try:
            account = provision_email_account(request)
            log_provisioning_event(logger, "email_provisioning", request.name, "email", True)
            return ProvisioningResponse(username=account.username, password=account.password)
        except ValueError as e:
            log_provisioning_event(logger, "email_provisioning", request.name, "email", False, str(e))
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            log_provisioning_event(logger, "email_provisioning", request.name, "email", False, str(e))
            raise HTTPException(status_code=500, detail="Internal server error")

    @app.post("/provision/git",
              operation_id="provision_git",
              response_model=ProvisioningResponse,
              responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
              summary="Provision a git account",
              description="Creates a git account for an employee after validating their ID")
    async def provision_git(request: ProvisioningRequest):
        try:
            account = provision_git_account(request)
            log_provisioning_event(logger, "git_provisioning", request.name, "git", True)
            return ProvisioningResponse(username=account.username, password=account.password)
        except ValueError as e:
            log_provisioning_event(logger, "git_provisioning", request.name, "git", False, str(e))
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            log_provisioning_event(logger, "git_provisioning", request.name, "git", False, str(e))
            raise HTTPException(status_code=500, detail="Internal server error")

    @app.post("/provision/batch",
              response_model=BatchProvisioningResponse,
              responses={400: {"model": ErrorResponse}},
              summary="Provision multiple accounts",
              description="Creates multiple accounts for employees after validating their IDs")
    async def provision_batch(request: BatchProvisioningRequest):
        try:
            response = provision_batch_accounts(request)
            log_provisioning_event(logger, "batch_provisioning", f"{len(request.requests)} requests", "batch", True)
            return response
        except Exception as e:
            log_provisioning_event(logger, "batch_provisioning", f"{len(request.requests)} requests", "batch", False, str(e))
            raise HTTPException(status_code=500, detail="Internal server error")