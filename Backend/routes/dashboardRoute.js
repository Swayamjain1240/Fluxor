import express from "express";

import {
    getDashboardSummary,
    getRecentActivity,
} from "../controllers/dashboardController.js";

import { Protect } from "../middleware/authMiddleware.js";

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