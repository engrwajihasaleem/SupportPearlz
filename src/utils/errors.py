"""Translate common provider and application failures into safe user-facing messages."""
from __future__ import annotations


def friendly_error(exc: Exception, action: str = "complete this request") -> str:
    """Return actionable text without exposing stack traces or credentials."""
    name = type(exc).__name__.lower()
    message = str(exc).lower()

    if "authentication" in name or "invalid_api_key" in message or "incorrect api key" in message or "api key provided" in message:
        return "The OpenAI API key was rejected. Check that you copied the complete key from the correct OpenAI account, that it is active, and that it has not been revoked. Then enter it again."
    if "permission" in name or "insufficient_quota" in message or "billing" in message or "quota" in message:
        return "The API key was recognised, but the account/project does not currently have permission or available API quota. Check API billing, usage limits, project access, and model permissions in your OpenAI account."
    if "ratelimit" in name or "rate_limit" in message:
        return "The AI provider rate limit has been reached. Wait briefly and try again. If it continues, review your API usage limits."
    if "timeout" in name or "timeout" in message:
        return "The AI provider did not respond before the request timed out. Check your internet connection and retry."
    if "connection" in name or "connection" in message or "dns" in message:
        return "SupportPearlz could not connect to the AI provider. Check your internet connection, firewall, or proxy settings, then retry."
    if "notfound" in name or "model_not_found" in message:
        return "The configured AI model is unavailable to this API project. Check the model name and your project's model access."
    if "dimension" in message or "embedding" in message and "dimension" in message:
        return "The saved vector index is incompatible with the configured embedding model. An administrator must rebuild the knowledge index using the current embedding model."
    return f"SupportPearlz could not {action}. Please retry. If the problem continues, ask the administrator to review the application log."
