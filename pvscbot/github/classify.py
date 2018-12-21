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


def has_labels(event):
    return event.data["issue"]["labels"]


# Removing 'classify' from closed issues is taken care of in the 'closed' submodule.
@router.register("issues", action="opened")
@router.register("issues", action="reopened")
async def classify_new_issue(event, gh, *args, **kwargs):
    """Add the 'classify' label.

    If any labels already exist then don't apply the label as that implies that
    the issue has already been triaged.

    """
    issue = event.data["issue"]
    if issue["labels"]:
        # Teammate pre-classified the issue when creating it.
        return
    await add_classify_label(gh, event)


@router.register("issues", action="labeled")
async def added_label(event, gh, *args, **kwargs):
    if not is_opened(event):
        return
    elif event.data["label"]["name"] == labels.Status.classify.value:
        return
    elif has_classify(event):
        await gh.delete(
            event.data["issue"]["labels_url"], {"name": labels.Status.classify.value}
        )


@router.register("issues", action="unlabeled")
async def no_labels(event, gh, *args, **kwargs):
    if not is_opened(event):
        return
    elif not has_labels(event):
        await add_classify_label(gh, event)
