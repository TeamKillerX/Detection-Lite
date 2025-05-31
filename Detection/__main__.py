#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROPRIETARY SOFTWARE - STRICTLY CONFIDENTIAL
© 2025 Randy Dev. All Rights Reserved.

This source code is licensed under proprietary terms and may NOT be:
- Copied
- Modified
- Distributed
- Reverse-engineered
- Used as derivative work

Violators will be prosecuted under DMCA § 1201 and applicable copyright laws.

Authorized use only permitted with express written consent from TeamKillerX.
Contact: killerx@randydev.my.id
"""

import logging

from .utils import DetectionManager

if __name__ == "__main__":
    manager = DetectionManager()
    try:
        manager.loop.run_until_complete(manager.run())
    except KeyboardInterrupt:
        logging.info("🟠 Shutdown requested by user")
    except Exception as e:
        logging.critical(f"🔴 Startup failed: {e}", exc_info=True)
    finally:
        if manager.loop.is_running():
            manager.loop.run_until_complete(manager.loop.shutdown_asyncgens())
            manager.loop.close()
        logging.info("🔴 Detection Manager stopped")
