import express from "express";

import {
    getDashboardSummary,
    getRecentActivity,
} from "../controllers/dashboard.controller.js";

import { Protect } from "../middleware/auth.middleware.js";

const router = express.Router();

router.get(
    "/summary",
    Protect,
    getDashboardSummary
);

router.get(
    "/recent",
    Protect,
    getRecentActivity
);

export default router;