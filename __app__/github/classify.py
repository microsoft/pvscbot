# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import gidgethub.routing

from . import labels

router = gidgethub.routing.Router()


def is_opened(event):
    return event.data["issue"]["state"] == "open"


def has_classify(event):
    return any(
        label["name"] == labels.Status.classify.value
        for label in event.data["issue"]["labels"]
    )


async def add_classify_label(gh, event):
    await gh.post(
        event.data["issue"]["labels_url"],
        data={"labels": [labels.Status.classify.value]},
    )


def classify_unneeded(labels_to_check):
    """Determine if an existing label negates needing 'classify'."""
    status_labels = set(labels.STATUS_LABELS) | labels.CLASSIFICATION_LABELS
    status_labels.add(labels.Team.data_science.value)
    return any(label in status_labels for label in labels_to_check)


# Removing 'classify' from closed issues is taken care of in the 'closed' submodule.
@router.register("issues", action="opened")
@router.register("issues", action="reopened")
async def classify_new_issue(event, gh, *args, **kwargs):
    """Add the 'classify' label."""
    issue = event.data["issue"]
    existing_labels = {label["name"] for label in issue["labels"]}
    if classify_unneeded(existing_labels):
        # Teammate pre-classified the issue when creating it.
        return
    async for label in gh.getiter(issue["labels_url"]):
        if classify_unneeded({label["name"]}):
            # Issue already has a status label.
            return
    else:
        await add_classify_label(gh, event)


@router.register("issues", action="labeled")
async def added_label(event, gh, *args, **kwargs):
    """Remove 'classify' if it is no longer required."""
    added_label = event.data["label"]["name"]
    if not is_opened(event):
        return
    elif added_label == labels.Status.classify.value:
        return
    elif has_classify(event):
        if classify_unneeded({added_label}):
            try:
                await gh.delete(
                    event.data["issue"]["labels_url"],
                    {"name": labels.Status.classify.value},
                )
            except gidgethub.BadRequest as exc:
                if not "Label does not exist" in str(exc):
                    raise


@router.register("issues", action="unlabeled")
async def removed_label(event, gh, *args, **kwargs):
    remaining_labels = {label["name"] for label in event.data["issue"]["labels"]}
    if not is_opened(event) or classify_unneeded(remaining_labels):
        return
    else:
        await add_classify_label(gh, event)
