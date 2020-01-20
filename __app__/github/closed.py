# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import gidgethub.routing

from . import labels


router = gidgethub.routing.Router()

ALL_STATUS_LABELS = {label.value for label in labels.Status}


@router.register("issues", action="closed")
async def remove_status_labels(event, gh, *args, **kwargs):
    """Remove all status-related labels."""
    labels = event.data["issue"]["labels"]
    labels_url = event.data["issue"]["labels_url"]
    for label in labels:
        label_name = label["name"]
        if label_name in ALL_STATUS_LABELS:
            await gh.delete(labels_url, {"name": label_name})
