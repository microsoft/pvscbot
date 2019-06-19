# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import gidgethub.routing


router = gidgethub.routing.Router()


@router.register("ping")
async def ping(*args, logger=None, **kwargs):
    """Respond to the 'ping' event by doing nothing."""
    if logger:
        logger.info("'ping' event received")
