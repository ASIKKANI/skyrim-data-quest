# backend/app/models/rule_engine.py

import re

class RuleEngine:
    def __init__(self):
        pass

    def evaluate(self, email_data):
        """
        Evaluate an email JSON with simple rules.
        Returns a phishing score between 0 and 1.
        """
        score = 0
        total_rules = 3  # update if you add more rules

        # Rule 1: suspicious keywords in subject or body
        suspicious_keywords = ["urgent", "verify", "password", "bank", "lottery", "click here"]
        subject = email_data.get("headers", {}).get("Subject", "").lower()
        body = email_data.get("body", "").lower()

        if any(keyword in subject or keyword in body for keyword in suspicious_keywords):
            score += 1

        # Rule 2: suspicious sender address
        from_email = email_data.get("from", "").lower()
        if not re.match(r".+@.+\..+", from_email):  # malformed email
            score += 1
        elif any(domain in from_email for domain in ["paypal", "amazon", "bank"]):
            score += 1

        # Rule 3: too many links in body
        links = re.findall(r"http[s]?://\S+", body)
        if len(links) > 3:
            score += 1

        return score / total_rules
