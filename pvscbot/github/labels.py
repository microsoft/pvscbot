import enum


class Status(enum.Enum):
    classify = "classify"
    triage = "triage"
    needs_decision = "needs decision"
    needs_more_info = "info needed"
    needs_PR = "needs PR"
    needs_spec = "needs spec"
    needs_upstream_fix = "needs upstream fix"
    validate_fix = "validate fix"
