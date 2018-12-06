import gidgethub.routing

from . import labels

router = gidgethub.routing.Router()


@router.register("issues", action="opened")
@router.register("issues", action="reopened")
async def add_classify_label(event, gh, *args, **kwargs):
    """Add the 'classify' label.

    If any labels already exist then don't apply the label as that implies that
    the issue has already been triaged.

    """
    issue = event.data["issue"]
    if issue["labels"]:
        # Teammate pre-classified the issue when creating it.
        return
    await gh.post(issue["labels_url"], data={"labels": [labels.Status.classify.value]})
