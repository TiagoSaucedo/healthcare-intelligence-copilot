
import requests

from app.config import settings


class APIClientError(Exception):
    """Erro de comunicação com a API."""


class HealthcareAPIClient:
    """Cliente HTTP para comunicação com a API do Healthcare Intelligence Copilot."""

    def __init__(self, base_url: str | None = None, timeout: int = 600):
        self.base_url = (base_url or settings.api_base_url).rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _get(self, endpoint: str, params: dict | None = None):
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout as exc:
            raise APIClientError(
                "A API demorou muito para responder."
            ) from exc

        except requests.exceptions.ConnectionError as exc:
            raise APIClientError(
                "Não foi possível conectar à API. Verifique se o servidor está ativo."
            ) from exc

        except requests.exceptions.HTTPError as exc:
            status_code = exc.response.status_code
            raise APIClientError(
                f"A API retornou um erro HTTP {status_code}."
            ) from exc

        except requests.exceptions.RequestException as exc:
            raise APIClientError(
                "Ocorreu um erro ao consultar a API."
            ) from exc

        except ValueError as exc:
            raise APIClientError(
                "A API retornou uma resposta JSON inválida."
            ) from exc

    def get_health(self):
        return self._get("/health")

    def get_financial_summary(
        self,
        start_month: str,
        end_month: str,
    ):
        return self._get(
            "/api/v1/analytics/financial/summary",
            {
                "start_month": start_month,
                "end_month": end_month,
            },
        )

    def get_financial_monthly(
        self,
        start_month: str,
        end_month: str,
    ):
        return self._get(
            "/api/v1/analytics/financial/monthly",
            {
                "start_month": start_month,
                "end_month": end_month,
            },
        )

    def get_provider_summary(
        self,
        start_month: str,
        end_month: str,
    ):
        return self._get(
            "/api/v1/analytics/providers/summary",
            {
                "start_month": start_month,
                "end_month": end_month,
            },
        )
    

    def get_provider_monthly(
        self,
        start_month: str,
        end_month: str,
    ):
        return self._get(
            "/api/v1/analytics/providers/monthly",
            {
                "start_month": start_month,
                "end_month": end_month,
            },
        )

    def get_paid_provider_summary(
        self,
        start_month: str,
        end_month: str,
    ):
        return self._get(
            "/api/v1/analytics/providers/paid/summary",
            {
                "start_month": start_month,
                "end_month": end_month,
            },
        )

    def get_paid_provider_monthly(
        self,
        start_month: str,
        end_month: str,
    ):
        return self._get(
            "/api/v1/analytics/providers/paid/monthly",
            {
                "start_month": start_month,
                "end_month": end_month,
            },
        )

    def get_procedure_summary(
        self,
        start_month: str,
        end_month: str,
    ):
        return self._get(
            "/api/v1/analytics/procedures/summary",
            {
                "start_month": start_month,
                "end_month": end_month,
            },
        )

    def get_contract_summary(
        self,
        start_month: str,
        end_month: str,
    ):
        return self._get(
            "/api/v1/analytics/contracts/summary",
            {
                "start_month": start_month,
                "end_month": end_month,
            },
        )


    def get_procedure_monthly(
        self,
        start_month: str,
        end_month: str,
    ):
        return self._get(
            "/api/v1/analytics/procedures/monthly",
            {
                "start_month": start_month,
                "end_month": end_month,
            },
        )

    def get_contract_monthly(
        self,
        start_month: str,
        end_month: str,
    ):
        return self._get(
            "/api/v1/analytics/contracts/monthly",
            {
                "start_month": start_month,
                "end_month": end_month,
            },
        )

    def get_ranking(
        self,
        dimension: str,
        start_month: str,
        end_month: str,
        limit: int = 10,
        metric: str = "apresentada",
    ):
        return self._get(
            "/api/v1/analytics/rankings",
            {
                "dimension": dimension,
                "start_month": start_month,
                "end_month": end_month,
                "limit": limit,
                "metric": metric,
            },
        )

    def get_ranking_summary(
        self,
        dimension: str,
        start_month: str,
        end_month: str,
        metric: str = "apresentada",
    ):
        return self._get(
            "/api/v1/analytics/rankings/summary",
            {
                "dimension": dimension,
                "start_month": start_month,
                "end_month": end_month,
                "metric": metric,
            },
        )

    def get_ranking_analysis(
        self,
        dimension: str,
        start_month: str,
        end_month: str,
        limit: int = 10,
        metric: str = "apresentada",
    ):
        return self._get(
            "/api/v1/analytics/rankings/analysis",
            {
                "dimension": dimension,
                "start_month": start_month,
                "end_month": end_month,
                "limit": limit,
                "metric": metric,
            },
        )

    def post_chat(self, message: str):
        url = f"{self.base_url}/api/v1/chat"

        try:
            response = self.session.post(
                url,
                json={"message": message},
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout as exc:
            raise APIClientError(
                "A API demorou muito para responder."
            ) from exc

        except requests.exceptions.ConnectionError as exc:
            raise APIClientError(
                "Não foi possível conectar à API. Verifique se o servidor está ativo."
            ) from exc

        except requests.exceptions.HTTPError as exc:
            status_code = exc.response.status_code
            raise APIClientError(
                f"A API retornou um erro HTTP {status_code}."
            ) from exc

        except requests.exceptions.RequestException as exc:
            raise APIClientError(
                "Ocorreu um erro ao enviar a mensagem."
            ) from exc

        except ValueError as exc:
            raise APIClientError(
                "A API retornou uma resposta JSON inválida."
            ) from exc

    def close(self):
        self.session.close()
