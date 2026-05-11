from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.schemas.provider_schema import ProviderStatus

from app.schemas.provider_common import (
    NormalizedCallbackEvent,
    NormalizedStatusResult,
    NormalizedSubmitResult,
)


class BaseVideoProviderAdapter(ABC):
    """
    Interface chuẩn cho mọi video provider adapter.

    Mục tiêu:
    - ép toàn bộ provider trả về cùng một normalized contract
    - giữ provider_router.py, dispatch/poll services, callback route
      không phụ thuộc vào provider-specific response shapes
    """

    provider_name: str

    @abstractmethod
    async def submit(
        self,
        scene_payload: dict,
        callback_url: str | None,
    ) -> NormalizedSubmitResult:
        """
        Submit một scene sang provider.

        Input:
        - scene_payload: payload đã được dispatch service normalize
        - callback_url: URL webhook/callback backend muốn provider gọi về

        Output:
        - NormalizedSubmitResult
        """
        raise NotImplementedError

    @abstractmethod
    async def query(
        self,
        *,
        provider_task_id: str | None,
        provider_operation_name: str | None,
    ) -> NormalizedStatusResult:
        """
        Query/poll trạng thái scene từ provider.

        Quy ước:
        - Veo thường dùng provider_operation_name

        Output:
        - NormalizedStatusResult
        """
        raise NotImplementedError

    @abstractmethod
    def verify_callback(
        self,
        headers: dict[str, str],
        raw_body: bytes,
    ) -> bool:
        """
        Verify callback signature / authenticity.

        Return:
        - True nếu callback hợp lệ
        - False nếu callback không hợp lệ
        """
        raise NotImplementedError

    @abstractmethod
    def normalize_callback(
        self,
        headers: dict[str, str],
        payload: dict,
    ) -> NormalizedCallbackEvent:
        """
        Chuẩn hóa callback payload từ provider về contract thống nhất.

        Output:
        - NormalizedCallbackEvent
        """
        raise NotImplementedError


class ProviderAdapter(ABC):
    """Backward-compatible adapter interface used by provider lab APIs."""

    provider_name: str

    @abstractmethod
    def status(self) -> ProviderStatus:
        raise NotImplementedError

    @abstractmethod
    def build_payload(self, operation: str, input_data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def payload_preview(self, operation: str, input_data: dict[str, Any], dry_run: bool = True):
        payload = self.build_payload(operation, input_data)
        from app.schemas.provider_schema import ProviderPayloadPreview

        return ProviderPayloadPreview(
            provider=self.provider_name,
            operation=operation,
            payload=payload,
            dry_run=dry_run,
        )

    def build_execution_result(
        self,
        *,
        operation: str,
        dry_run: bool,
        payload: dict[str, Any],
        accepted: bool = True,
        result: dict[str, Any] | None = None,
        message: str = "Simulated execution",
        external_job_id: str | None = None,
    ):
        from app.schemas.provider_schema import ProviderExecutionResult

        return ProviderExecutionResult(
            provider=self.provider_name,
            operation=operation,
            dry_run=dry_run,
            accepted=accepted,
            external_job_id=external_job_id,
            payload=payload,
            result=result or {},
            message=message,
        )

    def execute(self, operation: str, input_data: dict[str, Any], dry_run: bool = True):
        import warnings  # noqa: PLC0415
        warnings.warn(
            "ProviderAdapter.execute() with dry_run=True is deprecated. "
            "Use BaseVideoProviderAdapter (async) for real provider execution. "
            "Planned removal: Q4/2026.",
            DeprecationWarning,
            stacklevel=2,
        )
        if not dry_run:
            raise NotImplementedError(
                f"{self.__class__.__name__} does not implement real execution. "
                "Override execute() with provider-specific HTTP call logic, or "
                "use the proper publish/render workflow for real operations."
            )
        payload = self.build_payload(operation, input_data)
        return self.build_execution_result(
            operation=operation,
            dry_run=dry_run,
            payload=payload,
            accepted=True,
            result={},
            message="Simulated execution",
        )

    def handle_callback(self, payload: dict[str, Any], headers: dict[str, Any]):
        from app.schemas.provider_schema import ProviderCallbackResult

        return ProviderCallbackResult(
            provider=self.provider_name,
            accepted=True,
            payload={"payload": payload, "headers": headers},
            message="Callback accepted",
        )