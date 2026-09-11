import express from "express";

import {
    getReports,
    getReportById,
    getReportByInvestigation,
} from "../controllers/reportController.js";

import { Protect } from "../middleware/authMiddleware.js";

const router = express.Router();

router.get(
    "/",
    Protect,
    getReports
);

router.get(
    "/investigation/:investigationId",
    Protect,
    getReportByInvestigation
);

router.get(
    "/:reportId",
    Protect,
    getReportById
);

export default router;