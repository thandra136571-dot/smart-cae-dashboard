import re
from collections import Counter


def get_error_recommendation(message):
    """Suggest possible causes and solutions for common log messages."""

    text = message.lower()

    if "database" in text or "connection failed" in text:
        return {
            "issue": "Database Connection Problem",
            "cause": (
                "The database server may be unavailable, "
                "or the connection settings may be incorrect."
            ),
            "solution": (
                "Check the database server status, connection settings, "
                "network connectivity, and application logs."
            )
        }

    elif "server unavailable" in text or "server down" in text:
        return {
            "issue": "Server Availability Problem",
            "cause": (
                "The server may be stopped, overloaded, "
                "or experiencing a service failure."
            ),
            "solution": (
                "Verify that the server is running, check its resource usage, "
                "and review the application logs."
            )
        }

    elif "storage" in text or "disk full" in text:
        return {
            "issue": "Storage Capacity Warning",
            "cause": (
                "The system may be running low on available disk space."
            ),
            "solution": (
                "Check disk usage and safely remove unnecessary temporary "
                "files or archive old logs according to your retention policy."
            )
        }

    elif "response time" in text or "timeout" in text:
        return {
            "issue": "Performance Problem",
            "cause": (
                "Requests may be taking too long because of slow operations, "
                "resource constraints, or unavailable dependencies."
            ),
            "solution": (
                "Investigate slow requests, check resource usage, "
                "and inspect the services the application depends on."
            )
        }

    elif "memory" in text or "out of memory" in text:
        return {
            "issue": "Memory Usage Problem",
            "cause": (
                "The application may be using more memory than is available."
            ),
            "solution": (
                "Monitor memory usage and investigate processes or operations "
                "that consume excessive memory."
            )
        }

    elif "permission denied" in text or "access denied" in text:
        return {
            "issue": "Permission Problem",
            "cause": (
                "The application may not have the required access permissions."
            ),
            "solution": (
                "Check the file, folder, or service permissions and grant "
                "only the access required by the application."
            )
        }

    elif "file not found" in text or "no such file" in text:
        return {
            "issue": "Missing File",
            "cause": (
                "The requested file may have been moved, renamed, "
                "or specified using an incorrect path."
            ),
            "solution": (
                "Verify the file path, filename, and file availability."
            )
        }

    else:
        return {
            "issue": "Unclassified Log Message",
            "cause": (
                "The message does not match a known rule in the "
                "recommendation engine."
            ),
            "solution": (
                "Review the original log entry and related messages "
                "to determine the underlying cause."
            )
        }


def analyze_logs(file_path):
    logs = []

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as file:

        for line in file:
            line = line.strip()

            if not line:
                continue

            match = re.search(
                r"\b(DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL|FATAL)\b",
                line,
                re.IGNORECASE
            )

            if match:
                level = match.group(1).upper()

                if level == "WARN":
                    level = "WARNING"
                elif level == "FATAL":
                    level = "CRITICAL"

                message = line[match.end():].strip(" :|-")

            else:
                level = "UNKNOWN"
                message = line

            log_entry = {
                "level": level,
                "message": message,
                "original": line
            }

            logs.append(log_entry)

    counts = Counter(log["level"] for log in logs)

    repeated_errors = Counter(
        log["message"]
        for log in logs
        if log["level"] in ("ERROR", "CRITICAL")
    )

    # Generate recommendations for error and warning messages.

    recommendations = []
    seen_recommendations = set()

    for log in logs:
        if log["level"] in ("ERROR", "CRITICAL", "WARNING"):
            recommendation = get_error_recommendation(log["message"])

            key = (
                recommendation["issue"],
                log["message"].lower()
            )

            if key not in seen_recommendations:
                seen_recommendations.add(key)

                recommendations.append({
                    "level": log["level"],
                    "message": log["message"],
                    "issue": recommendation["issue"],
                    "cause": recommendation["cause"],
                    "solution": recommendation["solution"]
                })

    return {
        "total": len(logs),
        "errors": counts["ERROR"] + counts["CRITICAL"],
        "warnings": counts["WARNING"],
        "info": counts["INFO"],
        "debug": counts["DEBUG"],
        "unknown": counts["UNKNOWN"],
        "logs": logs,
        "repeated_errors": [
            {"message": message, "count": count}
            for message, count in repeated_errors.most_common(5)
        ],
        "recommendations": recommendations
    }