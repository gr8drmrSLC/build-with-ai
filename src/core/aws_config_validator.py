"""
aws_config_validator.py — validate AWS credentials and permissions at startup.

Call validate_aws_config() once at startup in any project that uses AWS.
Fails fast with a clear message rather than producing a cryptic boto3 error
mid-run when the first real AWS call is made.

Usage:
    from core.aws_config_validator import validate_aws_config, AWSConfigError

    try:
        validate_aws_config(required_services=["s3", "ec2"])
    except AWSConfigError as e:
        logger.critical("AWS config invalid — cannot start", extra={"reason": str(e)})
        sys.exit(1)
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Services this validator knows how to probe.
# Each entry maps service name -> (probe function, what it checks).
_PROBES: dict[str, tuple[str, str]] = {
    "s3":           ("list_buckets",        "S3 ListBuckets"),
    "ec2":          ("describe_regions",    "EC2 DescribeRegions"),
    "ssm":          ("describe_parameters", "SSM DescribeParameters"),
    "secretsmanager": ("list_secrets",      "SecretsManager ListSecrets"),
    "cloudwatch":   ("describe_alarms",     "CloudWatch DescribeAlarms"),
}


class AWSConfigError(Exception):
    """Raised when AWS credentials or permissions are invalid."""


def validate_aws_config(
    required_services: list[str] | None = None,
    region: str | None = None,
) -> dict[str, str]:
    """
    Validate AWS credentials, region, and basic service access.

    Checks in order:
    1. boto3 is importable (optional dependency — only required for AWS projects)
    2. Credentials resolve (any valid source: env, ~/.aws/credentials, instance role)
    3. Resolved identity is logged (account ID + ARN for audit trail)
    4. Each requested service can be called with a read-only probe

    Args:
        required_services: List of AWS service names to probe (e.g. ["s3", "ec2"]).
                           Use None to skip service probes and only validate credentials.
        region: Override AWS region. Defaults to settings.aws_region.

    Returns:
        Dict with 'account_id', 'arn', 'region' of the resolved identity.

    Raises:
        AWSConfigError: If any check fails, with a message describing the specific failure.
    """
    # --- 1. boto3 availability ---
    try:
        import boto3
        import botocore.exceptions
    except ImportError:
        raise AWSConfigError(
            "boto3 is not installed. Add it to your dependencies: "
            "pip install boto3  or  add 'boto3>=1.34' to pyproject.toml [project.optional-dependencies.aws]"
        )

    # --- 2. Region ---
    from core.config import settings  # noqa: PLC0415

    resolved_region = region or settings.aws_region

    # --- 3. Credentials + identity ---
    try:
        sts = boto3.client("sts", region_name=resolved_region)
        identity = sts.get_caller_identity()
    except botocore.exceptions.NoCredentialsError:
        raise AWSConfigError(
            "No AWS credentials found. Set AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY "
            "in .env, or configure ~/.aws/credentials, or attach an IAM instance role."
        )
    except botocore.exceptions.ClientError as e:
        code = e.response["Error"]["Code"]
        raise AWSConfigError(
            f"AWS credentials present but STS call failed ({code}). "
            "Check that the key is active and has sts:GetCallerIdentity permission."
        )
    except Exception as e:
        raise AWSConfigError(f"Unexpected error during STS identity check: {e}") from e

    account_id = identity["Account"]
    arn = identity["Arn"]

    logger.info(
        "AWS identity resolved",
        extra={"account_id": account_id, "arn": arn, "region": resolved_region},
    )

    # --- 4. Service probes ---
    if required_services:
        for service in required_services:
            _probe_service(service, resolved_region, boto3, botocore.exceptions)

    return {"account_id": account_id, "arn": arn, "region": resolved_region}


def _probe_service(
    service: str,
    region: str,
    boto3,       # type: ignore[type-arg]
    botocore_exc,  # type: ignore[type-arg]
) -> None:
    """Call a read-only API on the given service to confirm access."""
    if service not in _PROBES:
        logger.warning(
            "No probe defined for service '%s' — skipping permission check. "
            "Add an entry to _PROBES in aws_config_validator.py.",
            service,
        )
        return

    method_name, description = _PROBES[service]

    try:
        client = boto3.client(service, region_name=region)
        # Call with no arguments — all probes use list/describe calls that
        # return results (possibly empty) without requiring specific resource IDs
        getattr(client, method_name)()
        logger.debug("AWS service probe passed", extra={"service": service})
    except botocore_exc.ClientError as e:
        code = e.response["Error"]["Code"]
        if code in {"AccessDenied", "UnauthorizedOperation", "AuthFailure"}:
            raise AWSConfigError(
                f"Permission denied on {description}. "
                f"The IAM identity does not have {service}:{method_name} permission. "
                f"Add it to the IAM policy or use a role that includes it."
            )
        # Other client errors (e.g. endpoint not available in region) — warn, don't fail
        logger.warning(
            "AWS service probe returned non-auth error — treating as warning",
            extra={"service": service, "error_code": code},
        )
    except Exception as e:
        raise AWSConfigError(
            f"Unexpected error probing {service}: {e}"
        ) from e
