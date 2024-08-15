import os


def get_endpoint(key):
    end_point_map = {
        "visits_per_day": "VisitsSummary.getVisits",
        "unique_visitors": "VisitsSummary.getUniqueVisitors",
    }
    return end_point_map[key]


def get_parameters(period, date, endpoint_key):
    return {
        "module": "API",
        "token_auth": os.environ.get("MATOMO_AUTH_TOKEN"),
        "idSite": os.environ.get("MATOMO_SITE_ID"),
        "date": str(date),
        "period": period,
        "format": "json",
        "module": "API",
        "method": get_endpoint(endpoint_key),
    }
